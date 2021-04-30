from conans import ConanFile, AutoToolsBuildEnvironment, MSBuild
from conans import tools
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

  def source( self ):
    breakpad_git = tools.Git(folder='breakpad')
    breakpad_git.clone('https://chromium.googlesource.com/breakpad/breakpad', branch=self.branch, shallow=True)
    if self.settings.os == 'Linux':
      lss_git = tools.Git(folder='breakpad/src/third_party/lss')
      lss_git.clone('https://chromium.googlesource.com/linux-syscall-support')
    if self.settings.os == 'Windows':
      gyp_git = tools.Git(folder='breakpad/src/tools/gyp')
      gyp_git.clone('https://github.com/umogSlayer/gyp-clone.git')

  def build( self ):
    if self.settings.os == 'Macos':
      arch = 'i386' if self.settings.arch == 'x86' else self.settings.arch
      self.run( 'xcodebuild -project breakpad/src/client/mac/Breakpad.xcodeproj -sdk macosx -target Breakpad ARCHS=%s ONLY_ACTIVE_ARCH=YES -configuration %s' % (arch, self.settings.build_type) )
    elif self.settings.os == 'Windows':
      tools.patch(base_path='breakpad', patch_file='patch/common.gypi.patch')
      os.environ['GYP_MSVS_VERSION'] = '2019'
      self.run('python breakpad/src/tools/gyp/gyp_main.py --no-circular-check -D win_release_RuntimeLibrary=2 -D win_debug_RuntimeLibrary=3 breakpad/src/client/windows/breakpad_client.gyp')
      msbuild = MSBuild(self)
      msbuild.build('breakpad/src/client/windows/common.vcxproj', upgrade_project=False)
      msbuild.build('breakpad/src/client/windows/handler/exception_handler.vcxproj', upgrade_project=False)
      msbuild.build('breakpad/src/client/windows/crash_generation/crash_generation_client.vcxproj', upgrade_project=False)
      msbuild.build('breakpad/src/client/windows/crash_generation/crash_generation_server.vcxproj', upgrade_project=False)
      msbuild.build('breakpad/src/client/windows/sender/crash_report_sender.vcxproj', upgrade_project=False)
    elif self.settings.os == 'Linux':
      env_build = AutoToolsBuildEnvironment(self)
      env_build.configure('breakpad/')
      env_build.make()

  def package( self ):
    self.copy("FindBREAKPAD.cmake", ".", ".")
    if self.settings.os != 'Linux':
      self.copy( '*.h', dst='include/common', src='breakpad/src/common' )

    if self.settings.os == 'Macos':
      self.copy( '*.h', dst='include/client/mac', src='breakpad/src/client/mac' )
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
    if self.settings.os == 'Linux':
      self.cpp_info.includedirs.append('include/breakpad')
    self.env_info.path.append(os.path.join(self.package_folder, "bin"))
