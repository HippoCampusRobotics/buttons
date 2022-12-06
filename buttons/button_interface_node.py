import pigpio
import rcl_interfaces.msg
import rclpy
from rclpy.exceptions import InvalidParameterTypeException
from rclpy.node import Node
from typing import List
import os

from buttons_msgs.msg import Button


class ButtonInterfaceNode(Node):

    def __init__(self, node_name: str) -> None:
        super().__init__(node_name)
        self._ok = False

        self.button_pub = self.create_publisher(Button, 'button', 10)

        self.gpio_guard_time = 1.0

        # parameters
        self.gpios: List = []

        if not self.init_params():
            return

        self.pi = pigpio.pi()
        if not self.pi.connected:
            self.get_logger().fatal('Could not connect to pigpiod.')
            return

        self.times = {}
        for gpio in self.gpios:
            self.times[gpio] = self.get_clock().now().nanoseconds * 1e-9
            self.pi.set_pull_up_down(gpio, pigpio.PUD_UP)
            self.pi.callback(gpio, pigpio.FALLING_EDGE, self.on_falling_edge)

        self._ok = True

    def is_okay(self):
        return self._ok

    def init_params(self):
        descriptor = rcl_interfaces.msg.ParameterDescriptor()
        descriptor.name = 'gpios'
        descriptor.description = ('GPIOs to use as inputs.')
        descriptor.read_only = True
        descriptor.type = (
            rcl_interfaces.msg.ParameterType.PARAMETER_INTEGER_ARRAY)
        try:
            param = self.declare_parameter(descriptor.name,
                                           descriptor=descriptor)
        except InvalidParameterTypeException as e:
            self.get_logger().fatal(f'{e}')
            return False
        if param.type_ == rclpy.Parameter.Type.NOT_SET:
            self.get_logger().fatal(f'Required parameter {param.name} not set.')
            return False

        self.gpios = param.value
        self.get_logger().info(f'{param.name}={param.value}')
        return True

    def on_falling_edge(self, gpio, *_):
        now = self.get_clock().now().nanoseconds * 1e-9
        if now - self.times[gpio] < 1.0:
            return
        self.times[gpio] = now
        try:
            index = self.gpios.index(gpio)
        except ValueError:
            self.get_logger().error(
                f'Button at GPIO {gpio} pressed, but it is not in list of known'
                ' GPIOs')
        msg = Button()
        msg.header.frame_id = os.path.basename(self.get_name())
        msg.button = index
        self.button_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ButtonInterfaceNode('buttons')
    if not node.is_okay():
        node.destroy_node()
        return

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()


if __name__ == '__main__':
    main()
