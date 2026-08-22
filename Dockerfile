# Uno Q / host container — ROS 2 Jazzy + LeRobot (SLIM for 16GB eMMC)
# Slimmed for Uno Q Debian overlay: ros:jazzy-ros-base (not full ros:jazzy desktop = +2GB GUI+Qt)
# Runs on x86_64 (dev) and aarch64 (Uno Q) — multi-arch. Simulation (Gazebo/RViz) is NOT included here — run sim on laptop/WSL natively.
FROM ros:jazzy-ros-base

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# Minimal apt: ONLY real-arm needs. Each extra ros-jazzy-* drags 100s MB + fills /var/lib/docker/overlay2 on 16GB eMMC.
# - ros-dev-tools alone pulls mercurial+subversion+bloom+PyQt5+opencv (your 260MB failure) — DO NOT install on Uno Q.
# - rivz2 / joint-state-publisher-gui / ros-gz-sim / gz-ros2-control / foxglove are SIM/GUI — not needed for hw_interface + camera_bridge.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv python3-pip python3-serial \
    python3-colcon-common-extensions \
    ros-jazzy-xacro ros-jazzy-robot-state-publisher \
    ros-jazzy-controller-manager ros-jazzy-joint-trajectory-controller ros-jazzy-joint-state-broadcaster \
    ros-jazzy-ros2-control ros-jazzy-ros2-controllers \
    ros-jazzy-cv-bridge \
    curl git \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

# Venv with ROS visibility — mirrors repo .venv (AGENTS.md §LeRobot), keep pip cache off to save overlay
RUN python3 -m venv --system-site-packages /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=/opt/venv/bin:$PATH

# Pin setuptools BEFORE lerobot (AGENTS.md:88 — 81 breaks colcon)
RUN /opt/venv/bin/pip install --no-cache-dir "setuptools==79.*"
# lerobot 0.6.1 requires numpy>=2.0,<2.3 (your log: Cannot install lerobot==0.6.1 and numpy==1.26.4)
# Let lerobot pull numpy 2.1.x + opencv 5.0 aarch64 (manylinux_2_28_aarch64) — DO NOT pin 1.26.4
RUN /opt/venv/bin/pip install --no-cache-dir \
    "lerobot==0.6.1" "opencv-python-headless" \
    h5py datasets
# CPU torch by default (Uno Q / dev laptop without CUDA); override at compose if needed
RUN /opt/venv/bin/pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu

WORKDIR /workspace
# Copy source last for cache hits
COPY src/ ./src/
COPY lerobot-ros2-recorder.py ./

# Build workspace (symlink-install so Python edits apply without rebuild)
RUN source /opt/ros/jazzy/setup.bash && \
    colcon build --symlink-install

# Entrypoint: source ROS + venv on every run
RUN echo 'source /opt/ros/jazzy/setup.bash' >> /ros_entrypoint.sh && \
    echo 'source /workspace/install/setup.bash' >> /ros_entrypoint.sh && \
    echo 'source /opt/venv/bin/activate' >> /ros_entrypoint.sh && \
    echo 'exec "$@"' >> /ros_entrypoint.sh && chmod +x /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
