import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/qasob/tic_tac_toe_playing_robot/install/robot_move'
