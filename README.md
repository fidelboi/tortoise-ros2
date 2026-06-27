╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ████████╗ ██████╗ ██████╗ ████████╗ ██████╗ ██╗███████╗     ║
║   ╚══██╔══╝██╔═══██╗██╔══██╗╚══██╔══╝██╔═══██╗██║██╔════╝     ║
║      ██║   ██║   ██║██████╔╝   ██║   ██║   ██║██║███████╗     ║
║      ██║   ██║   ██║██╔══██╗   ██║   ██║   ██║██║╚════██║     ║
║      ██║   ╚██████╔╝██║  ██║   ██║   ╚██████╔╝██║███████║     ║
║      ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝╚══════╝     ║
║                                                              ║
║      Vision-Based Autonomous Differential Drive Robot        ║
╚══════════════════════════════════════════════════════════════╝

# 🐢 Tortoise: Differential Drive Robot

> **Why "Tortoise"?** The robot's compact, rounded shell-like structure resembles a tortoise. It's small, sturdy, and surprisingly nimble!

A fully autonomous differential drive robot built with ROS 2 Humble, capable of:
- ⌨️ **Keyboard teleoperation** (arrow keys / WASD)
- 🎮 **Gamepad/Joystick control** (with deadzone & dynamic speed scaling)
- 🎯 **Autonomous green ball tracking** (using HSV color detection & proportional control)

Perfect for learning robotics, computer vision, and ROS 2 fundamentals.

---

## 📋 Table of Contents

