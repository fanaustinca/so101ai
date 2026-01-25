Markdown

# 🤖 LeRobot SO-100: The "Dad Demo" & FLL Guide

![Status](https://img.shields.io/badge/Status-Operational-green)
![Robot](https://img.shields.io/badge/Hardware-SO--100-blue)
![Platform](https://img.shields.io/badge/OS-Windows%20%2F%20WSL-orange)
![AI Model](https://img.shields.io/badge/Model-ACT%20Policy-purple)

Welcome! This repository documents the complete workflow for building, training, and deploying the **SO-100 Robot Arm** using the [Hugging Face LeRobot](https://github.com/huggingface/lerobot) library.

This guide is specifically tailored for **Windows users (via WSL2)** and focuses on the "Puppeteer" configuration (Human Leader Arm + Robot Follower Arm).

---

## 📋 Table of Contents
1. [Hardware Bill of Materials](#-1-hardware-bill-of-materials)
2. [Desktop Setup (The "Kitchen")](#-2-desktop-setup-windowswsl)
3. [Connecting the Robot (The "Bridge")](#-3-connecting-the-robot)
4. [The Workflow](#-4-the-workflow)
5. [🚨 The Debug Playbook (Troubleshooting)](#-5--the-debug-playbook-troubleshooting)

---

## 🛒 1. Hardware Bill of Materials

### A. The Robot Arms (The Hands)
* **The Follower (Active):** SO-100 Robot Arm Kit.
    * *Motors:* 6x Feetech STS3215.
    * *Controller:* ESP32-S3 / Feetech Bus Linker.
* **The Leader (Passive):** A secondary arm used for teleoperation.
    * *Note:* Using a leader arm is superior to a game controller because it provides smoother, human-like training data.

### B. Vision System (The Eyes)
* **Top Camera:** Logitech C920 (or equivalent 1080p webcam).
    * *Mounting:* High above the table, looking down at a 45-degree angle.
* **Wrist Camera:** Arducam or stripped webcam.
    * *Mounting:* Attached directly to the gripper to see the object up close.

### C. The Stage (The World)
* **Surface:** **Matte Yoga Mat** (Solid color, no patterns).
    * *Why?* Prevents glare, protects motors from stalling, and provides friction for gripping.
* **Lighting:** Dedicated desk lamp or ring light.
    * *Critical:* Do not rely on sunlight. Variable lighting kills AI performance.

---

## 💻 2. Desktop Setup (Windows/WSL)

Since we are on Windows, we need to create a Linux environment to run the AI.

### Step 1: Install WSL
Open **PowerShell (Admin)** and run:
```powershell
wsl --install
# RESTART YOUR COMPUTER NOW
Step 2: Install the USB Bridge
Windows blocks USB devices from Linux. We need usbipd to open the gate.

PowerShell

winget install -e --id dorssel.usbipd-win
# RESTART YOUR COMPUTER AGAIN
Step 3: Set up LeRobot (Inside Linux)
Open your Ubuntu terminal (search "Ubuntu" in Start Menu) and run:

Bash

# 1. Create a folder for your project
mkdir ~/lerobot_ws && cd ~/lerobot_ws

# 2. Download the LeRobot code
git clone [https://github.com/huggingface/lerobot.git](https://github.com/huggingface/lerobot.git)

# 3. Create a Python virtual environment (Keeps things clean)
conda create -n lerobot python=3.10
conda activate lerobot

# 4. Install the software
cd lerobot
pip install -e .
🔌 3. Connecting the Robot
⚠️ YOU MUST DO THIS EVERY TIME YOU PLUG THE ROBOT IN.

Plug in the Robot and the Leader arm to your laptop.

Open PowerShell (Admin) on Windows.

Find your devices:

PowerShell

usbipd list
(Look for "CP210x" or "Feetech". Note the BUSID, e.g., 2-1)

Attach them to Linux:

PowerShell

usbipd attach --wsl --busid <ROBOT_ID>
usbipd attach --wsl --busid <LEADER_ID>
🎬 4. The Workflow
Phase 1: Teleoperation (The "Handshake")
Before recording, prove the robot works.

Bash

python lerobot/scripts/control_robot.py teleoperate \
  --robot-path so100 \
  --robot-type so100
Success: When you move the Leader, the Follower moves instantly.

Phase 2: Data Collection (The "Training")
Record 50 episodes of your task (e.g., "Pick up the red block").

Bash

python lerobot/scripts/control_robot.py record \
  --robot-path so100 \
  --robot-type so100 \
  --repo-id <YOUR_GITHUB_USER>/<DATASET_NAME> \
  --num-episodes 50
Tip: Move smoothly. Pause for 1 second before grabbing the object.

Phase 3: The Demo (The "Magic Trick")
Run your trained AI policy.

Bash

python lerobot/scripts/lerobot_eval.py \
  --policy.path outputs/train/act_so100_real/checkpoints/last/pretrained_model \
  --env.type so100_real \
  --device cpu \
  --num-episodes 50
🚨 5. The Debug Playbook (Troubleshooting)
Problem: "Device Not Found" / "No such file or directory"
Cause: Linux cannot see the USB port.

Fix: You forgot the usbipd attach step.

Close the Linux terminal.

Open PowerShell (Admin).

Run usbipd list and usbipd attach again.

Problem: The Robot Twitches or Vibrates violently
Cause: The "Leader" arm is fighting the "Follower" arm, or the PID gains are too high.

Fix:

Check your cables. Ensure the Leader is plugged into the Leader port.

Restart the script.

Hold the Leader arm steady before hitting Enter.

Problem: The Robot Misses the Block (Visual Failure)
Cause: Lighting changes or Glare.

Fix:

Close the blinds. Sunlight creates hard shadows the AI doesn't understand.

Use the Lamp. Shine a bright light on the stage to overpower the room lights.

Check the Mat. Ensure there are no wrinkles or shiny spots on the table.

Problem: "Camera index not found"
Cause: The webcam is unplugged or another app (like Zoom) is using it.

Fix:

Close all other apps (Zoom, Discord, Camera App).

Unplug and Replug the camera.

Run ls /dev/video* in Ubuntu to see if it lists video0/video2.

Problem: FLL Demo Panic (AI won't start)
Emergency Plan:

Kill the code (Ctrl + C).

Switch to Teleoperation Mode (Phase 1 code).

Hand the Leader arm to a judge and let them try.

Spin: "We are now demonstrating the 'Data Collection' phase of the pipeline."
