## CMake configuration - set up project #####################################
cmake_minimum_required( VERSION 2.8 )
project( ppQuanTrade )

# Checking operating system
if ( UNIX )
    message( STATUS "Unix system" )
endif ( UNIX )

# Default is debug output
# Unable it with -D CMAKE_BUILD_TYPE=Release
if ( CMAKE_BUILD_TYPE STREQUAL "Debug" )
    set( CMAKE_BUILD_TYPE Debug )
    #add_definitions(-g -Wall -W -DDEBUG)
endif ()

# Some version infos for config file
set(project_VERSION_MAJOR 0)
set(project_VERSION_MINOR 5)
set(project_PATCH_VERSION 0)
set(project_VERSION 
    ${project_VERSION_MAJOR}.${project_VERSION_MINOR}.${project_PATCH_VERSION})
set(BUILD_DIR build CACHE PATH "Installation directory for Cmake files")

#############################################################################
##  Set up project architecture  ############################################

set( SOURCES trade.cpp )   # No class files
message( STATUS "sources: ${SOURCES}" )
add_executable( QuanTrade ${SOURCES} )

#############################################################################
##  Set up external libs  ###################################################

# SQLite3 lib
find_library(SQLite3_LIB sqlite3 )
find_path( SQLite3_INCLUDES sqlite3.h PATHS /usr/include )

# Boost lib
#set(BOOST_INCLUDE_DIR /home/xavier/lib/boost_1_49_0)
#include_directories(${BOOST_INCLUDE_DIR})

#############################################################################

ADD_CUSTOM_COMMAND(TARGET QuanTrade
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy QuanTrade ../)
