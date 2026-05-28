cmake_minimum_required(VERSION 3.5)
project(urg_node2)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

set(URG_LIBRARY_DIR urg_library/current)
set(URG_LIBRARY_C_INCLUDE_DIR ${URG_LIBRARY_DIR}/include/c)
set(URG_LIBRARY_SRC_DIR ${URG_LIBRARY_DIR}/src)

include_directories(include ${URG_LIBRARY_C_INCLUDE_DIR})

add_library(urg_c SHARED
  ${URG_LIBRARY_SRC_DIR}/urg_sensor.c
  ${URG_LIBRARY_SRC_DIR}/urg_utils.c
  ${URG_LIBRARY_SRC_DIR}/urg_debug.c
  ${URG_LIBRARY_SRC_DIR}/urg_connection.c
  ${URG_LIBRARY_SRC_DIR}/urg_ring_buffer.c
  ${URG_LIBRARY_SRC_DIR}/urg_serial.c
  ${URG_LIBRARY_SRC_DIR}/urg_serial_utils.c
  ${URG_LIBRARY_SRC_DIR}/urg_tcpclient.c
)

add_executable(urg_node2_node src/urg_node2.cpp)
ament_target_dependencies(urg_node2_node rclcpp sensor_msgs)
target_link_libraries(urg_node2_node urg_c)

install(TARGETS
  urg_node2_node urg_c
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
