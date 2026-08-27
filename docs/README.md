# NexusArm Documentation Roadmap

> **📍 This file is the index for the whole manual.** If you don't know which doc to open next, you're in the right place. Pick the path that matches what you want to *do*, and follow the numbered steps in order — each step links to the exact file and tells you what you'll get out of it.

---

## 1. The 30-second mental model

NexusArm is one arm, one API, three ways to run it:

```
   intent ──▶ /modular_arm/move_to (MoveTo.srv) ──▶ IK + trajectory ──▶ arm motion
                ▲                                            │
                │         same API in all three worlds:     │
        ┌───────┴────────┬────────────────┬─────────────────┘
     Simulation      Real hardware      Learned ACT policy
     (Gazebo)        (Uno R3 + servos)  (camera → joints)
```

* **Sim** — Gazebo Harmonic, fastest way to see it move. No hardware.
* **Real arm** — 4-DOF printed arm driven by an Arduino Uno R3; same `move_to` service as sim.
* **Learning** — record demos, train an ACT policy, let the arm act on its own from a camera.

Everything below points you at the smallest set of files to read for your goal.

---

## 2. The documentation at a glance

| File | What it covers | Read it if… |
|---|---|---|
| **[`README.md`](../README.md)** (repo root) | Project pitch, architecture, quick-start snippets | You want the 10,000-ft view or a copy-paste quick start. |
| [`docs/01_SETUP.md`](01_SETUP.md) | Install ROS 2 Jazzy + Gazebo, build the workspace, create the LeRobot venv | You're setting up a machine from scratch (laptop or Uno Q prep). |
| [`docs/02_KINEMATICS.md`](02_KINEMATICS.md) | FK/IK math, joint limits, URDF sync rules | You want to understand (or tweak) the geometry. Standalone — skip unless curious. |
| [`docs/03_HARDWARE.md`](03_HARDWARE.md) | Mechanical build + wiring (BOM, perfboard, power) | You're physically building the real arm. |
| [`docs/04_HARDWARE_BRINGUP.md`](04_HARDWARE_BRINGUP.md) | Flash the Uno R3, launch the ROS bridge, MoveTo examples | You've built it and want to wake it up. |
| [`docs/05_DATA_COLLECTION.md`](05_DATA_COLLECTION.md) | Record LeRobot demos with the recorder + teleop | You want to create a training dataset. |
| [`docs/06_INFERENCE.md`](06_INFERENCE.md) | Run a trained ACT policy on the real arm | You have a policy and want the arm to act autonomously. |
| [`docs/07_CAMERA_BRIDGE.md`](07_CAMERA_BRIDGE.md) | Phone/ESP32 MJPEG → ROS 2 (DroidCam setup, QoS, fps) | You need cameras for collection or inference. |
| [`docs/08_TRAINING.md`](08_TRAINING.md) | Train your own ACT policy (free Colab/Kaggle) | You have demos and want to train a policy. |
| [`HARDWARE.md`](../HARDWARE.md) (repo root) | **Uno Q** (Debian + Docker) one-command bringup + full command list | You're deploying on the Arduino Uno Q edge board. |
| [`docs/sim_setup/`](sim_setup/README.md) | Sim-only deep dive: bringup, MoveTo poses, cameras/Foxglove, troubleshooting, teleop | You only care about the simulation. |

> **Two top-level files (`README.md`, `HARDWARE.md`) live at the repo root; everything else is in `docs/`.** `SETUP.md` at the root is now just a redirect to `docs/01_SETUP.md`.

---

## 3. Pick your path

Follow the steps **in order**. Each builds on the previous. Where a step is optional, it's marked *(optional)*.

### 🅐 Path A — "I just want the simulation, no hardware"
1. [`README.md`](../README.md) → skim "Quick start — simulation" for the 30-second version.
2. [`docs/sim_setup/README.md`](sim_setup/README.md) → one-command sim + verify. **This is your main sim doc.**
3. [`docs/sim_setup/01_sim_bringup.md`](sim_setup/01_sim_bringup.md) → RViz check, headless tuning, timing.
4. [`docs/sim_setup/02_move_to_api.md`](sim_setup/02_move_to_api.md) → more poses, pitch/elbow semantics.
5. [`docs/sim_setup/03_cameras_and_foxglove.md`](sim_setup/03_cameras_and_foxglove.md) → cameras empty? Foxglove setup?
6. [`docs/sim_setup/04_troubleshooting_sim.md`](sim_setup/04_troubleshooting_sim.md) → anything fails (kill sequence, SHM locks, DDS trap).
7. *(optional)* [`docs/sim_setup/05_teleop.md`](sim_setup/05_teleop.md) → leader-arm pots → sim arm.
8. *(optional)* [`docs/02_KINEMATICS.md`](02_KINEMATICS.md) → understand the math.

