import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import serial

class CmdVelToSerial(Node):
    def __init__(self):
        super().__init__('cmd_vel_to_serial_node')
        
        # Parâmetros de conexão
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baud', 9600)
        
        port = self.get_parameter('port').get_parameter_value().string_value
        baud = self.get_parameter('baud').get_parameter_value().integer_value

        try:
            self.arduino = serial.Serial(port, baud, timeout=0.1)
            self.get_logger().info(f'Conectado ao Arduino na porta {port} a {baud} bps')
        except Exception as e:
            self.get_logger().error(f'Falha ao conectar na Serial: {e}')

        # Inscrição no tópico cmd_vel (padrão do ROS 2)
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10) # QoS History Depth

    def cmd_vel_callback(self, msg):
        vx = msg.linear.x
        vy = msg.linear.y
        vw = msg.angular.z
        
        # Formata a string idêntica ao que o Arduino Mega espera
        comando = f"<{vx:.3f},{vy:.3f},{vw:.3f}>\n"
        
        try:
            self.arduino.write(comando.encode('utf-8'))
        except Exception as e:
            self.get_logger().warn(f'Erro ao enviar para Serial: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelToSerial()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
