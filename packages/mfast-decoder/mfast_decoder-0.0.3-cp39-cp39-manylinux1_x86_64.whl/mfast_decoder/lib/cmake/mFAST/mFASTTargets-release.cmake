#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mfast_static" for configuration "Release"
set_property(TARGET mfast_static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mfast_static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmfast.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS mfast_static )
list(APPEND _IMPORT_CHECK_FILES_FOR_mfast_static "${_IMPORT_PREFIX}/lib/libmfast.a" )

# Import target "mfast_coder_static" for configuration "Release"
set_property(TARGET mfast_coder_static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mfast_coder_static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LINK_INTERFACE_LIBRARIES_RELEASE "mfast_static"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmfast_coder.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS mfast_coder_static )
list(APPEND _IMPORT_CHECK_FILES_FOR_mfast_coder_static "${_IMPORT_PREFIX}/lib/libmfast_coder.a" )

# Import target "mfast_xml_parser_static" for configuration "Release"
set_property(TARGET mfast_xml_parser_static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mfast_xml_parser_static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LINK_INTERFACE_LIBRARIES_RELEASE "mfast_static"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmfast_xml_parser.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS mfast_xml_parser_static )
list(APPEND _IMPORT_CHECK_FILES_FOR_mfast_xml_parser_static "${_IMPORT_PREFIX}/lib/libmfast_xml_parser.a" )

# Import target "mfast_json_static" for configuration "Release"
set_property(TARGET mfast_json_static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mfast_json_static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LINK_INTERFACE_LIBRARIES_RELEASE "mfast_static"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmfast_json.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS mfast_json_static )
list(APPEND _IMPORT_CHECK_FILES_FOR_mfast_json_static "${_IMPORT_PREFIX}/lib/libmfast_json.a" )

# Import target "fast_type_gen" for configuration "Release"
set_property(TARGET fast_type_gen APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(fast_type_gen PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/bin/fast_type_gen-1.3.0"
  )

list(APPEND _IMPORT_CHECK_TARGETS fast_type_gen )
list(APPEND _IMPORT_CHECK_FILES_FOR_fast_type_gen "${_IMPORT_PREFIX}/bin/fast_type_gen-1.3.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
