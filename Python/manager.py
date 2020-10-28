# -*- coding: utf-8 -*-

from global_const import app_config
import time
import sys
sys.path.append(app_config.path.text_color)
from color_print import const

# from robot_arms import RobotArms
from servo_array_driver import ServoArrayDriver
import paho.mqtt.client as mqtt
from mqtt_agent import MqttAgent

from robot_eye import RobotEye
from robot_sensors import RobotSensors
from xyz_arm import XyzArm
from chessboard import ChessboardRow, Chessboard, ChessboardCell, CHESSBOARD_CELL_STATE
from plate import Plate, PlateCell, PLATE_CELL_STATE, PLATE_STATE
from servos import Servos

class SowerManager():

    def __init__(self):
        self.__eye = RobotEye()
        self.__chessboard = Chessboard()
        self.__xyz_arm = XyzArm()
        self.__servos = Servos()
        self.__servos_minghao = ServoArrayDriver()
        self.__sensors = RobotSensors(self.on_new_plate_enter, self.on_new_row_enter)
        # self.__servos = ServoArrayDriver()
        self.__current_plate = Plate()
        self.__next_plate = Plate()
        self.__coming_row_id_of_current_plate = 0

        self.__goto = self.__on_state_begin
        # self.__goto = self.__on_state_test_mqtt
        # self.__mqtt = None
        self.__mqtt_agent = MqttAgent()
        self.__system_turn_on = False

        self.__YELLOW = const.print_color.fore.yellow
        self.__GREEN = const.print_color.fore.green
        self.__RESET = const.print_color.control.reset

    def setup(self):
        mqtt = self.__mqtt_agent.connect()
        self.__mqtt_agent.connect_eye(self.__eye.on_mqtt_message)
        # self.__eye.setup(self.__mqtt_agent, self.__on_eye_got_new_plate)
        self.__eye.setup(mqtt, self.__on_eye_got_new_plate)
        self.__servos.setup(self.__xyz_arm.pickup_then_place_to_cell)
        self.__xyz_arm.setup(mqtt, None)
        self.__xyz_arm.connect_to_marlin()
        self.__xyz_arm.Init_Marlin()
        self.__xyz_arm.init_and_home()

        print(const.print_color.background.blue + self.__YELLOW)
        print('System is initialized. Now is working')
        print(self.__RESET)

    def __on_state_test_mqtt(self):
        # return image as mqtt message payload
        # f= open("Python/test.jpg")
        # content = f.read()
        # byte_im = bytearray(content)


        # im = cv2.imread('test.jpg')
        # im_resize = cv2.resize(im, (500, 500))
        # is_success, im_buf_arr = cv2.imencode(".jpg", im_resize)
        # byte_im = im_buf_arr.tobytes()

        with open('test.jpg', 'rb') as f:
            byte_im = f.read()
        self.__mqtt.publish('sower/img/bin', byte_im )
        time.sleep(100)

    def __on_state_begin(self):
        if self.__system_turn_on:
            self.__goto = self.__on_state_working

    def __on_state_idle(self):
        if False:
            self.__goto = self.__on_state_working

    def __on_state_working(self):
        if self.__system_turn_on:
            self.__eye.main_loop()
            self.__xyz_arm_fill_buffer()
            self.__plan_servos_action()
        else:
            self.__goto = self.__on_state_begin

        if False:
            self.__goto = self.__on_state_emergency_stop

    def __on_state_emergency_stop(self):
        if self.__mqtt_system_on:
            self.__goto = self.__on_state_begin

    def __on_eye_got_new_plate(self, plate_array, image):
        if False:
            # For  solution  Minghao
            info = plate_array
            self.__servos_minghao.send_new_platmap(new_map)
        
        if True:
            # For solution voicevon@gmail.com
            plate_map = plate_array
            self.__next_plate.from_map(plate_map)

    def on_new_plate_enter(self):
        map = self.__next_plate.get_plate_map()
        self.__current_plate.from_map(map)

    def on_new_row_enter(self):
        self.__servos.output_i2c(123)
        self.__chessboard.execute_plan()
        
    
    def __create_servos_plan_for_next_row(self, unplanned_row_id):
        '''
        # try a new plan, only plan for one row entering
        #   This function will be invoked from main_loop()
        # When need a feeding plan?
        #   1. At least one shadow cells is empty.
        #       - What is shadow cells?
        #           - When the plate entered, one or two or three rows of the plate will be seen by chessboard,
        #           -  The cells those are inside of the three rows, is called shadow cells, 
        #       - How to calculate shadow cells?
        #           - Class Plate will help to get shadow cells.
        #   2. Chessboard cell is avaliable to drop.
        #       - How to decide chessboard cell is avaliable to drop ?
        #           - chessboard.cell(row, col).state == CHESSBOARD_CELL_STATE.Unplanned
        #   3. How is the plan orgnized?
        #       - To chessboard, will plan to each cell.
        #       - To plate, will plan to each row ??   
        #   4. When to finish plan to a row entering?
        #       - A: All cells in this row is not empty (Prefilled or planned)
        #       - B: Target row of plate has moved into shadow area.
        '''

        shadow_rows = self.__current_plate.get_shadow_rows(unplanned_row_id)
        for row_index in range (0, len(shadow_rows)):
            plate_row = self.__current_plate.get_row_map(unplanned_row_id + row_index)
            chessboard_row = self.__chessboard.get_row_map(row_index)
            this_row_is_full = True
            for col in range(0, 8):
                # Compare two cells between chessboard_cell and plate_cell
                plate_cell = PlateCell()
                plate_cell.from_row_col(unplanned_row_id + row_index, col)
                chessboard_cell = ChessboardCell()
                chessboard_cell.from_row_col(row_index, col)
                if plate_cell.state == PLATE_CELL_STATE.Emppty_Unplanned:
                    # Got an empty plate_cell, Let's see whether we can refill this cell.
                    if chessboard_cell.state == CHESSBOARD_CELL_STATE.Unplanned:
                        # got a matched cell from chessboard
                        plate_cell.to_state(PLATE_CELL_STATE.Empty_Planned)
                        chessboard_cell.to_state(CHESSBOARD_CELL_STATE.PlannedToDrop)
                    else:
                        # Can't get matched cell from chessboard
                        this_row_is_full = False
                        
            if this_row_is_full:
                # all cells in this row are filled or refilled
                self.__current_plate.finished_plan_for_this_row(unplanned_row_id)

    def release_servos_action(self):
        row_id = self.next_enter_row_id()
        # get servos_action, It's 3 bytes array, or Tuple?
        servos_action = Servos_action()
        shadow_rows = range(self.next_enter_row_id, self.next_enter_row_id-3, -1)
        for row_id in shadow_rows:
            if row_id >=0:
                for col_id in range(8, 0, -1):
                    if self.rows[row_id + offset].state == PLATE_CELL_STATE.Empty_Planned 
                        servos_action.bytes[0] *= 2
                        servos_action.bytes[0] += 1
        self.__servos.output_i2c(servos_action.bytes)
        self.__chessboard.on_servos_released(servos_action.bytes)

    def __plan_servos_action(self):
        if self.__current_plate.has_got_map():
            unplanned_row_id = self.__current_plate.get_unplanned_row_id()
            if unplanned_row_id in range(0,16):
                # get shadow rows. should be counted in range(1,4)
                self.__create_servos_plan_for_next_row(unplanned_row_id)
            

        #Check whether current plate is finished
        if self.__current_plate.state == PLATE_STATE.Finished:
            map = self.__next_plate.to_map()
            self.__current_plate.from_map(map)
            self.__next_plate.to_state_begin()

    def __xyz_arm_fill_buffer(self):
        row, col = self.__chessboard.get_one_empty_cell()
        if row >= 0:
            self.__xyz_arm.pickup_from_warehouse()
            self.__xyz_arm.place_to_cell(row, col)
            self.__chessboard.set_one_cell(row, col)

    def main_loop(self):
        self.__system_turn_on = self.__mqtt_agent.mqtt_system_turn_on 
        last_function = self.__goto
        self.__goto()
        if last_function != self.__goto:
            print(const.print_color.background.blue + self.__YELLOW)
            print(self.__goto.__name__)
            print(self.__RESET)


if __name__ == "__main__":
    runner = SowerManager()
    runner.setup()
    while True:
        runner.main_loop()


#
#         |-----------> ??? ----------->|
#         ^                             |
#         |-----------> ??? ----------->|
#         ^                             |
#         |-----------> ??? ----------->|
#         ^                             |
#         |-----------> ??? ----------->|
#         ^
#         |           |--->--->--->--->--->--->---|
#         ^           |                           |
#        begin ---> idle ---> working ------> EmergencyStop
#         ^           ^          |                 |
#         |           |--<---<---|                 |
#         ^                      |                 |
#         |<---<---<---<---<---<--                 |
#         ^                                        |
#         |<---<---<---<---<---<---<---<---<---<----
#   
#
#        idle, EmergencyStop: are not avaliable before version 1.0
