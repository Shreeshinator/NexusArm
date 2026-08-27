> **📖 Docs roadmap:** not sure what to read next? See the [Documentation Roadmap](README.md) — it gives the exact reading order for your goal.

# Camera Bridge — Phone / ESP32 MJPEG → ROS 2

The `camera_bridge` node pulls MJPEG video from a phone (DroidCam / IP Webcam) or an ESP32-CAM over WiFi, and republishes each JPEG frame as a ROS 2 `sensor_msgs/CompressedImage` — **no decoding**, almost no CPU load.

This is needed for: LeRobot data collection (`lerobot-ros2-recorder.py`), ACT policy inference (`lerobot_infer.py`), and Foxglove visualization.

---

## 1. What you need

| Option | How | URL format |
|--------|-----|------------|
| **DroidCam** (recommended) | Install DroidCam from F-Droid or Play Store on your phone; install the `droidcam` Linux driver (one‑liner in the terminal) | `http://<phone-ip>:4747/video` |
| **IP Webcam** | Any Android phone with the "IP Webcam" app (Free version works) | `http://<phone-ip>:8080/video` |
| **ESP32-CAM** | Flash the `cameraWebServer` example; connect to same WiFi | `http://<esp32-ip>:81/stream` |
| **Both** | One `camera_bridge` with both URLs (recommended) — it spawns one thread per camera | `front_url` + `gripper_url` together |

> **One node handles both cameras** — pass both `front_url` and `gripper_url` to a single `camera_bridge` (it spawns `gripper` + `front` threads). Don't run two nodes with the same name — they'd clash.

---

## 2. Quickstart: DroidCam (phone + Linux laptop)

### a. Phone side

1. Install **DroidCam** (from F-Droid or Play Store).
2. Open the app → note the IP address and port (default **4747**).
3. Keep the app running in the foreground; the stream starts immediately.

### b. Linux side

The phone serves `http://<phone-ip>:4747/video` over WiFi — **no driver needed** for `camera_bridge` (it pulls MJPEG directly via HTTP). Just ensure phone + laptop share the same WiFi and use the phone IP shown in the app.

Optional Linux driver (only if you want a `/dev/video*` device for other apps):

```bash
# needs v4l2loopback — only if you need DroidCam as a webcam elsewhere
sudo apt install v4l2loopback-dkms  # then follow DroidCam's own install guide for droidcam
# For camera_bridge you can skip this — use the phone IP directly.
```

### c. Test the stream

```bash
curl -s http://127.0.0.1:4747/video | head -c 200
# Should output MJPEG multipart headers (like "--dcmjpeg...").
```

---

## 3. Quickstart: ESP32-CAM

If you have an ESP32-CAM board:

1. Flash the `cameraWebServer` example (Arduino IDE: `File → Examples → ESP32Camera → WebServer`).
2. Connect the ESP32 to your WiFi network — note its IP address (e.g. `192.168.1.50`).
3. The stream URL is `http://192.168.1.50:81/stream`.

Test it:

```bash
curl -s http://192.168.1.50:81/stream | head -c 200
```

---

## 4. Running the camera_bridge node

The node is installed as `ros2 run robot_arm_hardware camera_bridge`. No ROS 2 params file is strictly required — you can pass params on the command line.

### a. One node, both cameras (front + gripper)

```bash
ros2 run robot_arm_hardware camera_bridge --ros-args \
    -p front_url:=http://192.168.1.51:4747/video \
    -p gripper_url:=http://192.168.1.50:81/stream \
    -p fps:=15.0
```

### b. Front camera only

```bash
ros2 run robot_arm_hardware camera_bridge --ros-args \
    -p front_url:=http://192.168.1.51:4747/video
```

### c. Gripper camera only

```bash
ros2 run robot_arm_hardware camera_bridge --ros-args \
    -p gripper_url:=http://192.168.1.50:81/stream
```

