from conans import ConanFile, CMake
import os

username = os.getenv( '"CONAN_USERNAME', 'shinichy' )
channel = os.getenv( 'CONAN_CHANNEL', 'testing' )

class TestConan( ConanFile ):
  settings = 'os', 'compiler', 'build_type', 'arch'
  requires = 'breakpad/1.0.0@%s/%s' %  (username, channel )
  generators = 'cmake'

  def build( self ):
    cmake = CMake( self )
    cmake.configure()
    cmake.build()

  def imports( self ):
    self.copy( '*.dll', 'bin', 'bin' )
    self.copy( '*.dylib', 'bin', 'bin' )

  def test( self ):
    os.chdir( 'bin' )
    self.run( '.%sexample' % os.sep )
