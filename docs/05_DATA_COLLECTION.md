# Data Collection — Record Demos for Learning

> Let's collect some good demos! This is the friendly walkthrough for the LeRobot recorder — the same tool that made `shreeshinator/arm-picking-blocks-real` (front cam 480×640 @15Hz, 5 joints).

**Reference you can keep open:** `lerobot_custom_hardware.md` is the upstream LeRobot tutorial — handy background, but this page is the exact commands for *this* arm.

## What you get

A **LeRobotDataset v3** with:

* `observation.state` — 5 floats from `/joint_states` (`joint1..joint4, gripper_joint`)
* `action` — 5 floats from `/joint_command` (`Float64MultiArray`, what `hw_move_to` published)
* `observation.images.front` — front camera video
* `observation.images.gripper` — gripper camera video (optional)
* `task` — your text prompt, e.g. `"place the block in the bowl"`

The recorder samples on a **fixed clock (`--fps`)**, not on every message — so `fps` must be **≤ your slowest camera's real rate** or frames will just duplicate.

## Prerequisites — quick & friendly

* Arm built and flashed (`03_HARDWARE.md` + `04_HARDWARE_BRINGUP.md`), ZK-4XX ~6V
* ROS built: `source /opt/ros/jazzy/setup.bash && source install/setup.bash`
* Venv ready — create if missing (see `01_SETUP.md` §4): `.venv` with `include-system-site-packages=true`, `lerobot==0.6.1`, `numpy==1.26.4`, `opencv-python-headless` only, `h5py`, `torch` CPU, `setuptools==79.*`
  * Use it as `.venv/bin/python` — don't `pip install lerobot` globally
* Cameras via `camera_bridge` — **see `07_CAMERA_BRIDGE.md` for full DroidCam / ESP32 setup**:
  ```bash
  # Phone via DroidCam at http://<PHONE_IP>:4747/video, or ESP32 at http://<ESP32_IP>:81/stream (or both)
  ros2 run robot_arm_hardware camera_bridge --ros-args \
    -p front_url:=http://<PHONE_IP>:4747/video \
    -p gripper_url:="" \
    -p fps:=15.0
  ```
  Topics are `CompressedImage` on `/front_cam/image_raw/compressed` and `/gripper_cam/image_raw/compressed` (passthrough JPEG, `BEST_EFFORT depth=1`). Verify first: `ros2 topic hz /front_cam/image_raw/compressed` before choosing `--fps` (see `07_CAMERA_BRIDGE.md` §5-6 for fps planning).

## Bring up the real arm first (3-terminal checklist)

```bash
# Terminal 1 — arm + MoveTo service
ros2 launch robot_arm_hardware real_arm.launch.py serial_port:=/dev/ttyACM0 baud_rate:=115200
# Terminal 2 — cameras (see 07_CAMERA_BRIDGE.md for phone/ESP32 IPs)
ros2 run robot_arm_hardware camera_bridge --ros-args -p front_url:=http://<PHONE_IP>:4747/video -p fps:=15.0
# Terminal 3 — teleop that drives MoveTo (keep this focused):
ros2 run robot_arm_hardware keyboard_teleop
# controls: w/a/s/d X/Y coarse, i/j/k/l X/Y fine, q/e Z, u/o Z fine, r/f pitch, [ ] wrist, space gripper, x print, ENTER/d/q for recorder if in same terminal, Ctrl-C quit
# START pose is 0.27,0,0.08,-1.57 (grasp height)
```

## Record — one command

```bash
source /opt/ros/jazzy/setup.bash
# login once if you plan to push: huggingface-cli login
# pre-check cameras are alive: ros2 topic hz /front_cam/image_raw/compressed  (should be ~10-15 Hz on real phone)

.venv/bin/python lerobot-ros2-recorder.py \
  --repo-id your-hf-username/your-dataset \
  --task "place the block in the bowl" \
  --fps 15 \
  --front-cam-topic /front_cam/image_raw/compressed \
  --gripper-cam-topic /gripper_cam/image_raw/compressed \
  --cams front \
  --joint-states-topic /joint_states \
  --joint-commands-topic /joint_command \
  --joint-commands-type float64 \
  --compressed
# tip: if gripper cam isn't connected, use --cams front (as above) so it doesn't wait forever
# sim: add --joint-commands-topic /joint_commands --joint-commands-type joint --fps 3  (sim cameras ~2-5 Hz at 640×480)
```

What to watch for: `Waiting for messages on: ...` then `Dataset created at ... front cam (480,640,3) ... 5 joints. Press ENTER to start`.

## Control episodes (pick your style)

**Topic (recommended — works headless, great for scripting):**
```bash
ros2 topic pub --once /lerobot_recorder/command std_msgs/String "{data: start}"   # start
ros2 topic pub --once /lerobot_recorder/command std_msgs/String "{data: save}"    # save episode
ros2 topic pub --once /lerobot_recorder/command std_msgs/String "{data: discard}" # drop it
ros2 topic pub --once /lerobot_recorder/command std_msgs/String "{data: finish}"  # finalize + push if --push
```

