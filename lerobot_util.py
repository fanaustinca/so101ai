"""Utility functions for patching project dependencies."""

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from IPython.display import Markdown, display


def detect_env():
    """
    Detect the current execution environment and set the 'CONTAINER' environment variable.

    Returns:
        str: 'COLAB', 'VAST', or 'LOCAL'
    """
    # Check for Google Colab
    if importlib.util.find_spec("google") and importlib.util.find_spec("google.colab"):
        env = "COLAB"
        ROOT_DIR = "/content/so101ai"
    elif "VAST_CONTAINERLABEL" in os.environ or "VAST_API_KEY" in os.environ:
        env = "VAST"
        ROOT_DIR = "/workspace/so101ai"
    else:
        env = "LOCAL"
        # Set ROOT_DIR to the parent directory of this file
        # User requested one level up, so: dirname(dirname(abspath(__file__)))
        ROOT_DIR = os.getcwd()

    os.environ["CONTAINER"] = env
    os.environ["ROOT_DIR"] = ROOT_DIR
    return env


def patch_pyproject(file_path="pyproject.toml"):
    """
    Patch pyproject.toml to update PyTorch and related packages to newer versions.

    This function updates torch, torchcodec, and torchvision dependencies to versions
    that support latest Nvidia GPU and CUDA, replacing legacy constraints.

    Args:
        file_path (str): Path to the pyproject.toml file. Defaults to "pyproject.toml"
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "r") as f:
        lines = f.readlines()

    # Define the exact new strings you want inside the first set of quotes
    updates = {
        "torch": "torch>=2.2.1",
        "torchcodec": "torchcodec>=0.2.1",
        "torchvision": "torchvision>=0.21.0",
    }

    new_lines = []
    for line in lines:
        patched_line = line
        for package, new_full_string in updates.items():
            # This regex looks for the package name inside quotes and replaces
            # EVERYTHING inside those specific quotes up to the first ';' or the end quote.
            # It handles multiple comma-separated constraints by wiping them out.
            pattern = rf'"{package}[^a-zA-Z].*'
            replacement = f'"{new_full_string}",'
            patched_line = re.sub(pattern, replacement, patched_line)
        new_lines.append(patched_line)

    with open(file_path, "w") as f:
        f.writelines(new_lines)

    print("Cleanly patched pyproject.toml and removed legacy constraints.")


def install_lerobot():
    """Clones the LeRobot repository."""
    # Retrieve ROOT_DIR from environment (set by detect_env)
    root_dir = os.environ.get("ROOT_DIR")
    if not root_dir:
        print("ROOT_DIR not set. Please run detect_env() first.")
        return

    # 1. cd ROOT_DIR
    try:
        os.chdir(root_dir)
        print(f"Changed directory to {root_dir}")
    except FileNotFoundError:
        print(f"Error: ROOT_DIR {root_dir} does not exist.")
        return

    # 2. git clone https://github.com/huggingface/lerobot.git
    if os.path.exists("lerobot"):
        print("lerobot repository already exists.")
    else:
        print("Cloning lerobot repository...")
        import subprocess

        try:
            subprocess.run(
                ["git", "clone", "https://github.com/huggingface/lerobot.git"],
                check=True,
            )
            print("Successfully cloned lerobot.")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning lerobot: {e}")
            return

    # 3. cd lerobot
    try:
        os.chdir("lerobot")
        print("Changed directory to lerobot")
    except FileNotFoundError:
        print("Error: lerobot directory not found after clone.")

    # 4. Patch pyproject.toml to avoid package version conflicts
    patch_pyproject(file_path="pyproject.toml")

    # 5. pip install all dependencies
    print("Installing lerobot dependencies...")
    import subprocess

    try:
        subprocess.run(["pip", "install", "-e", "."], check=True)
        print("Successfully installed lerobot dependencies.")

        subprocess.run(
            ["pip", "install", "feetech-servo-sdk"],
            check=True,
        )
        print("Successfully installed feetech-servo-sdk.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing lerobot dependencies: {e}")
        return


def get_secret(key_name):
    # 1. Try Google Colab userdata (Secret Manager)
    if "google.colab" in sys.modules:
        try:
            from google.colab import userdata

            return userdata.get(key_name)
        except Exception:
            pass  # Fallback if secret not found in Colab

    # 2. Try Local/WSL .env file
    load_dotenv(override=True)

    # 3. Fallback to standard environment variable (os.environ)
    return os.getenv(key_name)


def setup_huggingface():
    """Sets up Hugging Face environment."""
    HF_TOKEN = get_secret("HF_TOKEN")
    # Apply to environment so libraries find them automatically
    if HF_TOKEN:
        # HUGGINGFACE env
        os.environ["HF_TOKEN"] = HF_TOKEN
        from huggingface_hub import login

        login(token=HF_TOKEN)
        print("login to hf")
    else:
        print("login to hf failed")


def setup_wandb():
    WANDB_API_KEY = get_secret("WANDB_API_KEY")

    if WANDB_API_KEY:
        os.environ["WANDB_API_KEY"] = WANDB_API_KEY
        os.environ["WANDB_NOTEBOOK_NAME"] = "train_so101_model.ipynb"
        # WANDB env
        import wandb

        wandb.login()
        print("login to wandb")
    else:
        print("login to wandb failed")


def cd_lerobot():
    root_dir = Path(os.environ.get("ROOT_DIR"))
    return os.chdir(root_dir / "lerobot")


def setup_lerobot_env():
    detect_env()
    install_lerobot()
    setup_huggingface()
    setup_wandb()
    cd_lerobot()


def print_shell_md(title: str, command: str, *args: str):
    """
    Displays a markdown block with a title and a shell command.

    The command is built from the `command` argument and any additional `args` provided.

    Args:
        title (str): The title to display above the command.
        command (str): The base command or first part of the command (e.g., 'python').
        *args (str): Zero or more additional parts of the command, which will be
            space-separated.
    """
    md_text = f"""
## {title}
### Copy-Paste Command
```bash
{command} {" ".join(args)}
```
"""
    display(Markdown(md_text))


def get_camera_mapping():
    print("Scanning hardware indices...")
    mapping = {}
    try:
        # Using the standard subprocess module
        output = subprocess.run(
            ["v4l2-ctl", "--list-devices"], capture_output=True, text=True
        ).stdout
        print("Raw v4l2-ctl output:")
        print(output)
        parts = output.split("\n\n")
        for part in parts:
            lines = part.strip().split("\n")
            if lines:
                name = lines[0].strip()
                indices = re.findall(r"/dev/video(\d+)", part)
                if indices:
                    # Pick the first (lowest/even) index
                    mapping[name] = int(indices[0])
    except FileNotFoundError:
        print("Error: v4l2-ctl not found. Run 'sudo apt install v4l-utils' first.")
    return mapping


def get_lerobot_camera_index():
    top_cam_keyword = "Logitech Webcam"
    wrist_cam_keyword = "USB2.0_CAM1"

    mapping = get_camera_mapping()
    print("Camera Mapping:", mapping)
    for name, index in mapping.items():
        if top_cam_keyword in name:
            top_cam_index = index
        elif wrist_cam_keyword in name:
            wrist_cam_index = index

    return top_cam_index, wrist_cam_index


if __name__ == "__main__":
    setup_lerobot_env()
