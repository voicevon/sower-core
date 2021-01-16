# -*- coding: utf-8 -*-
from app_config import AppConfig

import sys
sys.path.append(AppConfig.pylib_path)
from mqtt_helper import g_mqtt
from terminal_font import TerminalFont

# from robot_eye import RobotEye
from robot_sower  import RobotSower

import time

class SowerManager():

    def __connect_to_mqtt_broker(self):
        broker = AppConfig.server.mqtt.broker_addr
        port = AppConfig.server.mqtt.port
        uid = AppConfig.server.mqtt.username
        password = AppConfig.server.mqtt.password
        g_mqtt.connect_broker(broker, port, uid, password)

    def __init__(self):
        self.__connect_to_mqtt_broker()
        # self.__eye = RobotEye()
        self.__robot_sower = RobotSower()

        self.__goto = self.__on_state_begin
        self.__system_turn_on = True

        self.__YELLOW = TerminalFont.Color.Fore.yellow
        self.__GREEN = TerminalFont.Color.Fore.yellow
        self.__RESET = TerminalFont.Color.Control.reset

        # subscribe all topics from config files
        topic_count = 0
        for topic in AppConfig.server.mqtt.subscript_topics.topic_dict.keys():
            g_mqtt.subscribe(topic)
            topic_count += 1
            print('subscribed MQTT topics from config :  %i, %s' %(topic_count,topic))


        print('MQTT subscription is done')

        solution = AppConfig.robot_arms.servo_controller.solution 
        if solution == 'minghao':
            self.__eye.setup(self.__robot_sower.on_eye_got_new_plate)
        # elif solution == 'xuming':
        #     self.__eye.setup(self.__planner.update_next_plate_from_eye_result)

        print(self.__YELLOW + TerminalFont.Color.Background.blue)
        print('System is initialized. Now is working')
        print(self.__RESET)

    def __on_state_begin(self):
        if self.__system_turn_on:
            self.__robot_sower.turn_on_light_fan_conveyor()
            self.__goto = self.__on_state_working

    def __on_state_idle(self):
        if False:
            self.__goto = self.__on_state_working

    def __on_state_working(self):
        if self.__system_turn_on:
            # self.__eye.spin_once()   # for single threading
            # self. __planner.spin_once()  # For Xuming solution
            self.__robot_sower.spin_once()
        else:
            self.__goto = self.__on_state_begin

        if False:
            self.__goto = self.__on_state_emergency_stop

    def __on_state_emergency_stop(self):
        if self.__mqtt_system_on:
            self.__goto = self.__on_state_begin


    def spin(self):
        # self.__system_turn_on = self.__mqtt_agent.mqtt_system_turn_on 
        while True:
            last_function = self.__goto
            self.__goto()
            if last_function != self.__goto:
                print(self.__YELLOW + TerminalFont.Color.Background.blue)
                print(self.__goto.__name__)
                print(self.__RESET)


if __name__ == "__main__":
    runner = SowerManager()
    runner.spin()


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
