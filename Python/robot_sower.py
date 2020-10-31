from robot_sensors import RobotSensors
from robot_xyz_arm import XyzArm
from robot_servo_array import  ServoArrayDriver
from chessboard import  g_chessboard, ChessboardCell, CHESSBOARD_CELL_STATE
from plate import Plate, PlateCell, PLATE_CELL_STATE, PLATE_STATE

from global_const import app_config



class RobotSower():
    '''
    This is the hard robot, will take the plan and execute it.
    '''
    def __init__(self, do_init_marlin=False):
        self.__xyz_arm = XyzArm()
        self.__servos_minghao = ServoArrayDriver()
        self.__servos_minghao.connect_serial_port('/dev/ttyUSB1', 115200, echo_is_on=False)
        self.__sensors = RobotSensors(self.__on_new_plate_enter, self.__on_new_row_enter)
        self.__current_plate = Plate()
        self.__next_plate = Plate()
        if do_init_marlin:
            self.__xyz_arm.connect_to_marlin()
            self.__xyz_arm.init_and_home()
        
    def on_eye_got_new_plate(self, plate_array):
        solution = app_config.robot_arms.servo_controller.solution
        if solution == 'minghao':
            new_map = plate_array
            self.__servos_minghao.send_new_platmap(new_map)
        elif solution == 'xuming':
            plate_map = plate_array
            self.__next_plate.from_map(plate_map)

    def __on_new_plate_enter(self):
        map = self.__next_plate.get_plate_map()
        self.__current_plate.from_map(map)

    def __on_new_row_enter(self):
        g_chessboard.execute_plan()
        g_chessboard_need_a_new_plan = True
        # reload plan from where??
        # g_chessboard.reload_plan()

    def xyz_arm_fill_chessboard(self):
        solution = app_config.robot_arms.servo_controller.solution
        if solution == 'minghao':
            row, col = self.__servos_minghao.get_first_empty_cell()
        elif solution == 'xuming':
            row, col = g_chessboard.get_first_empty_cell()

        if row >= 0:
            # TODO: this is a long time processing, should start a new thread 
            self.__xyz_arm.pickup_from_warehouse()
            self.__xyz_arm.place_to_cell(row, col)
            g_chessboard.set_one_cell(row, col)
        if solution == 'minghao':
            # update map and send new map to Minghao's subsystem
            self.__servos_minghao.inform_minghao(row, col)


    def spin(self):
        self.__servos_minghao.spin()
        self.xyz_arm_fill_chessboard()
        if g_chessboard_need_a_new_plan:    
            g_chessboard.loadplan()
            g_chessboard_need_a_new_plan = False
        