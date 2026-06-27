import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge

import cv2
import numpy as np
import time  # Imported for the step-and-wait duration delay


class GreenBallTracker(Node):

    def __init__(self):
        super().__init__('green_ball_tracker')

        self.bridge = CvBridge()

        # Image subscriber - Strictly queue size 1 to avoid processing old frames
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            1
        )

        # Robot velocity publisher
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Green HSV range
        self.lower_green = np.array([25, 40, 40])
        self.upper_green = np.array([95, 255, 255])

        # --- STEP AND WAIT TUNING PARAMETERS ---
        self.threshold = 50          # Pixel deadband around center
        self.pulse_speed = 0.25      # High speed command to break heavy robot friction
        self.pulse_duration = 0.08   # How long (seconds) the robot turns per step
        self.wait_cooldown = 0.4     # Time (seconds) to wait for camera to catch up

        self.last_step_time = time.time()
        # ---------------------------------------

        self.get_logger().info(
            'Green Ball Tracker started. STEP-AND-WAIT control mode active.'
        )

    def image_callback(self, msg):
        # 1. Cooldown Enforcement
        # If we recently took a step, ignore incoming camera frames until the
        # robot has completely stopped and the camera pipeline has refreshed.
        current_time = time.time()
        if current_time - self.last_step_time < self.wait_cooldown:
            return  # Skip processing this frame entirely

        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )
        except Exception as e:
            self.get_logger().error(f'CV Bridge Error: {e}')
            return

        height, width = frame.shape[:2]
        center_x = width // 2

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)

        # Remove noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        twist_msg = Twist()

        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)

            if area > 8000:
                M = cv2.moments(largest_contour)

                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    error_x = center_x - cx

                    # 2. Step-and-Wait Alignment Logic
                    if abs(error_x) > self.threshold:
                        # Determine direction
                        direction = 1.0 if error_x > 0 else -1.0

                        # Apply a strong pulse command to overcome physical weight
                        twist_msg.angular.z = self.pulse_speed * direction
                        self.cmd_vel_pub.publish(twist_msg)
                        self.get_logger().info(f"Taking STEP: Speed {twist_msg.angular.z}")

                        # Let the robot move for a brief split-second
                        time.sleep(self.pulse_duration)

                        # FORCE IMMEDIATE STOP
                        twist_msg.angular.z = 0.0
                        self.cmd_vel_pub.publish(twist_msg)
                        self.get_logger().info("WAITING for camera to stabilize...")

                        # Start the cooldown clock
                        self.last_step_time = time.time()

                    else:
                        # Ball is centered, handle forward movement smoothly
                        twist_msg.angular.z = 0.0
                        if area < 80000:
                            twist_msg.linear.x = -0.1  # Move forward
                            self.get_logger().info("Centered: Moving Forward")
                        else:
                            twist_msg.linear.x = 0.0
                            self.get_logger().info("Centered: Target Reached")

                        self.cmd_vel_pub.publish(twist_msg)
        else:
            # Hard stop if ball is lost
            twist_msg.linear.x = 0.0
            twist_msg.angular.z = 0.0
            self.cmd_vel_pub.publish(twist_msg)

        cv2.imshow("Green Ball Tracking", frame)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = GreenBallTracker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    stop_msg = Twist()
    node.cmd_vel_pub.publish(stop_msg)

    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
