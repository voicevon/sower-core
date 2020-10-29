from robot_sensors import RobotSensors
from robot_xyz_arm import XyzArm
from rebot_servos import Servos
from servo_array_driver import ServoArrayDriver
from chessboard import ChessboardRow, Chessboard, ChessboardCell, CHESSBOARD_CELL_STATE
from plate import Plate, PlateCell, PLATE_CELL_STATE, PLATE_STATE




class RobotSower():

    def __init__(self):
        self.__xyz_arm = XyzArm()
        self.__servos = Servos()
        self.__servos_minghao = ServoArrayDriver()
        self.__sensors = RobotSensors(self.__on_new_plate_enter, self.__on_new_row_enter)
        self.__current_plate = Plate()
        self.__next_plate = Plate()

        self.__chessboard = Chessboard()
        
        self.__servos.setup(self.__xyz_arm.pickup_then_place_to_cell)
        self.__xyz_arm.setup(mqtt, None)
        self.__xyz_arm.connect_to_marlin()
        self.__xyz_arm.Init_Marlin()
        self.__xyz_arm.init_and_home()
    def get_chessboard(self):
        return self.__chessboard

    def on_eye_got_new_plate(self, plate_array, image):
        if False:
            # For  solution  Minghao
            info = plate_array
            self.__servos_minghao.send_new_platmap(new_map)
        
        if True:
            # For solution voicevon@gmail.com
            plate_map = plate_array
            self.__next_plate.from_map(plate_map)

    def __on_new_plate_enter(self):
        map = self.__next_plate.get_plate_map()
        self.__current_plate.from_map(map)

    def __on_new_row_enter(self):
        self.__servos.output_i2c(123)
        self.__chessboard.execute_plan()


    def xyz_arm_fill_buffer(self):
        row, col = self.__chessboard.get_one_empty_cell()
        if row >= 0:
            self.__xyz_arm.pickup_from_warehouse()
            self.__xyz_arm.place_to_cell(row, col)
            self.__chessboard.set_one_cell(row, col)