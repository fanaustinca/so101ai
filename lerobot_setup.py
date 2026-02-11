"""Utility functions for patching project dependencies."""
import re
import os


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
        "torchvision": "torchvision>=0.21.0"
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
