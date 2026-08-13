from setuptools import find_packages, setup
import os
from glob import glob

package_name = "robot_arm_hardware"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (
            os.path.join("share", package_name, "launch"),
            glob(os.path.join("launch", "*launch.[pxy]*")),
        ),
        # Install executables into lib/<pkg>/ so `ros2 run` discovers them
        # (this setuptools/ament_python combo otherwise drops them in bin/).
        (os.path.join("lib", package_name), [
            "scripts/hw_interface",
            "scripts/joint_keyboard_teleop",
            "scripts/hw_move_to",
            "scripts/keyboard_teleop",
        ]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="user",
    maintainer_email="user@example.com",
    description="Real-robot hardware interface bridging /joint_command to an Arduino servo bridge.",
    license="MIT",
)
