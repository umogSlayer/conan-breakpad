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
if (CMAKE_HOST_SYSTEM_NAME STREQUAL "Linux")
    find_library(BREAKPAD_COMMON NAMES breakpad PATHS ${CONAN_LIB_DIRS_BREAKPAD})
    find_library(BREAKPAD_CLIENT NAMES breakpad_client PATHS ${CONAN_LIB_DIRS_BREAKPAD})
else ()
    find_library(BREAKPAD_COMMON NAMES common PATHS ${CONAN_LIB_DIRS_BREAKPAD})
    find_library(BREAKPAD_EXCEPTION_HANDLER NAMES exception_handler PATHS ${CONAN_LIB_DIRS_BREAKPAD})
    find_library(BREAKPAD_CRASH_GENERATION_CLIENT NAMES crash_generation_client PATHS ${CONAN_LIB_DIRS_BREAKPAD})
    find_library(BREAKPAD_CRASH_GENERATION_SERVER NAMES crash_generation_server PATHS ${CONAN_LIB_DIRS_BREAKPAD})
    find_library(BREAKPAD_CRASH_REPORT_SENDER NAMES crash_report_sender PATHS ${CONAN_LIB_DIRS_BREAKPAD})
endif()

MESSAGE("** BREAKPAD ALREADY FOUND BY CONAN!")
SET(BREAKPAD_FOUND TRUE)
MESSAGE("** FOUND BREAKPAD LIBRARIES:"
    " ${BREAKPAD_COMMON}"
    " ${BREAKPAD_EXCEPTION_HANDLER}"
    " ${BREAKPAD_CRASH_GENERATION_CLIENT}"
    " ${BREAKPAD_CRASH_GENERATION_SERVER}"
    " ${BREAKPAD_CRASH_REPORT_SENDER}"
    " ${BREAKPAD_CLIENT}")

set(BREAKPAD_INCLUDE_DIRS ${CONAN_INCLUDE_DIRS_BREAKPAD} ${CONAN_INCLUDE_DIRS_BREAKPAD}/breakpad)
if (CMAKE_HOST_SYSTEM_NAME STREQUAL "Linux")
    set(BREAKPAD_LIBRARIES ${BREAKPAD_COMMON} ${BREAKPAD_CLIENT})
    mark_as_advanced(BREAKPAD_COMMON BREAKPAD_CLIENT)
else ()
    set(BREAKPAD_LIBRARIES ${BREAKPAD_COMMON} ${BREAKPAD_EXCEPTION_HANDLER} ${BREAKPAD_CRASH_GENERATION_CLIENT})
    mark_as_advanced(BREAKPAD_COMMON BREAKPAD_EXCEPTION_HANDLER BREAKPAD_CRASH_GENERATION_CLIENT)
endif ()

add_library(google::breakpad INTERFACE IMPORTED)
set_property(TARGET google::breakpad PROPERTY INTERFACE_INCLUDE_DIRECTORIES ${BREAKPAD_INCLUDE_DIRS})
set_property(TARGET google::breakpad PROPERTY INTERFACE_LINK_LIBRARIES ${BREAKPAD_LIBRARIES})
