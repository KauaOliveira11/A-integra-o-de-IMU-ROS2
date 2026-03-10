from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    imu_node = Node(
        package='imu_package',
        executable='imu_serial_publisher',
        name='imu_serial_publisher',
        output='screen',
        parameters=[
            {'port': '/dev/ttyACM0'},
            {'baudrate': 9600}
        ]
    )

    return LaunchDescription([
        imu_node
    ])
