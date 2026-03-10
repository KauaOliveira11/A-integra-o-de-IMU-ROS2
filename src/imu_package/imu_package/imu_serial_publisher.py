import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

import serial
import time
import math

from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class ImuSerialPublisher(Node):

    def __init__(self):
        super().__init__('imu_serial_publisher')

        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)

        port = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value

        # TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        # Publishers
        self.pub_front_roll = self.create_publisher(Float32, '/imu/front/roll', 10)
        self.pub_front_pitch = self.create_publisher(Float32, '/imu/front/pitch', 10)

        self.pub_back_roll = self.create_publisher(Float32, '/imu/back/roll', 10)
        self.pub_back_pitch = self.create_publisher(Float32, '/imu/back/pitch', 10)

        try:
            self.serial_conn = serial.Serial(port, baudrate, timeout=0.1)

            self.serial_conn.setDTR(False)
            self.serial_conn.setRTS(False)

            time.sleep(2)
            self.serial_conn.reset_input_buffer()

            self.get_logger().info("Serial conectada")

        except serial.SerialException as e:
            self.get_logger().error(str(e))
            raise SystemExit

        self.timer = self.create_timer(0.01, self.read_and_publish)

    def euler_to_quaternion(self, roll, pitch, yaw):

        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)

        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)

        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy

        return qx, qy, qz, qw

    def publish_tf(self, frame_name, roll, pitch):

        t = TransformStamped()

        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = "wx200/base_link"
        t.child_frame_id = frame_name

        if frame_name == "imu_front":
            t.transform.translation.x = 0.5
            t.transform.translation.y = 0.0
            t.transform.translation.z = 0.0
        else:
            t.transform.translation.x = 0.0
            t.transform.translation.y = 0.0
            t.transform.translation.z = 0.0

        roll = math.radians(roll)
        pitch = math.radians(pitch)

        qx, qy, qz, qw = self.euler_to_quaternion(roll, pitch, 0.0)

        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw

        self.tf_broadcaster.sendTransform(t)

    def read_and_publish(self):

        if self.serial_conn.in_waiting > 0:

            raw = self.serial_conn.read_until(b';')

            line = raw.decode('utf-8', errors='ignore').strip().replace(';', '')

            if line:

                parts = line.split(',')

                if len(parts) == 18:

                    try:

                        roll1 = float(parts[0])
                        pitch1 = float(parts[1])
                        roll2 = float(parts[9])
                        pitch2 = float(parts[10])

                        msg = Float32()

                        msg.data = roll1
                        self.pub_front_roll.publish(msg)

                        msg.data = pitch1
                        self.pub_front_pitch.publish(msg)

                        msg.data = roll2
                        self.pub_back_roll.publish(msg)

                        msg.data = pitch2
                        self.pub_back_pitch.publish(msg)

                        # Publica TF
                        self.publish_tf("imu_front", roll1, pitch1)
                        self.publish_tf("imu_back", roll2, pitch2)

                    except ValueError:
                        pass


def main(args=None):

    rclpy.init(args=args)

    node = ImuSerialPublisher()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        if node.serial_conn.is_open:
            node.serial_conn.close()

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