### d. Parameters (all optional, defaults shown)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `front_url` | `""` (disabled) | MJPEG URL for the front camera |
| `gripper_url` | `""` (disabled) | MJPEG URL for the gripper camera |
| `front_topic` | `/front_cam/image_raw/compressed` | ROS topic to publish front frames on |
| `gripper_topic` | `/gripper_cam/image_raw/compressed` | ROS topic to publish gripper frames on |
| `fps` | `15.0` | Max publish rate (the node will drop unchanged frames, so actual rate ≤ this) |

### e. QoS note (critical — images won't arrive otherwise)

The node publishes with `BEST_EFFORT depth=1 KEEP_LAST`. The LeRobot recorder and `lerobot_infer` subscriber both use the same QoS. **If you see "no front image" warnings**, check that both sides use BEST_EFFORT — the default ROS 2 publisher QoS is RELIABLE, which is incompatible and will silently drop all images.

To override the publisher QoS in rare cases, edit `camera_bridge.py:61-65` (the `img_qos` profile) or use `ros2 topic QoS` configuration.

---

## 5. Verifying it works

In a **third terminal** (after sourcing ROS 2 and launching your arm stack):

```bash
# Check front camera is publishing
ros2 topic echo /front_cam/image_raw/compressed --once
# Should show: header, format: jpeg, data=<bytes> (non-empty)

# Check gripper camera
ros2 topic echo /gripper_cam/image_raw/compressed --once

# Measure actual fps
ros2 topic hz /front_cam/image_raw/compressed
# Typical: DroidCam ~15 Hz at 480×640; ESP32 ~5–10 Hz depending on WiFi
```

If topics are empty, check:
* The phone/ESP32 is on the same WiFi as the laptop
* The URL is correct (copy from the phone app, don't type manually)
* `ros2 logger level --filter camera_bridge` — should show "reconnect in 1s" if WiFi hiccup

---

## 6. FPS planning for data collection

| Setup | Camera | Measured `ros2 topic hz` | Use |
|-------|--------|--------------------------|-----|
| **Sim** Gazebo 640×480 | rendered | ~2–5 Hz (CPU-bound) | `camera_bridge` not needed; `--fps 3` for `lerobot-ros2-recorder.py` |
| **Real** DroidCam 480×640 | phone WiFi | ~10–15 Hz (verify first) | `--fps 15` (if you measure ≥15) else lower to measured rate; `camera_bridge fps:=15.0` |
| **Real** ESP32-CAM 320×240 | ESP32 WiFi | ~5–13 Hz | `--fps 10`, `fps:=10` |

> **Rule of thumb:** `recorder --fps` **and** `camera_bridge fps` must be **≤** `ros2 topic hz` you actually measure. Otherwise frames duplicate. When in doubt, lower `--fps`. Sim at 640×480 must stay at `--fps 3`.

---

## 7. Troubleshooting checklist

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `/front_cam/image_raw/compressed` empty | URL wrong or phone not streaming | Verify URL in browser; check phone app is foreground |
| Images arrive but are all black / corrupted | URL doesn't emit MJPEG, or wrong boundary | DroidCam usually works out‑of‑the-box; ESP32 needs correct `cameraWebServer` sketch |
| `topic hz` shows "unknown" / very low (1–2 Hz) | CPU contention (Foxglove, opencode, other ROS 2 nodes) | Close Foxglove/opencode during recording; lower `--fps` |
| `camera_bridge` warns "reconnect in 1s" | WiFi drop, phone moved out of range | Re-position phone/ESP32; use 5 GHz WiFi if possible |
| `lerobot_infer` warns "no image" | QoS mismatch (RELIABLE vs BEST_EFFORT) | Ensure both `camera_bridge` and `lerobot_infer` use BEST_EFFORT (default in this repo) |

---

## 8. Credits

MJPEG passthrough design from the `camera_bridge.py` source — no cv2 decode, forward JPEG bytes untouched. Phone and ESP32 camera support adapted from the LeRobot ecosystem.