#!/usr/bin/env python3
"""
teleop_controller.py
====================
ROS 2 node that reads a joystick/gamepad and publishes geometry_msgs/Twist
to /cmd_vel for a differential-drive robot.

Axes mapping (PS4 / Xbox layout – change AXIS_* constants to suit):
  Left-stick Y  → linear.x  (forward / backward)
  Right-stick X → angular.z (turn left / right)

Dependencies:
  sudo apt install ros-<distro>-joy          # joy driver node
  ros2 run joy joy_node                      # run this first

Usage:
  ros2 run <your_package> teleop_controller
  # or directly:
  python3 teleop_controller.py
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


# ─── Axis / Button indices (change to match your controller) ──────────────────
AXIS_LINEAR   = 1   # Left stick Y  (forward / backward)
AXIS_ANGULAR  = 3   # Right stick X (turn left / right)
BTN_DEADMAN   = 4   # LB / L1  – hold to enable movement (set to None to disable)
# ─────────────────────────────────────────────────────────────────────────────

# ─── Scaling (m/s and rad/s) ──────────────────────────────────────────────────
MAX_LINEAR_SPEED  = 0.5   # m/s
MAX_ANGULAR_SPEED = 1.0   # rad/s
DEADZONE          = 0.05  # ignore stick values smaller than this
# ─────────────────────────────────────────────────────────────────────────────


class TeleopController(Node):

    def __init__(self):
        super().__init__('teleop_controller')

        # ── Parameters (overridable from CLI or launch file) ──────────────────
        self.declare_parameter('max_linear_speed',  MAX_LINEAR_SPEED)
        self.declare_parameter('max_angular_speed', MAX_ANGULAR_SPEED)
        self.declare_parameter('axis_linear',   AXIS_LINEAR)
        self.declare_parameter('axis_angular',  AXIS_ANGULAR)
        self.declare_parameter('btn_deadman',   BTN_DEADMAN if BTN_DEADMAN is not None else -1)
        self.declare_parameter('deadzone',      DEADZONE)
        self.declare_parameter('joy_topic',     '/joy')
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')

        self._max_lin  = self.get_parameter('max_linear_speed').value
        self._max_ang  = self.get_parameter('max_angular_speed').value
        self._ax_lin   = self.get_parameter('axis_linear').value
        self._ax_ang   = self.get_parameter('axis_angular').value
        self._btn_dead = self.get_parameter('btn_deadman').value   # -1 → disabled
        self._dz       = self.get_parameter('deadzone').value
        joy_topic      = self.get_parameter('joy_topic').value
        cmd_topic      = self.get_parameter('cmd_vel_topic').value

        # ── Publisher & Subscriber ─────────────────────────────────────────────
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        self._cmd_pub = self.create_publisher(Twist, cmd_topic, 10)
        self._joy_sub = self.create_subscription(Joy, joy_topic, self._joy_cb, qos)

        # Publish zero velocity at startup so the robot stays still
        self._cmd_pub.publish(Twist())

        self.get_logger().info(
            f"teleop_controller ready\n"
            f"  joy_topic     : {joy_topic}\n"
            f"  cmd_vel_topic : {cmd_topic}\n"
            f"  axis_linear   : {self._ax_lin}  (max {self._max_lin} m/s)\n"
            f"  axis_angular  : {self._ax_ang}  (max {self._max_ang} rad/s)\n"
            f"  deadman button: {'disabled' if self._btn_dead < 0 else self._btn_dead}\n"
            f"  deadzone      : {self._dz}"
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _apply_deadzone(self, value: float) -> float:
        """Return 0.0 if |value| < deadzone, else scale the remaining range to [0, 1]."""
        if abs(value) < self._dz:
            return 0.0
        # Rescale so motion starts from the deadzone edge (no sudden jump)
        sign = 1.0 if value > 0 else -1.0
        return sign * (abs(value) - self._dz) / (1.0 - self._dz)

    def _safe_axis(self, joy: Joy, index: int) -> float:
        if index < 0 or index >= len(joy.axes):
            self.get_logger().warn(
                f"Axis index {index} out of range (controller has {len(joy.axes)} axes)",
                throttle_duration_sec=5.0
            )
            return 0.0
        return joy.axes[index]

    def _safe_button(self, joy: Joy, index: int) -> bool:
        if index < 0 or index >= len(joy.buttons):
            return False
        return bool(joy.buttons[index])

    # ── Joy callback ──────────────────────────────────────────────────────────

    def _joy_cb(self, msg: Joy) -> None:
        # Deadman check
        deadman_active = (
            self._btn_dead < 0                          # feature disabled → always active
            or self._safe_button(msg, self._btn_dead)   # button held down
        )

        twist = Twist()

        if deadman_active:
            raw_lin = self._safe_axis(msg, self._ax_lin)
            raw_ang = self._safe_axis(msg, self._ax_ang)

            twist.linear.x  =  self._apply_deadzone(raw_lin) * self._max_lin
            twist.angular.z =  self._apply_deadzone(raw_ang) * self._max_ang
        # else: all fields are 0.0 by default → robot stops

        self._cmd_pub.publish(twist)


# ── Entry point ───────────────────────────────────────────────────────────────

def main(args=None):
    rclpy.init(args=args)
    node = TeleopController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Publish one last zero-velocity message before shutting down
        node._cmd_pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

