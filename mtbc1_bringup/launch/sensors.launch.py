# Copyright (c) 2021 Juan Miguel Jimeno
# Revised to launch Slamtech rplidar and Oakd Camera
# Define MTBC1_LASER_SENSOR=rplidar
# Define MTBC1_DEPTH_SENSOR=oakd or oakdlite or oakdpro
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, GroupAction
from launch.substitutions import PathJoinSubstitution, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition
from launch_ros.actions import Node, SetRemap


def generate_launch_description():
    laser_sensor_name = os.getenv('MTBC1_LASER_SENSOR', '')
    depth_sensor_name = os.getenv('MTBC1_DEPTH_SENSOR', '')
    
    fake_laser_config_path = PathJoinSubstitution(
        [FindPackageShare('mtbc1_bringup'), 'config', 'fake_laser.yaml']
    )

    #indices
    #0 - depth topic (str)
    #1 - depth info topic (str)
    depth_topics = {
        '': ['', '', '', {}, '', ''],
        'oakd': ['/right/image_rect', '/right/camera_info'],
        'oakdlite': ['/right/image_rect', '/right/camera_info'],
        'oakdpro': ['/right/image_rect', '/right/camera_info'],
    }

    point_cloud_topics = {
        '': '',
        'oakd': '/stereo/points',
        'oakdlite': '/stereo/points',
        'oakdpro': '/stereo/points',
    }

    laser_launch_path = PathJoinSubstitution(
        [FindPackageShare('mtbc1_bringup'), 'launch', 'lasers.launch.py']
    )

    depth_launch_path = PathJoinSubstitution(
        [FindPackageShare('mtbc1_bringup'), 'launch', 'depth.launch.py']
    )

    return LaunchDescription([
        GroupAction(
            actions=[
                SetRemap(src=point_cloud_topics[depth_sensor_name], dst='/camera/depth/color/points'),
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(depth_launch_path),
                    condition=IfCondition(PythonExpression(['"" != "', depth_sensor_name, '"'])),
                    launch_arguments={'sensor': depth_sensor_name}.items()   
                )
            ]
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(laser_launch_path),
            condition=IfCondition(PythonExpression(['"" != "', laser_sensor_name, '"'])),
            launch_arguments={
                'sensor': laser_sensor_name
            }.items()   
        ),
        Node(
            condition=IfCondition(PythonExpression(['"" != "', laser_sensor_name, '" and ', '"', laser_sensor_name, '" in "', str(list(depth_topics.keys())[1:]), '"'])),
            package='depthimage_to_laserscan',
            executable='depthimage_to_laserscan_node',
            remappings=[('depth', depth_topics[depth_sensor_name][0]),
                        ('depth_camera_info', depth_topics[depth_sensor_name][1])],
            parameters=[fake_laser_config_path]
        ) 
    ])
