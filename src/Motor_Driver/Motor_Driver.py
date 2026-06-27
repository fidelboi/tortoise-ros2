#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from gpiozero import Motor

class MotorDriver(Node):

    def __init__(self):
        super().__init__('motor_driver')

        self.motor1 = Motor(
            forward=27,
            backward=22,
            enable=17
        )

        self.motor2 = Motor(
            forward=24,
            backward=25,
            enable=23
        )

        self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.get_logger().info("Motor driver ready")

    def set_motor(self, motor, value):
        if value > 0:
            motor.forward(value)
        elif value < 0:
            motor.backward(-value)
        else:
            motor.stop()

    def cmd_vel_callback(self, msg):

        linear = msg.linear.x
        angular = msg.angular.z

        left = linear - angular
        right = linear + angular

        left = max(-1.0, min(1.0, left))
        right = max(-1.0, min(1.0, right))

        self.set_motor(self.motor1, left)

        # motor2 is reversed on your robot
        self.set_motor(self.motor2, -right)

def main(args=None):
    rclpy.init(args=args)

    node = MotorDriver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.motor1.stop()
    node.motor2.stop()

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
