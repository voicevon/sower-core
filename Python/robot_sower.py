from robot_sensors import RobotSensors
from robot_xyz_arm import XyzArm
from robot_servo_array import ServoArrayDriver
from chessboard import  Chessboard, ChessboardCell, CHESSBOARD_CELL_STATE
from plate import Plate, PlateCell, PLATE_CELL_STATE, PLATE_STATE

from global_const import app_config



class RobotSower():
    '''
    This is the hard robot, will take the plan and execute it.
    '''
    def __init__(self, mqtt):
        self.__xyz_arm = XyzArm()
        self.__servos_minghao = ServoArrayDriver()
        self.__sensors = RobotSensors(self.__on_new_plate_enter, self.__on_new_row_enter)
        self.__current_plate = Plate()
        self.__next_plate = Plate()
        self.__chessboard = Chessboard()
        # self.__servos.setup(self.__xyz_arm.pickup_then_place_to_cell)
        self.__xyz_arm.setup(mqtt, None)
        self.__xyz_arm.connect_to_marlin()
        self.__xyz_arm.Init_Marlin()
        self.__xyz_arm.init_and_home()
    
    def get_chessboard(self):
        return self.__chessboard

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
        self.__chessboard.execute_plan()
        self.__chessboard_need_a_new_plan = True
        # reload plan from where??
        # self.__chessboard.reload_plan()

    def xyz_arm_fill_chessboard(self):
        solution = app_config.robot_arms.servo_controller.solution
        if solution == 'minghao':
            row, col = self.__servos_minghao.get_first_empty_cell()
        elif solution == 'xuming':
            row, col = self.__chessboard.get_first_empty_cell()

        if row >= 0:
            # TODO: this is a long time processing, should start a new thread 
            self.__xyz_arm.pickup_from_warehouse()
            self.__xyz_arm.place_to_cell(row, col)
            self.__chessboard.set_one_cell(row, col)
        if solution == 'minghao':
            # update map and send new map to Minghao's subsystem
            self.__servos_minghao.inform_minghao(row, col)


    def main_loop(self):
        self.xyz_arm_fill_chessboard()
        if self.__chessboard_need_a_new_plan:    
            plan= self.__current_plate.get_plan()  # always return the plan for next_coming_row
            self.__chessboard.loadplan()
            self.__chessboard_need_a_new_plan = False
        