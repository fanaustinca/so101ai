# 🤖 SO-101 "Titan": Advanced Manipulation Policy

![System](https://img.shields.io/badge/System-SO--101-blue)
![Architecture](https://img.shields.io/badge/Model-ACT%20(Action%20Chunking)-purple)
![Reliability](https://img.shields.io/badge/Lighting-Invariant-yellow)
![Platform](https://img.shields.io/badge/OS-Windows%20WSL2-orange)

## 📖 Project Overview
This repository contains the codebase, training data, and model weights for the **SO-101 Robot Arm**. Unlike basic demos, this implementation focuses on **environmental robustness**—specifically the ability to operate under variable lighting (gyms, classrooms) and handling physical disturbances.

---

## 🛠️ Phase 0: The Physical Rig (Critical)

**Engineering Note:** 80% of AI failures are actually hardware/setup failures. Do not skip this.

### 1. Vision System Rigidity
* **Requirement:** Cameras must not move *at all* relative to the robot base.
* **Specification:** Use rigid aluminum extrusion or 3D printed hard-mounts.
* **Warning:** If a camera shifts by even 2mm after training, the robot will miss the target by 2mm.

### 2. The "Stage" Configuration
* **Surface:** Matte Yoga Mat (3mm-6mm thickness).
    * *Function:* Provides compliance (squish) for grasp errors and eliminates specular highlights (glare).
* **Lighting:** A dedicated local light source (Desk lamp/Ring light).
    * *Protocol:* The local light must overpower ambient room lighting to ensure consistent shadows.

---

## 💻 Phase 1: Environment Setup (Windows/WSL2)

### 1.1 System Dependencies
We use WSL2 to provide the Linux kernel required for the LeRobot stack.

```bash
# Powershell (Admin)
wsl --install
winget install -e --id dorssel.usbipd-win
```
# RESTART REQUIRED
1.2 The "USB Bridge" ProtocolThe SO-101 communicates via serial (UART) over USB. You must bridge these ports every session.PowerShell# Powershell (Admin) - Run every reboot
```powershell
# Powershell (Admin) - Run every reboot
usbipd list
usbipd attach --wsl --busid <ROBOT_ID>
usbipd attach --wsl --busid <LEADER_ID>
```
1.3 Software Installation (Ubuntu)Bash# Ubuntu Terminal
```bash
# Ubuntu Terminal
mkdir ~/lerobot_ws && cd ~/lerobot_ws
git clone [https://github.com/huggingface/lerobot.git](https://github.com/huggingface/lerobot.git)
conda create -n lerobot python=3.10
conda activate lerobot
cd lerobot
pip install -e .
```
## 🧠 Phase 2: Advanced Data Strategy (The 100-Episode Protocol)

To build a "Competition Grade" model, we use **Domain Randomization** during data collection. We do not just repeat the same move 100 times.

### The "25-25-50" Split

**1. Episodes 1-25: The "Golden Path"**
* **Condition:** Perfect lighting, standard start position.
* **Goal:** Teach the robot the ideal motion.
* **Technique:** Slow, smooth, deliberate movements.

**2. Episodes 26-50: Positional Variance**
* **Condition:** Same lighting.
* **Goal:** Spatial generalization.
* **Technique:** Move the target object to the extreme corners of the workspace (Top-left, Bottom-right, etc.).

**3. Episodes 51-100: Environmental Stress (The "FLL" Mode)**
* **Condition:** **Change the lighting.**
    * Turn the lamp OFF.
    * Open/Close the blinds.
    * Cast a shadow over the board with your body.
* **Goal:** Force the AI to ignore pixel brightness and focus on geometry.

### Command for Recording
```bash
python lerobot/scripts/control_robot.py record \
  --robot-path so100 \
  --robot-type so100 \
  --repo-id <USER>/<TASK> \
  --num-episodes 100 \
  --fps 30
Command for Recording:
Bash
```bash
python lerobot/scripts/control_robot.py record \
  --robot-path so100 \
  --robot-type so100 \
  --repo-id <USER>/<TASK> \
  --num-episodes 100 \
  --fps 30
```
🏋️ Phase 3: Training & HyperparametersFor 100 episodes, standard training settings are insufficient. We increase capacity to prevent underfitting.Bashpython lerobot/scripts/train.py \
```bash
python lerobot/scripts/train.py \
  --dataset_repo_id <USER>/<TASK> \
  --policy.type act \
  --env.type so100_real \
  --config_path lerobot/configs/policy/act_so100_real.yaml \
  --device cuda \
  --steps 50000 \
  --batch_size 16 \
  --save_freq 10000 \
  --num_workers 4
```
Explanation of Arguments:
steps 50000: More data requires more training passes (epochs) to converge.
batch_size 16: Stabilizes the gradient descent. (Reduce to 8 if GPU OOM errors occur).
num_workers 4: Speeds up data loading from disk.
🩺 Phase 4: Master Troubleshooting GuideA. 
Setup & Connection Issues
### A. Setup & Connection Issues

| Symptom | Diagnosis | Fix |
| :--- | :--- | :--- |
| `Device not found /dev/ttyUSB0` | WSL Bridge failure | Run `usbipd attach` in PowerShell (Admin). |
| `Permission denied` | User groups | Run `sudo chmod 666 /dev/ttyUSB*`. |
| `Camera index error` | Video device conflict | Unplug camera, run `ls /dev/video*`, replug. Ensure Zoom is closed. |
### B. Robot Physical Behavior

| Symptom | Diagnosis | Fix |
| :--- | :--- | :--- |
| **Violent Shaking/Jitter** | Leader/Follower Conflict | The Leader arm is sending noise. Hold it still or unplug it during playback. |
| **"Drift" (Misses by 1cm)** | Camera Extrinsics | Your camera bumped. You must retrain or physically move the camera back. |
| **Dropping items** | Grip strength | The grippers are slippery. Add electrical tape to the gripper pads for friction. |
### C. AI / Model Failure

| Symptom | Diagnosis | Fix |
| :--- | :--- | :--- |
| **Works at home, fails at school** | Lighting shift | You relied too much on color. Use the "Lamp Protocol" (Phase 0) or train more Shadow data. |
| **Robot stops mid-air** | Out of Distribution | The robot is in a pose it never saw during training. Record 10 episodes starting from that specific pose. |
| **Robot smashes table** | Bad Training Data | You likely smashed the table during recording. Delete those specific episodes and retrain. |
## 🚀 Phase 5: Deployment Checklist (Competition Day)

1.  **Check Hardware:** Tighten all screws on camera mounts.
2.  **Check Software:** Run a dummy inference script to warm up the GPU/CPU cache.
3.  **Lighting Check:**
    * *If bright sun:* Close blinds.
    * *If dim room:* Turn on Rig Lamp.
4.  **Launch Command:**
    ```bash
    python lerobot/scripts/lerobot_eval.py \
      --policy.path outputs/train/act_so100_real/checkpoints/last/pretrained_model \
      --env.type so100_real \
      --device cpu \
      --num-episodes 100
    ```
