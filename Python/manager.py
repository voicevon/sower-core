# -*- coding: utf-8 -*-

from global_const import app_config
from mqtt_helper import  g_mqtt

import time
import sys
sys.path.append(app_config.path.text_color)
from color_print import const

# from robot_arms import RobotArms
# import paho.mqtt.client as mqtt

from robot_eye import RobotEye
from planner import Planner
from robot_sower  import RobotSower

class SowerManager():

    def __init__(self):
        # self.__mqtt_agent = MqttAgent()
        g_mqtt.connect_broker()
        # app_config.g.mqtt.connect_broker()
        # self.mqtt_client = self.__mqtt_agent.connect()
        self.__eye = RobotEye()
        # self.__robot_sower = RobotSower(self.mqtt_client)
        # phy_chessboard = self.__robot_sower.get_chessboard()
        self.__planner = Planner()

        self.__coming_row_id_of_current_plate = 0

        self.__goto = self.__on_state_begin
        self.__system_turn_on = False

        self.__YELLOW = const.print_color.fore.yellow
        self.__GREEN = const.print_color.fore.green
        self.__RESET = const.print_color.control.reset

        # subscribe all topics from config files
        for topic in app_config.server.mqtt.subscript_topics.topic_dict.keys():
            g_mqtt.subscribe(topic)
            # app_config.g.mqtt.subscribe(topic)

        print('MQTT subscription is done')

        solution = app_config.robot_arms.servo_controller.solution 
        if solution == 'minghao':
            self.__eye.setup(self.__robot_sower.on_eye_got_new_plate)
        elif solution == 'xuming':
            self.__eye.setup(self.__planner.update_next_plate_from_eye_result)

        print(const.print_color.background.blue + self.__YELLOW)
        print('System is initialized. Now is working')
        print(self.__RESET)

    def __on_state_begin(self):
        if self.__system_turn_on:
            self.__goto = self.__on_state_working

    def __on_state_idle(self):
        if False:
            self.__goto = self.__on_state_working

    def __on_state_working(self):
        if self.__system_turn_on:
            self.__eye.main_loop()   # for single threading
            self. __planner.main_loop()
            self.__robot_sower.main_loop()
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
        # self.__system_turn_on = self.__mqtt_agent.mqtt_system_turn_on 
        last_function = self.__goto
        self.__goto()
        if last_function != self.__goto:
            print(const.print_color.background.blue + self.__YELLOW)
            print(self.__goto.__name__)
            print(self.__RESET)


if __name__ == "__main__":
    runner = SowerManager()
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
