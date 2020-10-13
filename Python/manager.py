# -*- coding: utf-8 -*-

from global_const import app_config
import time
import sys
sys.path.append(app_config.path.text_color)
from color_print import const

from robot_eye import RobotEye
# from robot_arms import RobotArms
from servo_array_driver import ServoArrayDriver
import paho.mqtt.client as mqtt
from mqtt_agent import MqttAgent
from xyz_arm import XyzArm

class SowerManager():

    def __init__(self):
        self.__eye = RobotEye()
        self.__xyz_arm = XyzArm()
        self.__xyz_arm.init_and_home()
        self.__servos = ServoArrayDriver()

        self.__goto = self.__on_state_begin
        # self.__goto = self.__on_state_test_mqtt
        # self.__mqtt = None
        self.__mqtt_agent = MqttAgent()
        self.__system_turn_on = False

        self.__YELLOW = const.print_color.fore.yellow
        self.__GREEN = const.print_color.fore.green
        self.__RESET = const.print_color.control.reset

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
        self.__mqtt.publish('sower/img/bin',byte_im )
        time.sleep(100)

    def __on_state_begin(self):
        if self.__system_turn_on:
            # Turn on light
            # Trun on main motor
            # Trun on vaccum motor
            # self.__mqtt.publish('sower/switch/light/command', 'ON')
            # self.__mqtt.publish('sower/switch/motor/command', 'ON')
            # self.__mqtt.publish('sower/switch/vaccum/command', 'ON')
            self.__goto = self.__on_state_working
            #print('begin begin')

    def __on_state_idle(self):
        if False:
            self.__goto = self.__on_state_working

    def __on_state_working(self):
        if self.__system_turn_on:
            #print('bbbbbbbbbbbbbbbbbbbbbbbbbbbbb')
            # Turn off light
            # Trun off main motor
            self.__mqtt.publish('sower/light/command', 'OFF')
            self.__mqtt.publish('sower/motor/command', 'OFF')
            self.__eye.main_loop()
        else:
            self.__goto = self.__on_state_begin

        if False:
            self.__goto = self.__on_state_emergency_stop

    def __on_state_emergency_stop(self):
        if self.__mqtt_system_on:
            self.__goto = self.__on_state_begin

    def __on_eye_got_new_plate(self, plate_array, image):
        self.__servos.send_new_platmap(plate_array)


        # flask return image to web ui

            
    def setup(self):
        mqtt = self.__mqtt_agent.connect()
        self.__mqtt_agent.connect_eye(self.__eye.on_mqtt_message)
        self.__eye.setup(self.__mqtt_agent, self.__on_eye_got_new_plate)
        self.__eye.setup(mqtt, self.__on_eye_got_new_plate)
        self.__xyz_arm.setup(mqtt, None)
        self.__servos.setup(self.__xyz_arm.pickup_then_place_to_cell)

        print(const.print_color.background.blue + self.__YELLOW)
        print('System is initialized. Now is working')
        print(self.__RESET)

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
