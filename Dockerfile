# Uno Q / host container — ROS 2 Jazzy + Gazebo Harmonic + LeRobot
# Runs on x86_64 (dev) and aarch64 (Uno Q) — ros:jazzy is multi-arch.
FROM ros:jazzy

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# System deps + ROS control/Camera bridge deps — verified names for ros:jazzy (Ubuntu 24.04 noble)
# python3-colcon-common-extensions is the correct apt name (not colcon-common-extensions)
# ros-dev-tools exists as meta, keep; v4l2loopback-dkms is optional (no kernel headers on arm64) — try but don't fail build
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv python3-pip python3-serial python3-pytest \
    python3-colcon-common-extensions ros-dev-tools \
    ros-jazzy-xacro ros-jazzy-robot-state-publisher \
    ros-jazzy-joint-state-publisher-gui ros-jazzy-rviz2 \
    ros-jazzy-ros-gz-sim ros-jazzy-ros-gz-bridge \
    ros-jazzy-gz-ros2-control ros-jazzy-controller-manager \
    ros-jazzy-joint-trajectory-controller ros-jazzy-joint-state-broadcaster \
    ros-jazzy-foxglove-bridge ros-jazzy-cv-bridge \
    curl git \
 && (apt-get install -y --no-install-recommends v4l2loopback-dkms || echo "v4l2loopback skip — no headers") \
 && rm -rf /var/lib/apt/lists/*

# Venv with ROS visibility — mirrors repo .venv (AGENTS.md §LeRobot)
RUN python3 -m venv --system-site-packages /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=/opt/venv/bin:$PATH

# Pin setuptools BEFORE lerobot (AGENTS.md:88 — 81 breaks colcon)
RUN /opt/venv/bin/pip install --no-cache-dir "setuptools==79.*"
RUN /opt/venv/bin/pip install --no-cache-dir \
    "lerobot==0.6.1" "numpy==1.26.4" "opencv-python-headless" \
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