### 🅑 Path B — "I want to build and run the REAL arm (native laptop)"
1. [`README.md`](../README.md) → "Quick start — real hardware".
2. [`docs/01_SETUP.md`](01_SETUP.md) → install deps, `colcon build`, create the venv.
3. [`docs/03_HARDWARE.md`](03_HARDWARE.md) → print + assemble + wire the arm.
4. [`docs/04_HARDWARE_BRINGUP.md`](04_HARDWARE_BRINGUP.md) → flash Uno R3, launch `real_arm.launch.py`, MoveTo calls.
5. [`docs/07_CAMERA_BRIDGE.md`](07_CAMERA_BRIDGE.md) → add phone/ESP32 cameras (needed for collection/inference).
6. *(then)* continue to Path C or D if you want learning.

### 🅒 Path C — "I have a real arm and want to TEACH it (collect → train → infer)"
Do Path B first (the arm must be alive). Then:
1. [`docs/07_CAMERA_BRIDGE.md`](07_CAMERA_BRIDGE.md) → cameras must stream before recording.
2. [`docs/05_DATA_COLLECTION.md`](05_DATA_COLLECTION.md) → record 50–100 clean demos.
3. [`docs/08_TRAINING.md`](08_TRAINING.md) → train ACT on Colab/Kaggle (free GPU).
4. [`docs/06_INFERENCE.md`](06_INFERENCE.md) → deploy the policy; dry-run first, then live.

### 🅓 Path D — "I'm deploying on the Arduino Uno Q (edge board, Debian + Docker)"
> **The Uno Q's own OS is Debian 13 (Trixie) — not Ubuntu.** ROS runs *inside* an Ubuntu-based Docker image on it. Don't follow the native-apt steps from Path B on the board itself; use the Docker path below.

1. [`README.md`](../README.md) → "Quick start — real hardware" (for context only).
2. [`docs/01_SETUP.md`](01_SETUP.md) → skim §1–§3 just to know the stack; **do not** run the native Ubuntu apt steps on the Uno Q.
3. [`HARDWARE.md`](../HARDWARE.md) → **this is your main Uno Q doc.** VS Code SSH → clone → fix disk → pull image → 3-terminal bringup → full command list. Reuse Paths B/C concepts *inside* the container.

### 🅔 Path E — "I want to understand the math only"
* [`docs/02_KINEMATICS.md`](02_KINEMATICS.md) → standalone, no hardware or ROS needed.

---

## 4. How the learning pipeline connects (C in one picture)

```
build arm (03) → bringup (04) → cameras (07)
                                      │
                                      ▼
   demos ──record──▶ 05_DATA_COLLECTION ──▶ HF dataset
                                      │
                                      ▼
   dataset ──train──▶ 08_TRAINING ──▶ HF policy
                                      │
                                      ▼
   policy ──deploy──▶ 06_INFERENCE ──▶ autonomous arm
```

`05 → 08 → 06` is the loop. `03/04/07` are the one-time hardware setup that feeds into it.

---

## 5. OS note — Ubuntu vs Debian (read this once)

* **Your dev laptop:** **Ubuntu 24.04** (Noble). `docs/01_SETUP.md` §2–§3 installs ROS 2 Jazzy via `apt` for this.
* **Arduino Uno Q (the edge board):** its onboard OS is **Debian 13 (Trixie) `aarch64`** — **not Ubuntu**. We run the whole ROS stack *inside* the `shreeshinator/nexusarm:unoq` Docker image (which is Ubuntu-based) on the Uno Q, so the OS difference doesn't matter for ROS. **Do not run the native `apt install ros-jazzy-*` steps on the Uno Q itself** — use the Docker path in `HARDWARE.md`.
* The Docker *image* being Ubuntu-based is correct and intentional (it's `FROM ros:jazzy-ros-base`).

---

## 6. Stuck? Where to look

| Symptom | Go to |
|---|---|
| Sim won't start / empty controllers | `docs/sim_setup/04_troubleshooting_sim.md` |
| Arm doesn't move (native) | `docs/04_HARDWARE_BRINGUP.md` §7 |
| Camera topics empty | `docs/07_CAMERA_BRIDGE.md` §5–§7 |
| Recorder / dataset issues | `docs/05_DATA_COLLECTION.md` (troubleshooting + resume) |
| Policy won't pick | `docs/06_INFERENCE.md` §5 |
| Uno Q SSH / disk / Docker errors | `HARDWARE.md` (Troubleshooting + FULL COMMAND LIST) |
| `Illegal instruction` / `av` errors on Uno Q | `HARDWARE.md` Step 5–6 (torch/av live fixes) |

---

*Last updated alongside the docs restructuring. Every other file links back here — if a link is broken, start from this roadmap.*
