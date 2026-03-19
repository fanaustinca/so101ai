#!/usr/bin/env python
"""Run lerobot-teleoperate with auto-detected arm ports and cameras."""

import json
import subprocess
import sys

from lerobot_util import get_arm_ports, get_lerobot_camera_index

leader_port, follower_port = get_arm_ports()
top_camera_index, wrist_camera_index = get_lerobot_camera_index()

camera_config = {
    "wrist": {
        "type": "opencv",
        "index_or_path": wrist_camera_index,
        "width": 640,
        "height": 480,
        "fps": 30,
    },
    "top": {
        "type": "opencv",
        "index_or_path": top_camera_index,
        "width": 640,
        "height": 480,
        "fps": 30,
    },
}

camera_config_str = json.dumps(camera_config, separators=(",", ":"))

cmd = [
    "lerobot-teleoperate",
    "--robot.type=so101_follower",
    f"--robot.port={follower_port}",
    "--teleop.type=so101_leader",
    f"--teleop.port={leader_port}",
    f"--robot.cameras={camera_config_str}",
    "--display_data=true",
]

print("Running:", " ".join(cmd))
sys.exit(subprocess.call(cmd))
