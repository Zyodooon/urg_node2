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
from launch import LaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch.actions import (DeclareLaunchArgument, EmitEvent, OpaqueFunction, RegisterEventHandler)
from launch.event_handlers import OnProcessStart
from launch.events import matches_action
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition


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

    # urg_node2をライフサイクルノードとして起動
    lifecycle_node = LifecycleNode(
        package='urg_node2',
        executable='urg_node2_node',
        name=LaunchConfiguration('node_name'),
        remappings=[('scan', LaunchConfiguration('scan_topic_name'))],
        parameters=[params_file],
        namespace='',
        output='screen',
    )

    # Unconfigure状態からInactive状態への遷移（auto_startがtrueのとき実施）
    urg_node2_node_configure_event_handler = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=lifecycle_node,
            on_start=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(lifecycle_node),
                        transition_id=Transition.TRANSITION_CONFIGURE,
                    ),
                ),
            ],
        ),
        condition=IfCondition(LaunchConfiguration('auto_start')),
    )

    # Inactive状態からActive状態への遷移（auto_startがtrueのとき実施）
    urg_node2_node_activate_event_handler = RegisterEventHandler(
        event_handler=OnStateTransition(
            target_lifecycle_node=lifecycle_node,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(lifecycle_node),
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    ),
                ),
            ],
        ),
        condition=IfCondition(LaunchConfiguration('auto_start')),
    )

    # パラメータについて
    return [
        lifecycle_node,
        urg_node2_node_configure_event_handler,
        urg_node2_node_activate_event_handler,
    ]


def generate_launch_description():
    # パラメータについて
    # auto_start      : 起動時自動でActive状態まで遷移 (default)true
    # connection_type : params_file未指定時の接続方式。serialまたはether (default)"serial"
    # params_file     : 使用するパラメータファイル。指定時はconnection_typeより優先
    # node_name       : ノード名 (default)"urg_node2"
    # scan_topic_name : トピック名 (default)"scan" *マルチエコー非対応*
    return LaunchDescription([
        DeclareLaunchArgument('auto_start', default_value='true'),
        DeclareLaunchArgument('connection_type', default_value='serial'),
        DeclareLaunchArgument('params_file', default_value=''),
        DeclareLaunchArgument('node_name', default_value='urg_node2'),
        DeclareLaunchArgument('scan_topic_name', default_value='scan'),
        OpaqueFunction(function=launch_setup),
    ])
