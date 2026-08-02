import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/shreeshinator/AI_Challenge_Robotic_Arm/install/modular_arm_kinematics'
