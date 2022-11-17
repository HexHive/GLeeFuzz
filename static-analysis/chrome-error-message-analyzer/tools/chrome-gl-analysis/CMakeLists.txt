# add_executable(chrome-gl-analysis chrome-gl-analysis.cpp)
# target_link_libraries(chrome-gl-analysis ${llvm_libs})
# set_target_properties(chrome-gl-analysis PROPERTIES
#    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

set(COMMON_SRCS svf_utils.cpp util.cpp llvm_utils.cpp)

set(COMMON_LIBS ${llvm_libs} Svf nlohmann_json::nlohmann_json)

function(ADD_GL_TOOL SFILE)
    get_filename_component(ENAME ${SFILE} NAME_WE)

    add_executable(${ENAME} ${SFILE} ${COMMON_SRCS})
    target_link_libraries(${ENAME} ${COMMON_LIBS})
    set_target_properties(${ENAME} PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

endfunction()

ADD_GL_TOOL(api_func_parse.cpp)
ADD_GL_TOOL(err_msg_analysis.cpp)
