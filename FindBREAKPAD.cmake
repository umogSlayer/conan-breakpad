#=============================================================================
# Copyright 2001-2011 Kitware, Inc.
#
# Distributed under the OSI-approved BSD License (the "License");
# see accompanying file Copyright.txt for details.
#
# This software is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the License for more information.
#=============================================================================
# (To distribute this file outside of CMake, substitute the full
#  License text for the above reference.)

find_library(BREAKPAD_COMMON NAMES breakpad PATHS ${CONAN_LIB_DIRS_BREAKPAD})
find_library(BREAKPAD_CLIENT NAMES breakpad_client PATHS ${CONAN_LIB_DIRS_BREAKPAD})

MESSAGE("** BREAKPAD ALREADY FOUND BY CONAN!")
SET(BREAKPAD_FOUND TRUE)
MESSAGE("** FOUND BREAKPAD LIBRARIES:  ${BREAKPAD_COMMON} ${BREAKPAD_CLIENT}")

set(BREAKPAD_INCLUDE_DIRS ${CONAN_INCLUDE_DIRS_BREAKPAD} ${CONAN_INCLUDE_DIRS_BREAKPAD}/breakpad)
set(BREAKPAD_LIBRARIES ${BREAKPAD_COMMON} ${BREAKPAD_CLIENT})

mark_as_advanced(BREAKPAD_COMMON BREAKPAD_CLIENT)

add_library(google::breakpad INTERFACE IMPORTED)
set_property(TARGET google::breakpad PROPERTY INTERFACE_INCLUDE_DIRECTORIES ${BREAKPAD_INCLUDE_DIRS})
set_property(TARGET google::breakpad PROPERTY INTERFACE_LINK_LIBRARIES ${BREAKPAD_LIBRARIES})
