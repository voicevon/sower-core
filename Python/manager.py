
from global_const import app_config

import sys
sys.path.append(app_config.path.text_color)
from color_print import const

from robot_eye import RobotEye
from robot_arm import RobotArm
from servo_array_driver import ServoArrayDriver
import paho.mqtt.client as mqtt

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


class SowerManager():
    
    def __init__(self):
        self.__eye = RobotEye()
        self.__arm = RobotArm()
        self.__servos = ServoArrayDriver()

        self.__goto = self.__on_state_begin

        self.__mqtt = mqtt
        self.__mqtt = mqtt.Client("sower-2039-1004")  # create new instance
        self.__mqtt_system_turn_on = False
        self.__eye.set_service_saw_caves(self.__servos.update_caves)

        self.__YELLOW = const.print_color.fore.yellow
        self.__GREEN = const.print_color.fore.green
        self.__RESET = const.print_color.control.reset

    def __on_state_begin(self):
        if self.__mqtt_system_turn_on:
            # Turn on light
            # Trun on main motor
            self.__mqtt.publish('sower/light/command', 'ON')
            self.__mqtt.publish('sower/motor/command', 'ON')
            self.__goto = self.__on_state_working

    def __on_state_idle(self):
        if False:
            self.__goto = self.__on_state_working

    def __on_state_working(self):
        if self.__mqtt_system_turn_on:
            # Turn off light
            # Trun off main motor
            self.__mqtt.publish('sower/light/command', 'OFF')
            self.__mqtt.publish('sower/motor/command', 'OFF')
            self.__goto = self.__on_state_begin

        if False:
            self.__goto = self.__on_state_emergency_stop

    def __on_state_emergency_stop(self):
        if self.__mqtt_system_on:
            self.__goto = self.__on_state_begin

    def start(self):
        self.__start_mqtt()

        print(const.print_color.background.blue + self.__YELLOW)
        print('System is initialized. Now is working')
        print(self.__RESET)

    def main_loop(self):
        last_function = self.__goto
        self.__goto()
        if last_function != self.__goto:
            print(const.print_color.background.blue + self.__YELLOW)
            print(self.__goto.__name__)
            print(self.__RESET)

    def __start_mqtt(self):
        broker = app_config.server.mqtt.broker_addr
        uid = app_config.server.mqtt.username
        psw = app_config.server.mqtt.password
        self.__mqtt.username_pw_set(username=uid, password=psw)
        self.__mqtt.connect(broker)
        print(self.__GREEN + '[Info]: MQTT has connected to: %s' % broker + self.__RESET)

        self.__mqtt.loop_start()
        # self.__mqtt.subscribe("house/bulbs/bulb1")
        self.__mqtt.publish(topic="fishtank/switch/r4/command", payload="OFF", retain=True)
        self.__mqtt.on_message = self.__mqtt_on_message
        # self.__mqtt.loop_stop()

    def __mqtt_on_message(self, client, userdata, message):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)

        if True:
            self.__mqtt_system_turn_on = True

if __name__ == "__main__":
    runner = SowerManager()
    runner.start()
    while True:
        runner.main_loop()
