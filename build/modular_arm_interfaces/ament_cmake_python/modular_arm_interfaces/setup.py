from setuptools import find_packages
from setuptools import setup

setup(
    name='modular_arm_interfaces',
    version='0.1.0',
    packages=find_packages(
        include=('modular_arm_interfaces', 'modular_arm_interfaces.*')),
)
