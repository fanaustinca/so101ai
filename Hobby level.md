# 🧠 SO-101 AI Project: The "Centurion" (100 Episodes)

![Status](https://img.shields.io/badge/Dataset-100%20Episodes-green)
![Difficulty](https://img.shields.io/badge/Level-Intermediate-yellow)
![Model](https://img.shields.io/badge/Architecture-ACT-purple)

This repository tracks the development of a robust manipulation policy for the **SO-101 Robot Arm**. Unlike simple 50-episode demos, this 100-episode dataset aims to solve tasks with high reliability and resistance to lighting changes.

---

## 📋 The "Golden Rules" of Data Collection

**Read this before you record a single frame.** The AI is only as smart as your hands. If you move poorly, the robot will learn to move poorly.

### 1. The "Bell Curve" Motion
Do not move jerkily. Your hand speed should look like a bell curve:
* **Start:** Slow acceleration.
* **Middle:** Fast (but controlled) travel.
* **End:** Slow deceleration to a stop.
* *Why?* Sudden stops confuse the AI and cause "jitter" during playback.

### 2. The "Intentional Pause"
The AI needs time to "think" (process the image) before acting.
* **Rule:** Before grabbing the object, hover your gripper around it for **0.5 seconds**.
* **Rule:** After grabbing, wait **0.5 seconds** before lifting.
* *Why?* This creates clear "key frames" in the data that link the image (Seeing the block) to the action (Closing the gripper).

### 3. Domain Randomization (The Secret Sauce)
You are recording 100 episodes. Do not do the exact same thing 100 times.
* **Episodes 1-50 (Standard):** Randomize the **Object Position** only. Move the block left, right, close, far.
* **Episodes 51-75 (Distractors):** Add a "dummy" object (like a coffee mug) to the edge of the table that you *don't* touch.
* **Episodes 76-100 (Lighting):** Change the lighting. Turn the lamp off. Open the blinds. Cast a shadow with your body.
* *Result:* An AI that works even when the environment is messy.

---

## 🎥 Step 1: Data Collection

**Time Estimate:** 1 - 1.5 Hours (Don't rush it).

### The Command
Run this in your Ubuntu terminal. Replace `task_name` with something descriptive (e.g., `place_red_cube`).

```bash
python lerobot/scripts/control_robot.py record \
  --robot-path so100 \
  --robot-type so100 \
  --repo-id <YOUR_USER>/<TASK_NAME> \
  --num-episodes 100 \
  --warmup-time-s 5 \
  --episode-time-s 15
```
The Routine
Reset: Place the robot and object in start positions.

Hands Off: Get your hands out of the camera view.

Listen: Wait for the "Go" signal from the computer.

Act: Perform the task using the Golden Rules.

Finish: Return robot to a neutral "safe" pose.

Loop: The system will automatically save and start the next episode.

⚠️ Mistake Recovery: If you drop the block or crash during an episode:

Finish the episode anyway.

Note the Episode ID (e.g., Episode 42).

After recording, go into the lerobot/data folder and delete that specific episode file.

Never train on bad data.

🏋️ Step 2: Training (The Crunch)
With 100 episodes, training takes longer. Use a GPU (Nvidia RTX 3060+) or Google Colab.

Hyperparameters for 100 Episodes
We increase the batch_size and steps slightly to accommodate more data.

Command:

Bash
```bash
python lerobot/scripts/train.py \
  --dataset_repo_id <YOUR_USER>/<TASK_NAME> \
  --policy.type act \
  --env.type so100_real \
  --config_path lerobot/configs/policy/act_so100_real.yaml \
  --device cuda \
  --steps 40000 \
  --batch_size 16 \
  --save_freq 10000
```
Changes:

--steps 40000: We double the training time so it sees all 100 episodes enough times.

--batch_size 16: (If your GPU allows) Helping the AI generalize better. If you run out of memory, go back to 8.

🧪 Step 3: Evaluation & Debugging
Run the trained policy:

Bash
```bash
python lerobot/scripts/lerobot_eval.py \
  --policy.path outputs/train/act_so100_real/checkpoints/last/pretrained_model \
  --env.type so100_real \
  --num-episodes 10
```
🩺 Debug Playbook
1. The "Zombie Arm" (Robot stops moving mid-air)

Diagnosis: The AI is uncertain. It has reached a state it has never seen before.

Fix: You likely didn't record enough data in that specific area of the table. Record 10 more episodes focused only on that area.

2. The "Smash & Grab" (Robot hits the table hard)

Diagnosis: In your training data, you probably smashed the table a few times. The AI learned that aggression.

Fix: Use the Yoga Mat to cushion mistakes, but aim for a "Soft Touch" in future recordings.

3. The "Drift" (Robot moves correct direction but misses by 1cm)

Diagnosis: Camera calibration shift.

Fix: Did you bump the camera stand?

Option A: Move the camera slightly to match the old view.

Option B (Better): Retrain from scratch (the 100 episodes are fine, but the new reality doesn't match the old data).

4. The "loop" (Robot hovers over the block forever)

Diagnosis: You hesitated too much during recording.

Fix: Be decisive. When you reach for the block, grab it. Do not second guess your movements during data collection.
