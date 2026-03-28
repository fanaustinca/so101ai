#!/usr/bin/env python
"""Run lerobot-record with auto-detected hardware and HF/W&B login."""

import argparse
import json
import subprocess
import sys
from datetime import datetime

from lerobot_util import (
    get_arm_ports,
    get_lerobot_camera_index,
    setup_huggingface,
    setup_wandb,
)


def main():
    parser = argparse.ArgumentParser(
        description="Record training data using lerobot-record with SO101 robot arms.",
        epilog="""\
This script auto-detects SO101 leader/follower arm USB ports and camera
indices (Logitech top cam + USB wrist cam), logs into Hugging Face and
Weights & Biases, then launches lerobot-record.

The dataset repo ID is built as: {hf_namespace}/{repo_name}_{YYMMDD}

Examples:
  %(prog)s --repo_name fll_training_lightbox
  %(prog)s --repo_name my_task --hf_namespace myuser --num_episodes 100
  %(prog)s --repo_name my_task --single_task pick_and_place --private
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo_name", required=True, help="Dataset repository name")
    parser.add_argument(
        "--hf_namespace",
        default="fanaustinca",
        help="HF namespace (default: fanaustinca)",
    )
    parser.add_argument(
        "--num_episodes", type=int, default=50, help="Number of episodes (default: 50)"
    )
    parser.add_argument(
        "--single_task",
        default="fll_collection",
        help="Task name (default: fll_collection)",
    )
    parser.add_argument(
        "--no_push_to_hub", action="store_true", help="Disable pushing to hub"
    )
    parser.add_argument("--private", action="store_true", help="Make dataset private")
    args = parser.parse_args()

    # Login to HF and W&B
    setup_huggingface()
    setup_wandb()

    # Auto-detect hardware
    leader_port, follower_port = get_arm_ports()
    top_camera_index, wrist_camera_index = get_lerobot_camera_index()

    # Build dataset repo id with date suffix
    date_suffix = datetime.now().strftime("%y%m%d")
    data_repo = f"{args.hf_namespace}/{args.repo_name}_{date_suffix}"

    camera_config = {
        "wrist": {
            "type": "opencv",
            "index_or_path": wrist_camera_index,
            "width": 640,
            "height": 480,
            "fps": 30,
            "fourcc": "MJPG",
        },
        "top": {
            "type": "opencv",
            "index_or_path": top_camera_index,
            "width": 640,
            "height": 480,
            "fps": 30,
            "fourcc": "MJPG",
        },
    }
    camera_config_str = json.dumps(camera_config, separators=(",", ":"))

    cmd = [
        "lerobot-record",
        "--robot.type=so101_follower",
        f"--robot.port={follower_port}",
        f"--robot.cameras={camera_config_str}",
        "--teleop.type=so101_leader",
        f"--teleop.port={leader_port}",
        f"--dataset.repo_id={data_repo}",
        f"--dataset.num_episodes={args.num_episodes}",
        f"--dataset.single_task={args.single_task}",
        f"--dataset.push_to_hub={str(not args.no_push_to_hub).lower()}",
        f"--dataset.private={str(args.private).lower()}",
    ]

    print(f"Running: {' '.join(cmd)}")
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
