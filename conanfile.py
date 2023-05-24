from conans import ConanFile, AutoToolsBuildEnvironment
from conans import tools
from conan.tools.microsoft import MSBuild, VCVars
import os, shutil

class BreakpadConan( ConanFile ):
  name = 'breakpad'
  branch = 'chrome_90'
  version = '0.1.' + branch
  license = 'https://chromium.googlesource.com/breakpad/breakpad/+/master/LICENSE'
  url = 'https://github.com/shinichy/conan-breakpad'
  settings = 'os', 'compiler', 'build_type', 'arch'
  generators = 'cmake'
  exports = ["FindBREAKPAD.cmake", "patch/*"]
  short_paths = True

  def generate( self ):
    if self.settings.os == 'Windows':
      ms = VCVars(self)
      ms.generate()

  def source( self ):
    breakpad_git = tools.Git(folder='breakpad')
    breakpad_git.clone('https://chromium.googlesource.com/breakpad/breakpad', branch=self.branch, shallow=True)
    if self.settings.os == 'Linux':
      lss_git = tools.Git(folder='breakpad/src/third_party/lss')
      lss_git.clone('https://chromium.googlesource.com/linux-syscall-support')
    if self.settings.os == 'Windows':
      gyp_git = tools.Git(folder='breakpad/src/tools/gyp')
      gyp_git.clone('https://github.com/umogSlayer/gyp-clone.git')

  def _macosx_build_commandline(self, project, target, build_type, build_settings):
    build_settings_string = ' '.join(key + '="' + value + '"' for key, value in build_settings.items())
    return 'xcodebuild -project {project} -sdk macosx -target {target} -configuration {build_type} {build_settings}' \
      .format(project=project,
              target=target,
              build_type=build_type,
              build_settings=build_settings_string)

  def build( self ):
    if self.settings.os == 'Macos':
      tools.patch(base_path='breakpad', patch_file='patch/Breakpad.xcodeproj.patch')
      arch = 'i386' if self.settings.arch == 'x86' \
             else 'arm64' if self.settings.arch == 'armv8' \
             else 'arm64e' if self.settings.arch == 'armv8.3' \
             else self.settings.arch
      build_settings = {
        'ARCHS': str(arch),
        'ONLY_ACTIVE_ARCH': 'YES',
        'MACOSX_DEPLOYMENT_TARGET': str(self.settings.os.get_safe('version', '10.15')),
      }
      command_line = self._macosx_build_commandline('breakpad/src/client/mac/Breakpad.xcodeproj',
                                                    'Breakpad',
                                                    self.settings.build_type,
                                                    build_settings)
      self.run(command_line)
    elif self.settings.os == 'Windows':
      tools.patch(base_path='breakpad', patch_file='patch/common.gypi.patch')
      os.environ['GYP_MSVS_VERSION'] = '2019'
      self.run('python breakpad/src/tools/gyp/gyp_main.py --no-circular-check -D win_release_RuntimeLibrary=2 -D win_debug_RuntimeLibrary=3 breakpad/src/client/windows/breakpad_client.gyp')
      msbuild = MSBuild(self)
      msbuild.build('breakpad/src/client/windows/common.vcxproj')
      msbuild.build('breakpad/src/client/windows/handler/exception_handler.vcxproj')
      msbuild.build('breakpad/src/client/windows/crash_generation/crash_generation_client.vcxproj')
      msbuild.build('breakpad/src/client/windows/crash_generation/crash_generation_server.vcxproj')
      msbuild.build('breakpad/src/client/windows/sender/crash_report_sender.vcxproj')
    elif self.settings.os == 'Linux':
      tools.patch(base_path='breakpad', patch_file='patch/std-max.patch', strip=1)
      env_build = AutoToolsBuildEnvironment(self)
      env_build.configure('breakpad/')
      env_build.make()

  def package( self ):
    self.copy("FindBREAKPAD.cmake", ".", ".")
    if self.settings.os != 'Linux':
      self.copy( '*.h', dst='include/common', src='breakpad/src/common' )

    if self.settings.os == 'Macos':
      self.copy( '*.h', dst='include/breakpad/client/mac', src='breakpad/src/client/mac' )
      # self.copy doesn't preserve symbolic links
      shutil.copytree('breakpad/src/client/mac/build/%s/Breakpad.framework' % self.settings.build_type, os.path.join(self.package_folder, 'lib', 'Breakpad.framework'), symlinks=True)
    elif self.settings.os == 'Windows':
      self.copy( '*.h', dst='include/client/windows', src='breakpad/src/client/windows' )
      self.copy( '*.h', dst='include/google_breakpad', src='breakpad/src/google_breakpad' )
      self.copy( '*.lib', dst='lib', src='breakpad/src/client/windows/%s' % self.settings.build_type, keep_path=False )
      self.copy( '*.lib', dst='lib', src='breakpad/src/client/windows/handler/%s' % self.settings.build_type, keep_path=False )
      self.copy( '*.lib', dst='lib', src='breakpad/src/client/windows/crash_generation/%s' % self.settings.build_type, keep_path=False )
      self.copy( '*.lib', dst='lib', src='breakpad/src/client/windows/sender/%s' % self.settings.build_type, keep_path=False )
      self.copy( '*.exe', dst='bin', src='breakpad/src/tools/windows/binaries' )
    elif self.settings.os == 'Linux':
      env_build = AutoToolsBuildEnvironment(self)
      env_build.install()

  def package_info( self ):
    if self.settings.os == 'Windows':
      self.cpp_info.libs = ['breakpad']
    if self.settings.os == 'Linux' or self.settings.os == 'Macos':
      self.cpp_info.includedirs.append('include/breakpad')
    self.env_info.path.append(os.path.join(self.package_folder, "bin"))
