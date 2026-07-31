# Le moteur de contribution mobile : llama.cpp compilé pour arm64, lié en
# statique dans une seule bibliothèque lenyay_llm.so.
#
# Le chemin des sources llama.cpp vient de local.properties (llama.dir),
# transmis par Gradle en -DLLAMA_CPP_DIR — le dépôt n'embarque pas 300 Mo
# de sources tierces, il les épingle (commit noté dans ANDROID.md).

cmake_minimum_required(VERSION 3.22)
project(lenyay_llm LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT DEFINED LLAMA_CPP_DIR)
    message(FATAL_ERROR "LLAMA_CPP_DIR manquant (llama.dir dans local.properties)")
endif()

# Une seule cible, hermétique : pas de réseau au configure, pas d'OpenMP
# (les threads de ggml suffisent), pas d'outils annexes.
set(BUILD_SHARED_LIBS OFF)
set(LLAMA_BUILD_COMMON ON)   # sinon la cible llama-common n'existe pas
set(LLAMA_BUILD_TESTS OFF)
set(LLAMA_BUILD_EXAMPLES OFF)
set(LLAMA_BUILD_TOOLS OFF)
set(LLAMA_BUILD_SERVER OFF)
set(LLAMA_CURL OFF)
set(GGML_OPENMP OFF)
set(GGML_CPU_KLEIDIAI OFF)

add_subdirectory(${LLAMA_CPP_DIR} build-llama)

add_library(lenyay_llm SHARED lenyay_llm.cpp)

target_include_directories(lenyay_llm PRIVATE
        ${LLAMA_CPP_DIR}
        ${LLAMA_CPP_DIR}/common
        ${LLAMA_CPP_DIR}/include
        ${LLAMA_CPP_DIR}/ggml/include
        ${LLAMA_CPP_DIR}/vendor)   # nlohmann/json embarqué, tiré par chat.h

target_link_libraries(lenyay_llm llama llama-common android log)