- [Features](#features)
- [Hardware Specifications](#hardware-specifications)
- [Software Stack](#software-stack)
- [Quick Start](#quick-start)
- [System Architecture](#system-architecture)
- [Usage Modes](#usage-modes)
- [Calibration & Tuning](#calibration--tuning)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## ✨ Features

### Control Modes
- **Keyboard Control**: Non-blocking terminal input with instant response
- **Gamepad Control**: Full analog stick support with configurable deadzone
- **Autonomous Mode**: Real-time green ball detection and pursuit using OpenCV

### Computer Vision
- HSV color space filtering for robust green detection
- Morphological operations (erosion/dilation) for noise reduction
- Contour detection with centroid calculation
- Proportional control for smooth tracking

### ROS 2 Integration
- Modular node architecture (separate nodes for each control mode)
- Launch files for easy mode switching
- Parameter server integration for dynamic configuration
- Standard `/cmd_vel` (Twist) messaging for motor control

---

## 🔧 Hardware Specifications

| Component | Model | Notes |
|-----------|-------|-------|
| **Compute** | Raspberry Pi 4 (4GB+) | Runs ROS 2 Humble |
| **Motors** | DC motors (5-12V) | Differential drive configuration |
| **Motor Driver** | L298N | Dual H-bridge for independent wheel control |
| **Camera** | USB Webcam | 30 FPS, VGA resolution sufficient |
| **Power** | 5V (RPi) + 12V (Motors) | Separate supplies recommended |
| **Chassis** | Custom/3D-printed | Compact form factor |

### Pinout (L298N Motor Driver)
```
L298N Pin → RPi GPIO
IN1 (Left Motor Fwd)  → GPIO 17
IN2 (Left Motor Rev)  → GPIO 18
IN3 (Right Motor Fwd) → GPIO 27
IN4 (Right Motor Rev) → GPIO 22
ENA (Left PWM)        → GPIO 12
ENB (Right PWM)       → GPIO 13
GND                   → GND
```

---

## 💻 Software Stack

```
ROS 2 Humble
├── rclpy (Python client library)
├── geometry_msgs (Twist for motor control)
├── sensor_msgs (Camera image streams)
├── joy (Gamepad driver)
└── cv_bridge (OpenCV ↔ ROS image conversion)

OpenCV 4.x (computer vision)
├── HSV color space conversion
├── Contour detection
└── Morphological operations

Python 3.10+
```

### Dependencies
```bash
ros-humble-rclpy
ros-humble-std-msgs
ros-humble-geometry-msgs
ros-humble-sensor-msgs
ros-humble-cv-bridge
ros-humble-joy
python3-opencv
```

---

## 🚀 Quick Start

### 1. Prerequisites

**On Raspberry Pi 4 with Ubuntu 22.04 LTS:**

```bash
# Install ROS 2 Humble (if not already installed)
sudo apt update
sudo apt install ros-humble-desktop

# Install dependencies
sudo apt install python3-opencv ros-humble-cv-bridge ros-humble-joy

# Source ROS setup
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 2. Clone & Build

```bash
# Create ROS 2 workspace
mkdir -p ~/ros_ws/src
cd ~/ros_ws

# Clone this repository
git clone https://github.com/YOUR_USERNAME/tortoise-robot.git src/robot_control

# Build the package
colcon build --symlink-install

# Source workspace
source install/setup.bash
```

### 3. Run the Robot

#### Keyboard Control
```bash
ros2 launch robot_control robot_keyboard.launch.py
```
**Controls:**
- `↑` or `W` - Forward
- `↓` or `S` - Backward
- `←` or `A` - Turn Left
- `→` or `D` - Turn Right
- `SPACE` - Stop
- `Q` - Quit

#### Gamepad Control
```bash
# First, ensure gamepad is detected
ls /dev/input/js*

# Launch gamepad controller
ros2 launch robot_control robot_gamepad.launch.py
```
**Controls:**
- Left Analog Stick (Y-axis) - Forward/Backward
- Right Analog Stick (X-axis) - Turn Left/Right
- `A` Button - Boost speed (2x multiplier)
- `Start` - Quit

#### Ball Follower (Autonomous)
```bash
ros2 launch robot_control robot_ball_follower.launch.py
```
**How it works:**
1. Captures video from USB camera
2. Detects green objects using HSV thresholding
3. Calculates centroid of largest green region
4. Adjusts left/right wheel speeds using proportional control
5. Tracks the ball in real-time

**Calibration:**
Press `C` while running to enter HSV calibration mode. Adjust sliders to match your green ball color.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      ROS 2 Humble                            │
│                    (Humble Hawksbill)                         │
└─────────────────────────────────────────────────────────────┘
                              ▲
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
        ┌─────────────┐ ┌──────────┐ ┌──────────────┐
        │ Keyboard    │ │ Gamepad  │ │ Ball Follower│
        │ Controller  │ │ Controller│ │ (CV Node)    │
        │ Node        │ │ Node     │ │              │
        └─────────────┘ └──────────┘ └──────────────┘
                    │         │         │
                    └─────────┼─────────┘
                              ▼
                    ┌─────────────────────┐
                    │  /cmd_vel Publisher │
                    │  (Twist Messages)   │
                    └─────────────────────┘
                              ▼
                    ┌─────────────────────┐
                    │  Motor Driver Node  │
                    │  (L298N Controller) │
                    └─────────────────────┘
                              ▼
                    ┌─────────────────────┐
                    │  Differential Drive │
                    │  (Left & Right PWM) │
                    └─────────────────────┘
```

### Node Details

| Node | Topic | Function |
|------|-------|----------|
| `keyboard_controller` | `/cmd_vel` | Reads terminal input, publishes Twist |
| `gamepad_controller` | `/cmd_vel` (via `/joy`) | Reads gamepad, publishes Twist |
| `ball_follower` | `/cmd_vel` | Processes camera feed, publishes Twist for tracking |
| `motor_driver` | Subscribes to `/cmd_vel` | Controls L298N PWM pins |

---

## 🎮 Usage Modes

### Mode 1: Keyboard Teleoperation
Perfect for learning basic robot control and navigation.

```python
# Internal logic
linear_velocity  = forward_input  * max_speed
angular_velocity = turn_input * max_angular_speed
publish_twist(linear_velocity, angular_velocity)
```

**Advantages:** Simple, intuitive, instant response
**Disadvantages:** Requires active input, no autonomous behavior

---

### Mode 2: Gamepad Control
Enhanced control with analog sticks and pressure sensitivity.

```python
# Deadzone handling
if abs(joystick_value) < deadzone_threshold:
    joystick_value = 0

# Speed scaling
speed = base_speed * joystick_value
if boost_button_pressed:
    speed *= boost_multiplier
```

**Advantages:** Smooth analog control, pressure-sensitive
**Disadvantages:** Requires gamepad hardware

---

### Mode 3: Autonomous Ball Tracking
Computer vision-based pursuit of green objects.

**Algorithm:**
```
1. Capture frame from USB camera
2. Convert BGR → HSV color space
3. Apply HSV thresholding: range(35-85°, 40-255, 40-255)
4. Morphological operations: erode → dilate
5. Find contours, get centroid of largest region
6. Proportional control:
   error = centroid_x - frame_center_x
   angular_velocity = Kp * error
7. Publish Twist with fixed forward speed + computed angular velocity
```

**Tuning Parameters** (`config/robot_params.yaml`):
```yaml
# HSV Thresholding (adjust for your green ball)
hsv_lower: [35, 40, 40]      # H, S, V minimum
hsv_upper: [85, 255, 255]    # H, S, V maximum

# Proportional control gain
kp_angular: 0.003             # Increase for faster tracking
min_contour_area: 500         # Pixels² - ignore small noise

# Motion constraints
max_linear_speed: 0.3         # m/s
max_angular_speed: 0.5        # rad/s
```

---

## 🎯 Calibration & Tuning

### Camera Calibration (HSV Range)

1. **Run ball follower in calibration mode:**
   ```bash
   ros2 run robot_control ball_follower.py --calibrate
   ```

2. **Adjust HSV sliders** to highlight only the green ball:
   - H (Hue): 0-180 (green typically 35-85)
   - S (Saturation): 0-255 (higher = more pure color)
   - V (Value): 0-255 (brightness)

3. **Save calibrated values** to `config/robot_params.yaml`

### Speed Tuning

Edit `config/robot_params.yaml`:
```yaml
max_linear_speed: 0.3    # Increase for faster forward motion
max_angular_speed: 0.5   # Increase for sharper turns
```

### Proportional Gain (Kp)

For ball follower tracking smoothness:
```yaml
kp_angular: 0.003        # Too low = sluggish tracking
                         # Too high = oscillation/overshoot
                         # Start at 0.003, adjust ±0.001
```

---

## 🐛 Troubleshooting

### Problem: Keyboard input not responding

**Solution:**
```bash
# Ensure terminal is in raw mode (non-canonical input)
stty -echo -icanon
```

The keyboard controller uses `termios` for non-blocking input to avoid key repeat delay.

---

### Problem: Gamepad not detected

**Solution:**
```bash
# Check connected devices
ls -la /dev/input/js*

# If not found, install joy driver
sudo apt install ros-humble-joy

# Test with jstest
jstest /dev/input/js0

# Grant permissions
sudo chmod a+rw /dev/input/js*
```

---

### Problem: Ball follower is erratic/oscillating

**Solution:**
1. **Reduce Kp gain:**
   ```yaml
   kp_angular: 0.002  # Lower from 0.003
   ```

2. **Increase minimum contour area** (filter noise):
   ```yaml
   min_contour_area: 1000  # Ignore tiny blobs
   ```

3. **Improve HSV calibration** (ensure crisp green detection)

---

### Problem: Robot drifts left/right during autonomous tracking

**Solution:**
- Check motor alignment (wheels perpendicular to chassis)
- Verify L298N PWM frequency consistency
- Balance motor speeds with differential gains 

---

## 📚 Project Structure

```
tortoise/
├── README.md
├── LICENSE
├── src/
│   ├── robot_driver/
│   ├── keyboard_teleop/
│   ├── vision_follower/
│   └── ...
├── launch/
├── images/
├── docs/

```

---

## 🚀 Future Enhancements

- [ ] **SLAM Integration**: Autonomous mapping with `slam_toolbox`
- [ ] **Navigation Stack**: Goal-based navigation with Nav2
- [ ] **Multi-Object Tracking**: Track multiple colored balls
- [ ] **PID Control**: Replace proportional control with tuned PID
- [ ] **IMU Integration**: Add gyroscope for drift correction
- [ ] **Web Dashboard**: Real-time telemetry & video stream via web browser
- [ ] **Object Detection**: Use YOLO for arbitrary object following
- [ ] **RViz Visualization**: Real-time robot pose & sensor data

---

## 📸 Demo

![robot](/images/img1.jpeg)

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs via GitHub Issues
- Submit pull requests for improvements
- Suggest new features or control modes
- Share calibration values for different environments

---

## 📖 References & Learning Resources

- [ROS 2 Humble Documentation](https://docs.ros.org/en/humble/)
- [rclpy Python Client Library](https://docs.ros.org/en/humble/Packages/rclpy/API.html)
- [OpenCV HSV Color Space](https://docs.opencv.org/master/df/d9d/tutorial_py_colorspaces.html)
- [Raspberry Pi GPIO Control](https://www.raspberrypi.com/documentation/computers/os.html)
- [Differential Drive Kinematics](https://en.wikipedia.org/wiki/Differential_wheeled_robot)

---

## 📄 License

This project is licensed under the **MIT License** — see [`LICENSE`](LICENSE) file for details.

You are free to use, modify, and distribute this project for educational and commercial purposes.

---

## 💬 Questions & Support

- **Issues**: Open a GitHub Issue for bugs or feature requests
- **Discussions**: Start a Discussion for general questions
- **Email**: syed.burhan.441@gmail.com

---

**Built with ❤️ by burhan.

*Happy robotics! 🤖🐢*
