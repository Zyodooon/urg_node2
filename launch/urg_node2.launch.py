# Copyright 2022 eSOL Co.,Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    config_file_path = os.path.join(
        get_package_share_directory('urg_node2'),
        'config',
        'params_serial.yaml'
    )

    return LaunchDescription([
        DeclareLaunchArgument('serial_port', default_value='/dev/lidar'),
        DeclareLaunchArgument('serial_baud', default_value='115200'),
        DeclareLaunchArgument('frame_id', default_value='laser'),
        DeclareLaunchArgument('scan_topic', default_value='scan'),
        Node(
            package='urg_node2',
            executable='urg_node2_node',
            name='urg_node2',
            parameters=[
                config_file_path,
                {
                    'serial_port': LaunchConfiguration('serial_port'),
                    'serial_baud': ParameterValue(LaunchConfiguration('serial_baud'), value_type=int),
                    'frame_id': LaunchConfiguration('frame_id'),
                    'scan_topic': LaunchConfiguration('scan_topic'),
                },
            ],
            output='screen',
        ),
    ])
