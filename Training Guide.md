# 🧠 Training Guide: SO-101 Robot Arm

![Status](https://img.shields.io/badge/Training-ACT%20Policy-purple)
![Platform](https://img.shields.io/badge/Platform-Nvidia%20or%20Colab-green)

This guide documents how to turn your recorded data (50 episodes) into a working AI brain using the **LeRobot** library.

---

## ✅ Prerequisites

Before you start, ensure you have:
1.  Recorded **50 episodes** of data.
2.  The data is located in `lerobot/data/<YOUR_DATASET_NAME>`.
    * *Example:* `lerobot/data/dad_demo_v1`

---

## ☁️ Option A: Training on Google Colab (Free & Easy)

If your laptop does not have a powerful Nvidia GPU (RTX 3060 or better), **use this method.**

### Step 1: Zip Your Data
In your **Ubuntu Terminal**, navigate to the lerobot folder and zip your dataset.
```bash
cd ~/lerobot_ws/lerobot
```
# Replace 'placeholder' with your actual folder name
```bash
zip -r my_training_data.zip data/placeholder
```
Step 2: Upload to Colab
Open Google Colab.

Create a New Notebook.

Go to Runtime > Change runtime type and select T4 GPU.

Drag and drop your my_training_data.zip file into the file sidebar (left side).

Step 3: Run the Training Code
Copy and paste this entire block into a Colab cell and press Play:

```Python

# 1. SETUP LEROBOT
!git clone [https://github.com/huggingface/lerobot.git](https://github.com/huggingface/lerobot.git)
%cd lerobot
!pip install -e .
!pip install flask

# 2. UNZIP DATA
!unzip -o /content/my_training_data.zip -d /content/lerobot/

# 3. START TRAINING
# Replace 'dad_demo_v1' with your dataset name!
!python lerobot/scripts/train.py \
  --dataset_repo_id dad_demo_v1 \
  --policy.type act \
  --env.type so100_real \
  --config_path lerobot/configs/policy/act_so100_real.yaml \
  --device cuda \
  --steps 20000 \
  --batch_size 8 \
  --save_freq 10000
```
Step 4: Download the Brain
When training finishes (Step 20,000), a folder named outputs will appear in the sidebar.

Navigate to: outputs/train/act_so100_real/checkpoints/last/pretrained_model.

Right-click the pretrained_model folder (or zip it first) and Download it to your laptop.

Place this folder inside your local lerobot/outputs/ folder.

💻 Option B: Training Locally (Nvidia GPU Only)
Use this method only if you have an Nvidia RTX 3060, 4070, or better inside your laptop.

Step 1: Verify GPU
Open your Ubuntu terminal and check if CUDA is visible.

Bash
```bash
nvidia-smi
```
Success: You see a table listing your GPU name.

Fail: If command not found, use Colab (Option A).

Step 2: Run Training Command
Run this command directly in your Ubuntu terminal:

Bash
```bash
python lerobot/scripts/train.py \
  --dataset_repo_id <YOUR_DATASET_NAME> \
  --policy.type act \
  --env.type so100_real \
  --config_path lerobot/configs/policy/act_so100_real.yaml \
  --device cuda \
  --steps 20000 \
  --batch_size 8 \
  --save_freq 10000
```
Note: Change <YOUR_DATASET_NAME> to the name of your folder in data/ (e.g., dad_demo_v1).

🧪 Testing the AI (The "Evaluation")
Once you have the trained model (either downloaded from Colab or trained locally), it's time to test it.

Run the Evaluation Script
Bash
```bash
python lerobot/scripts/lerobot_eval.py \
  --policy.path outputs/train/act_so100_real/checkpoints/last/pretrained_model \
  --env.type so100_real \
  --device cpu \
  --num-episodes 50
```
--device cpu: We use CPU for inference because it's safer for real-world robot control (lower latency spikes), but you can use cuda if you prefer.
