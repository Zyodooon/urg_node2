# urg_node2

ROS 2 driver node for Hokuyo URG/UST 2D LiDAR sensors using the bundled
`urg_library` submodule.

## Requirements

- ROS 2 Jazzy
- `colcon`
- A serial/USB Hokuyo LiDAR exposed as a readable device, for example
  `/dev/ttyACM0` or a stable symlink such as `/dev/lidar`

## Build

From this repository root:

```bash
source /opt/ros/jazzy/setup.bash
git submodule update --init --recursive
colcon build
source install/setup.bash
```

## Configure

The default configuration is in `config/params_serial.yaml`.

```yaml
urg_node2:
  ros__parameters:
    serial_port: '/dev/lidar'
    serial_baud: 115200
    frame_id: 'laser'
    scan_topic: 'scan'
```

If your sensor appears as `/dev/ttyACM0`, either update `serial_port` or pass an
override at launch time.

For a stable `/dev/lidar` symlink, create a udev rule matching your device. A
typical development shortcut is:

```bash
sudo ln -sf /dev/ttyACM0 /dev/lidar
```

Use a udev rule for production systems because `/dev/ttyACM0` numbering can
change after reconnects.

## Run

```bash
ros2 launch urg_node2 urg_node2.launch.py
```

Or run the node directly with parameter overrides:

```bash
ros2 run urg_node2 urg_node2_node --ros-args \
  -p serial_port:=/dev/ttyACM0 \
  -p serial_baud:=115200 \
  -p frame_id:=laser \
  -p scan_topic:=scan
```

The node publishes `sensor_msgs/msg/LaserScan` on the configured `scan_topic`.

## Verify

```bash
ros2 topic list
ros2 topic echo /scan --once
```

If the node repeatedly logs connection failures, check:

- The `serial_port` path exists.
- The current user can read and write the device.
- The sensor baud rate matches `serial_baud`.
- No other process is holding the serial device.
