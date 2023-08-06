# Config file for the mFAST package
# It defines the following variables
# MFAST_INCLUDE_DIR         - include directories for mFAST
# MFAST_LIBRARY_DIRS        - library directories for mFAST
# MFAST_LIBRARIES           - libraries to link against
# MFAST_COMPONENTS          - installed components
# MFAST_<component>_LIBRARY - particular component library
# MFAST_EXECUTABLE          - the fast_type_gen executable

# Compute paths
get_filename_component(MFAST_CMAKE_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)
include("${MFAST_CMAKE_DIR}/mFASTTargets.cmake")

find_package( Boost 1.55.0 )
set(MFAST_INCLUDE_DIR "${Boost_INCLUDE_DIR}")
foreach (directory ${MFAST_CMAKE_DIR}/../../../include)
  get_filename_component(directory "${directory}" ABSOLUTE)
  list(APPEND MFAST_INCLUDE_DIR "${directory}")
endforeach (directory)
set(MFAST_LIBRARY_DIRS "")

list(REMOVE_DUPLICATES MFAST_INCLUDE_DIR)

set(MFAST_EXECUTABLE bin/fast_type_gen)
# These are IMPORTED targets created by mFASTTargets.cmake
set(MFAST_FOUND "TRUE")


# Make dependent targets automatically pick up include directory and definitions for CMake 2.8.12 and later
set_property(TARGET  mfast_static;mfast_coder_static;mfast_xml_parser_static;mfast_json_static
             APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES ${MFAST_INCLUDE_DIR})


if (NOT DEFINED MFAST_USE_STATIC_LIBS OR MFAST_USE_STATIC_LIBS)
  set(STATIC_SUFFIX "_static")
  set(components coder_static;xml_parser_static;json_static)
else ()
  set(components )
endif ()

foreach (entry IN LISTS mFAST_FIND_COMPONENTS)
  foreach (component IN LISTS components)
    if ("${entry}${STATIC_SUFFIX}" STREQUAL "${component}")
      set("MFAST_${entry}_FOUND" Yes)
    endif ()
  endforeach (component)

  if (MFAST_${entry}_FOUND)
    list(REMOVE_ITEM mFAST_FIND_COMPONENTS "${entry}")
    list(APPEND MFAST_LIBRARIES "mfast_${entry}${STATIC_SUFFIX}")

    set(MFAST_USED_COMPONENTS "${MFAST_USED_COMPONENTS} ${entry}")
    set("MFAST_${entry}_LIBRARY" "mfast_${entry}${STATIC_SUFFIX}")
  else ()
    message(SEND_ERROR "mFAST component ${entry} NOT FOUND! Available components: ${components}")
  endif ()
endforeach (entry)

list(APPEND MFAST_LIBRARIES "mfast${STATIC_SUFFIX}")

message(STATUS "mFAST Found! Used components:${MFAST_USED_COMPONENTS}")
message(STATUS "Used libraries: ${MFAST_LIBRARIES}")

include("${MFAST_CMAKE_DIR}/FastTypeGenTarget.cmake")
include("${MFAST_CMAKE_DIR}/SetCXXStandard.cmake")
