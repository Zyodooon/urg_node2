#include "urg_node2/urg_node2.hpp"

#include <algorithm>
#include <chrono>
#include <csignal>
#include <limits>
#include <memory>

#include "urg_utils.h"

using namespace std::chrono_literals;

namespace
{
constexpr int kMaxDataSize = 5000;
constexpr double kPi = 3.14159265358979323846;
}

UrgScanNode::UrgScanNode()
: Node("urg_node2")
{
  std::signal(SIGPIPE, SIG_IGN);

  serial_port_ = declare_parameter<std::string>("serial_port", "/dev/lidar");
  serial_baud_ = declare_parameter<int>("serial_baud", 115200);
  frame_id_ = declare_parameter<std::string>("frame_id", "laser");
  frame_id_.erase(0, frame_id_.find_first_not_of('/'));

  scan_pub_ = create_publisher<sensor_msgs::msg::LaserScan>("/scan", rclcpp::QoS(20));
  scan_thread_ = std::thread(&UrgScanNode::scan_loop, this);
}

UrgScanNode::~UrgScanNode()
{
  stop_thread_ = true;
  if (scan_thread_.joinable()) {
    scan_thread_.join();
  }
  disconnect_lidar();
}

bool UrgScanNode::connect_lidar()
{
  if (urg_open(&urg_, URG_SERIAL, serial_port_.c_str(), serial_baud_) < 0) {
    RCLCPP_ERROR(
      get_logger(), "Could not open Hokuyo LiDAR %s:%d: %s",
      serial_port_.c_str(), serial_baud_, urg_error(&urg_));
    return false;
  }

  connected_ = true;
  scan_period_ = 1.0e-6 * static_cast<double>(urg_scan_usec(&urg_));

  int data_size = std::min(urg_max_data_size(&urg_), kMaxDataSize);
  distance_.resize(static_cast<size_t>(data_size));

  int first_step = urg_rad2step(&urg_, -kPi);
  int last_step = urg_rad2step(&urg_, kPi);
  if (last_step < first_step) {
    std::swap(first_step, last_step);
  }
  urg_set_scanning_parameter(&urg_, first_step, last_step, 1);

  angle_min_ = urg_step2rad(&urg_, first_step);
  angle_max_ = urg_step2rad(&urg_, last_step);
  angle_increment_ = urg_step2rad(&urg_, 1);

  int min_step = 0;
  int max_step = 0;
  urg_step_min_max(&urg_, &min_step, &max_step);
  time_increment_ =
    ((urg_step2rad(&urg_, max_step) - urg_step2rad(&urg_, min_step)) / (2.0 * kPi)) *
    scan_period_ / static_cast<double>(max_step - min_step);

  long min_distance = 0;
  long max_distance = 0;
  urg_distance_min_max(&urg_, &min_distance, &max_distance);
  range_min_ = static_cast<double>(min_distance) / 1000.0;
  range_max_ = static_cast<double>(max_distance) / 1000.0;

  return true;
}

void UrgScanNode::disconnect_lidar()
{
  if (connected_) {
    urg_close(&urg_);
    connected_ = false;
  }
}

void UrgScanNode::scan_loop()
{
  while (!stop_thread_) {
    if (!connected_ && !connect_lidar()) {
      rclcpp::sleep_for(500ms);
      continue;
    }

    if (urg_start_measurement(&urg_, URG_DISTANCE, 0, 0, 0) < 0) {
      disconnect_lidar();
      rclcpp::sleep_for(500ms);
      continue;
    }

    int error_count = 0;
    while (!stop_thread_) {
      sensor_msgs::msg::LaserScan msg;
      if (make_scan_message(msg)) {
        scan_pub_->publish(msg);
        error_count = 0;
        continue;
      }

      error_count++;
      if (error_count > 4) {
        break;
      }
    }

    urg_stop_measurement(&urg_);
    disconnect_lidar();
    rclcpp::sleep_for(500ms);
  }
}

bool UrgScanNode::make_scan_message(sensor_msgs::msg::LaserScan & msg)
{
  int beams = urg_get_distance(&urg_, distance_.data(), nullptr);
  if (beams <= 0) {
    return false;
  }

  msg.header.stamp = now();
  msg.header.frame_id = frame_id_;
  msg.angle_min = angle_min_;
  msg.angle_max = angle_max_;
  msg.angle_increment = angle_increment_;
  msg.time_increment = time_increment_;
  msg.scan_time = scan_period_;
  msg.range_min = range_min_;
  msg.range_max = range_max_;
  msg.ranges.resize(static_cast<size_t>(beams));

  for (int i = 0; i < beams; ++i) {
    const long distance = distance_[static_cast<size_t>(i)];
    msg.ranges[static_cast<size_t>(i)] =
      distance == 0 ? std::numeric_limits<float>::quiet_NaN() :
      static_cast<float>(distance) / 1000.0f;
  }

  return true;
}

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<UrgScanNode>());
  rclcpp::shutdown();
  return 0;
}
