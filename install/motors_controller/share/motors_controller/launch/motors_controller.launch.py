#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    cmd_vel_node = Node(
        package='motors_controller',
        executable='cmd_vel_to_serial',
        name='cmd_vel_to_serial_ros2',
        output='screen',
        parameters=[
            {'port': '/dev/ttyUSB0'},
            {'baudrate': 115200}
        ]

    )

    return LaunchDescription([
        cmd_vel_node
    ])
