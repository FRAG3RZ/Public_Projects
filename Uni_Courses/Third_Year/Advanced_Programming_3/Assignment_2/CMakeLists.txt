cmake_minimum_required(VERSION 3.20)

project(Assignment2 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_subdirectory(external/matplotplusplus)
add_subdirectory(external/ftxui)

#find_package(Matplot++ REQUIRED)

add_executable(demoplot
    All_Assignment_2_code/Project_Code/src/demo_with_graphs.cpp
)

target_include_directories(demoplot PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/All_Assignment_2_code/Project_Code/include
    ${CMAKE_CURRENT_SOURCE_DIR}/All_Assignment_2_code/Project_Code/src
)

target_link_libraries(demoplot PRIVATE matplot)

set_target_properties(demoplot PROPERTIES
    OUTPUT_NAME "demoplot_wsl.out"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/All_Assignment_2_code/Project_Code/src/executables"
)
