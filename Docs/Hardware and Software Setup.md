# 🤖 LeRobot SO-100 Starter Guide

Welcome! This repository documents the setup, training, and deployment of the **SO-100 Robot Arm** using the [Hugging Face LeRobot](https://github.com/huggingface/lerobot) library.

This guide is designed for Windows users (using WSL2) who want to build a low-cost, high-capability AI robot.

---

## 🛒 Part 1: Hardware Bill of Materials (BOM)

Before you write code, you need the right gear. Here is the recommended setup for a "Puppeteer" configuration (Human Leader + Robot Follower).

### 1. The Robot Arms
You need **two** arms for the best results: one to record data (Leader) and one to do the work (Follower).
* **The Follower (Active):** SO-100 Robot Arm Kit.
    * *Motors:* Feetech STS3215 (x6).
    * *Controller:* ESP32-S3 or similar bus servo controller.
    * *Source:* [WowRobo](https://wowrobo.us/) (Pre-assembled) or 3D print it yourself using the [Open Source Files](https://github.com/TheRobotStudio/SO-100).
* **The Leader (Passive):** A secondary arm to hold in your hand.
    * *Option A (Pro):* Buy a second SO-100 arm (cheaper "Leader" kits often have no motors or weaker motors).
    * *Option B (Budget):* 3D print a "dummy" arm with the same dimensions.

### 2. Vision System (The Eyes)
You need **two cameras** to train the ACT policy effectively.
* **Camera 1 (Top View):** Mounts high above the table looking down.
    * *Recommendation:* Logitech C920 or any 1080p Webcam.
* **Camera 2 (Wrist View):** Mounts directly to the robot's "wrist."
    * *Recommendation:* A smaller, lightweight webcam (stripped of its case) or a specific Arducam module.
* **Mounting:** You will need a simple aluminum extrusion stand or a 3D printed camera mount.

### 3. The "Stage" (Environment)
Consistency is key for AI.
* **Base:** A 2ft x 2ft piece of plywood or shelf board.
* **Surface:** A solid-color **Yoga Mat** (Matte finish, no patterns). This prevents glare and gives the gripper "squish" to grab objects securely.
* **Lighting:** A dedicated desk lamp or ring light. *Never rely on sunlight from a window.*

---

## 💻 Part 2: Desktop Setup (Windows/WSL)

This project runs on Linux, but you can use a Windows laptop (like a Lenovo Legion) by using the **Windows Subsystem for Linux (WSL)**.

### Step 1: Install WSL
Open PowerShell as Administrator and run:
```powershell
wsl --install
# Restart your computer after this finishes.
Step 2: Fix the USB "Invisible Wall"
By default, WSL cannot see USB devices plugged into Windows. You need usbipd-win to bridge the connection.

Open PowerShell (Admin).

Install the tool:

PowerShell

winget install -e --id dorssel.usbipd-win
Restart your computer.

Step 3: Install LeRobot Software
Open your Ubuntu (WSL) terminal and run these commands to set up the brain:

Bash

# 1. Create a workspace
mkdir ~/lerobot_ws && cd ~/lerobot_ws

# 2. Clone the repository
git clone [https://github.com/huggingface/lerobot.git](https://github.com/huggingface/lerobot.git)

# 3. Create a Python environment (Highly Recommended)
conda create -n lerobot python=3.10
conda activate lerobot

# 4. Install dependencies
cd lerobot
pip install -e .
🔌 Part 3: Connecting the Robot
Every time you plug the robot in, you must "pass it through" to Linux.

Plug in your Robot and Leader arm.

Open PowerShell (Admin) and find their Bus IDs:

PowerShell

usbipd list
(Look for devices named "Feetech", "CP210x", or "Serial Converter")

Attach them (Replace x-x with your actual IDs, e.g., 2-1):

PowerShell

usbipd attach --wsl --busid <ROBOT_ID>
usbipd attach --wsl --busid <LEADER_ID>
Now, inside your Ubuntu terminal, check if they are visible:

Bash

ls /dev/ttyUSB*
🎬 Part 4: Workflow
1. Teleoperation (Testing)
Before recording, verify you can control the robot with the leader arm.

Bash

python lerobot/scripts/control_robot.py teleoperate \
  --robot-path so100 \
  --robot-type so100
2. Data Collection
Record 50 episodes of a simple task (e.g., "Pick up the cube").

Bash

python lerobot/scripts/control_robot.py record \
  --robot-path so100 \
  --robot-type so100 \
  --repo-id <YOUR_USERNAME>/<DATASET_NAME> \
  --num-episodes 50
3. Training (Cloud Recommended)
If your laptop doesn't have an NVIDIA GPU, zip your lerobot/data folder and upload it to Google Colab to train.

Training time on Colab: ~45 minutes.

Training time on CPU: ~10+ hours.

4. Evaluation ( The Demo)
Run the trained AI policy on the real robot:

Bash

python lerobot/scripts/lerobot_eval.py \
  --policy.path outputs/train/act_so100_real/checkpoints/last/pretrained_model \
  --env.type so100_real \
  --device cpu \
  --num-episodes 50
⚠️ Troubleshooting Tips for FLL Demo
Lighting: If the robot misses the object, check for shadows. Turn on your dedicated lamp.

Glare: Ensure you are using the matte yoga mat background.

USB Error: If the script says "Device not found," you likely forgot the usbipd attach step in PowerShell.
