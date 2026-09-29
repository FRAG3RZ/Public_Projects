# Install script for directory: C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/external/FTXUI

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/install/GCC 15.2.0 x86_64-w64-mingw32")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Debug")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "C:/mingw64/bin/objdump.exe")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/build/GCC 15.2.0 x86_64-w64-mingw32/external/FTXUI/libftxui-screen.a")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/build/GCC 15.2.0 x86_64-w64-mingw32/external/FTXUI/libftxui-dom.a")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/build/GCC 15.2.0 x86_64-w64-mingw32/external/FTXUI/libftxui-component.a")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE DIRECTORY FILES "C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/external/FTXUI/include/ftxui")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/ftxui/ftxui-targets.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/ftxui/ftxui-targets.cmake"
         "C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/build/GCC 15.2.0 x86_64-w64-mingw32/external/FTXUI/CMakeFiles/Export/418a5211b54bdfa9fa029e8a3112c4d3/ftxui-targets.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/ftxui/ftxui-targets-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/ftxui/ftxui-targets.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/ftxui" TYPE FILE FILES "C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/build/GCC 15.2.0 x86_64-w64-mingw32/external/FTXUI/CMakeFiles/Export/418a5211b54bdfa9fa029e8a3112c4d3/ftxui-targets.cmake")
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/ftxui" TYPE FILE FILES "C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/build/GCC 15.2.0 x86_64-w64-mingw32/external/FTXUI/CMakeFiles/Export/418a5211b54bdfa9fa029e8a3112c4d3/ftxui-targets-debug.cmake")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/ftxui" TYPE FILE FILES
    "C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/build/GCC 15.2.0 x86_64-w64-mingw32/external/FTXUI/cmake/ftxui-config.cmake"
    "C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/build/GCC 15.2.0 x86_64-w64-mingw32/external/FTXUI/cmake/ftxui-config-version.cmake"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES "C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/build/GCC 15.2.0 x86_64-w64-mingw32/external/FTXUI/ftxui.pc")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/build/GCC 15.2.0 x86_64-w64-mingw32/external/FTXUI/examples/cmake_install.cmake")
  include("C:/Users/m4z3o/Desktop/University/Uni_Courses/Third_Year/Advanced_Programming_3/Assignment_2/out/build/GCC 15.2.0 x86_64-w64-mingw32/external/FTXUI/doc/cmake_install.cmake")

endif()

