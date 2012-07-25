## CMake configuration - set up project #####################################
cmake_minimum_required( VERSION 2.8 )
project( ppQuanTrade )

# Default is debug output
# Unable it with -D CMAKE_BUILD_TYPE=Release
if ( CMAKE_BUILD_TYPE STREQUAL "Debug" )
    set( CMAKE_BUILD_TYPE Debug )
    add_definitions(-g -Wall -W -DDEBUG)
endif ()

set(BUILD_DIR build CACHE PATH "Installation directory for Cmake files")

#############################################################################
##  Set up project architecture  ############################################

set( SOURCES basic.cpp )   # No class files
message( STATUS "sources: ${SOURCES}" )
add_executable( basic ${SOURCES} )

#############################################################################
##  Set up external libs  ###################################################

# SQLite3 lib
find_library(SQLite3_LIB sqlite3 )
find_path( SQLite3_INCLUDES sqlite3.h PATHS /usr/include )

# Boost lib
set(BOOST_INCLUDE_DIR /home/xavier/lib/boost_1_49_0)
include_directories(${BOOST_INCLUDE_DIR})

#############################################################################

ADD_CUSTOM_COMMAND(TARGET basic
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy basic ../)
