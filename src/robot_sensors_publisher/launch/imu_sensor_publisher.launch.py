from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    imu_node = Node(
        package='robot_sensors_publisher',
        executable='imu_serial_publisher',
        name='imu_serial_publisher',
        output='screen',
        parameters=[
            {'port': '/dev/ttyUSB0'},
            {'baudrate': 115200}
        ]
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        imu_node,
        rviz_node
    ])