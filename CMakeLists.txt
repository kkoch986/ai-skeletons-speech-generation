cmake_minimum_required(VERSION 3.8)
project(ai_skeletons_speech_generation)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add source files
set(SOURCES
    src/cactus_whistle_interface.cpp
)

# Add header files
set(HEADERS
    src/cactus_whistle_interface.h
)

# Create library
add_library(${PROJECT_NAME} STATIC ${SOURCES} ${HEADERS})

# Include directories
target_include_directories(${PROJECT_NAME} PUBLIC src)

# Link libraries (if any)
# target_link_libraries(${PROJECT_NAME} )

# Add demo executable
add_executable(demo src/demo.cpp)
target_link_libraries(demo ${PROJECT_NAME})

# Add test executable
add_executable(test src/test.cpp)
target_link_libraries(test ${PROJECT_NAME})