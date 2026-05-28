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
from launch_ros.actions import ComposableNodeContainer, LoadComposableNodes
from launch_ros.descriptions import ComposableNode
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration


def launch_setup(context, *args, **kwargs):
    del args, kwargs

    # パラメータファイルのパス設定
    params_file = LaunchConfiguration('params_file').perform(context)
    if not params_file:
        connection_type = LaunchConfiguration('connection_type').perform(context)
        params_file = os.path.join(
            get_package_share_directory('urg_node2'),
            'config',
            'params_serial.yaml' if connection_type == 'serial' else 'params_ether.yaml'
        )

    # コンテナノードの起動
    container_node = ComposableNodeContainer(
        name='app_container',
        namespace=[],
        package='rclcpp_components',
        executable='component_container',
        output='screen',
    )

    # urg_node2をコンポーネントノードとして起動
    load_composable_nodes = LoadComposableNodes(
        target_container='app_container',
        composable_node_descriptions=[
            ComposableNode(
                package='urg_node2',
                plugin='urg_node2::UrgNode2',
                name='urg_node2',
                parameters=[params_file],
            ),
        ],
    )

    return [
        container_node,
        load_composable_nodes,
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('connection_type', default_value='serial'),
        DeclareLaunchArgument('params_file', default_value=''),
        OpaqueFunction(function=launch_setup),
    ])
