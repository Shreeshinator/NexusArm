from setuptools import find_packages, setup
import os
from glob import glob

package_name = "modular_arm_teleop"

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
        (
            os.path.join("share", package_name, "config"),
            glob(os.path.join("config", "*.yaml")),
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="user",
    maintainer_email="user@example.com",
    description="Teleoperation node for the modular arm via Arduino leader arm.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "teleop_node = modular_arm_teleop.teleop_node:main",
        ],
    },
)
