import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/fbot/Área de Trabalho/IMU_WS/install/imu_package'
