cmake_minimum_required(VERSION 3.10.2)
project(loader)

SET(CMAKE_BUILD_TYPE Release CACHE STRING
	"Choose the type of build, options are: None Debug Release RelWithDebInfo MinSizeRel.")

set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR})

add_compile_options(-fPIC)
add_compile_options(-std=gnu++17)
add_compile_options(-Wdeprecated-declarations)

add_compile_options(-DHAVE_CSTDDEF)

add_definitions(-DROOT_DIR="${CMAKE_HOME_DIRECTORY}")
set(CMAKE_MODULE_PATH "${CMAKE_HOME_DIRECTORY}/cmake")


# set(PYBIND11_PYTHON_VERSION 3.10 CACHE STRING "")

find_package (Eigen3 3.3 REQUIRED)
find_package(LibXml2 REQUIRED)
# find_package(PythonLibs REQUIRED)
find_package(pybind11 REQUIRED)

include_directories(${FBX_INCLUDE_DIRS})
include_directories(${LIBXML2_INCLUDE_DIR})

file(GLOB srcs "*.h" "*.cpp")

add_library(loader ${srcs})
target_link_libraries(loader Eigen3::Eigen ${FBX_LIBRARIES} ${LIBXML2_LIBRARIES} pybind11::module pybind11::embed)

project(pycomcon)

add_library(pycomcon SHARED ${srcs})
target_link_libraries(pycomcon Eigen3::Eigen ${FBX_LIBRARIES} ${LIBXML2_LIBRARIES} pybind11::module pybind11::embed)
set_target_properties(pycomcon PROPERTIES PREFIX "" )