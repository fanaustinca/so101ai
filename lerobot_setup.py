"""Utility functions for patching project dependencies."""

import importlib.util
import os
import re
from pathlib import Path


def detect_env():
    """
    Detect the current execution environment and set the 'CONTAINER' environment variable.

    Returns:
        str: 'COLAB', 'VAST', or 'LOCAL'
    """
    # Check for Google Colab
    if importlib.util.find_spec("google") and importlib.util.find_spec("google.colab"):
        env = "COLAB"
        ROOT_DIR = "/content/"
    elif "VAST_CONTAINERLABEL" in os.environ or "VAST_API_KEY" in os.environ:
        env = "VAST"
        ROOT_DIR = "/workspace/"
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

        subprocess.run(["pip", "install", "wandb", "python-dotenv"], check=True)
        print("Successfully installed wandb and python-dotenv.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing lerobot dependencies: {e}")
        return


def cd_lerobot():
    root_dir = Path(os.environ.get("ROOT_DIR"))
    os.chdir(root_dir / "lerobot")


def setup_lerobot_env():
    detect_env()
    install_lerobot()


if __name__ == "__main__":
    setup_lerobot_env()
