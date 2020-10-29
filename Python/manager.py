# -*- coding: utf-8 -*-

from global_const import app_config
import time
import sys
sys.path.append(app_config.path.text_color)
from color_print import const

# from robot_arms import RobotArms
import paho.mqtt.client as mqtt
from mqtt_agent import MqttAgent

from robot_eye import RobotEye
from planner import Planner
from robot_sower  import RobotSower

class SowerManager():

    def __init__(self):
        self.__eye = RobotEye()
        self.__robot_sower = RobotSower()
        phy_chessboard = RobotSower.get_chessboard()
        self.__planner = Planner(phy_chessboard)

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
        on_eye_got_new_plate_callbacks = []
        on_eye_got_new_plate_callbacks.append(self.__planner.on_eye_got_new_plate)
        on_eye_got_new_plate_callbacks.append(self.__robot_sower.on_eye_got_new_plate)
        self.__eye.setup(mqtt, on_eye_got_new_plate_callbacks)

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
            self.__eye.main_loop()   # for single threading
            self.__robot_sower.xyz_arm_fill_buffer()
            self. __planner.try_to_renew_plate()
            self.__planner.create_plan()
        else:
            self.__goto = self.__on_state_begin

        if False:
            self.__goto = self.__on_state_emergency_stop

    def __on_state_emergency_stop(self):
        if self.__mqtt_system_on:
            self.__goto = self.__on_state_begin



    def release_servos_action(self):
        row_id = self.next_enter_row_id()
        # get servos_action, It's 3 bytes array, or Tuple?
        servos_action = Servos_action()
        shadow_rows = range(self.next_enter_row_id, self.next_enter_row_id-3, -1)
        for row_id in shadow_rows:
            if row_id >=0:
                for col_id in range(8, 0, -1):
                    if self.rows[row_id + offset].state == PLATE_CELL_STATE.Empty_Planned:
                        servos_action.bytes[0] *= 2
                        servos_action.bytes[0] += 1
        self.__servos.output_i2c(servos_action.bytes)
        self.__chessboard.on_servos_released(servos_action.bytes)





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
