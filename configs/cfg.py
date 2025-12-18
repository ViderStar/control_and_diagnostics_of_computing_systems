import os

DEFAULT_VARIANT = int(os.getenv('DEFAULT_VARIANT', '3'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

LAB4_RAM_BITS = int(os.getenv('LAB4_RAM_BITS', str(2 ** 20)))
LAB4_SIM_BITS = int(os.getenv('LAB4_SIM_BITS', '256'))
LAB4_FAULT_SAMPLES = int(os.getenv('LAB4_FAULT_SAMPLES', '32'))

LAB3_POLY = os.getenv('LAB3_POLY', 'x8⊕x6⊕x5⊕x4⊕1')

LAB5_RAM_BITS = int(os.getenv('LAB5_RAM_BITS', str(2 ** 20)))
LAB5_SIM_BITS = int(os.getenv('LAB5_SIM_BITS', '256'))
LAB5_FAULT_SAMPLES = int(os.getenv('LAB5_FAULT_SAMPLES', '32'))