**Keyboard (must be in the *same* terminal as the recorder, TTY open):**
* `ENTER` = start new episode (or save if already recording)
* `d` then `ENTER` = discard without saving
* `q` then `ENTER` = finish completely

Every `save` writes an episode; `finish` calls `finalize()` (required in v3 — otherwise parquet is corrupt) and `push_to_hub()` if you passed `--push`.

## Real-world tips that save you time

* **fps:** At 640×480 the Gazebo sim does ~2-5Hz, real DroidCam does ~15Hz. Keep recorder `fps` at or below what you measure with `ros2 topic hz /front_cam/image_raw/compressed`. For sim at 640×480 use `--fps 3`, real at 480×640 use `--fps 15`.
* **Sim vs real action topics:** Sim teleop publishes `/joint_commands` (plural, `JointState`) — you need `--joint-commands-type joint --joint-commands-topic /joint_commands`. Real arm publishes `/joint_command` (singular, `Float64MultiArray`) — use `float64` as above. If you have no command topic, add `--action-fallback state`.
* **QoS:** Camera topics are `BEST_EFFORT depth=1` — recorder already uses that (`lerobot-ros2-recorder.py:148`). Don't switch to RELIABLE or images won't arrive.
* **Storage:** videos encode in background; a few hundred episodes at 640×480 are just a few GB. Local root defaults to `~/.cache/huggingface/lerobot/<repo-id>` (override with `--root`).
* **Push:** `huggingface-cli login` once, then `--push` (add `--private` if you want it hidden).

## Verify your dataset

```python
from lerobot.datasets.lerobot_dataset import LeRobotDataset
ds = LeRobotDataset("your-hf-username/your-dataset")
print(ds.meta.info)                 # schema, fps, episodes
print(ds.num_episodes, ds.num_frames)
print(ds[0]["observation.state"], ds[0]["action"])
print(ds[0]["observation.images.front"].shape)  # should be (3, 480, 640)
```

Or paste your `repo_id` into https://huggingface.co/spaces/lerobot/visualize_dataset once pushed.

## Resume — add more episodes later (friendly!)

Crashed, closed the terminal, or just want more demos tomorrow? Just run **the same command** again with the **same `--repo-id` and `--root`** (if you used one). The recorder uses `LeRobotDataset.create(...)` — if a dataset already exists at `~/.cache/huggingface/lerobot/<repo-id>` (or your `--root`), it **loads and appends** instead of overwriting:

```bash
# Exact same repo-id as before — new episodes append after the old ones
.venv/bin/python lerobot-ros2-recorder.py \
  --repo-id your-hf-username/your-dataset \
  --task "place the block in the bowl" \
  --fps 15 --cams front --compressed \
  --front-cam-topic /front_cam/image_raw/compressed \
  --joint-states-topic /joint_states \
  --joint-commands-topic /joint_command --joint-commands-type float64
# keep teleop + camera_bridge running, then start/save/finish as usual
```

Tips:
* Always `finish` cleanly — it calls `dataset.finalize()` (closes parquet/video writers). If you `Ctrl-C` mid-episode, that episode's buffer is discarded but previously `save`d episodes are safe.
* Want to keep collecting after a `finish`? Just run the same command again — it will report `Resuming dataset ... n episodes already`.
* If you used a custom `--root /path/to/my_data`, you **must** pass the same `--root` on resume or it will create a new dataset at the default cache path.
* To inspect after resume: `from lerobot.datasets.lerobot_dataset import LeRobotDataset; ds = LeRobotDataset("your-hf-username/your-dataset"); print(ds.num_episodes)`.

> **Training resume is separate** — see `08_TRAINING.md` §5 for resuming `lerobot-train` checkpoints.

## Troubleshooting — friendly

* `data is stale 0.7s old` → camera didn't publish fast enough. Lower `--fps` or check `camera_bridge` logs (reconnects every 1s on WiFi hiccup).
* `No --joint-names given; locked joint order` → fine on first run, but pass `--joint-names joint1 joint2 joint3 joint4 gripper_joint` to be explicit next time.
* `action==state` warning in `lerobot_infer` later → you recorded without a real command topic. For imitation, `action` should be the *commanded* target — add the `--joint-commands-topic` correctly or post-shift `action[t]=state[t+1]`.
* `Dataset already exists` but 0 episodes shown → you forgot `--root` on resume, or changed `--fps`/`--cams` mid-dataset (resolution/fps must stay constant for a given repo-id — start a new `repo-id` if you change them).

Happy collecting — a handful of clean demos beats dozens of messy ones! When you have 50–100 clean episodes, head to `08_TRAINING.md` to train your own ACT policy for free on Colab/Kaggle.
