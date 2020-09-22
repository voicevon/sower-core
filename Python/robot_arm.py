

from global_const import app_config

import sys
sys.path.append(app_config.path.text_color)
from color_print import const
from servo_array_driver import ServoArrayDriver
from reprap_robot_arm import ReprapRobot
from plate_and_cave import Cave, Plate, SowerBuffer


class PreFeeder(ReprapRobot):

    def fill_in_one_cave(self, target_cave_id):
        target_cave = self.BufferCave()
        target_cave.from_id(target_cave_id)
        self.goto('Warehouse')
        self.eef_pick_up()
        self.goto(target_cave)
        self.eef_place_down()


class RobotArms():
    
    def __init__(self):
        self.__servos = ServoArrayDriver()
        self.__prefeeder = PreFeeder()

        self.__sower_buffer = SowerBuffer()
        self.__plate_from_eye = Plate()
        self.__plate_below_buffer = Plate()

    def connect(self):
        self.__prefeeder.connect_to_marlin()
        self.__prefeeder.Init_Marlin()
        self.__servos.connect()
    
    def set_new_plate(self, new_plate):
        self.__plate_from_eye = new_plate


if __name__ == "__main__":
    test = RobotArms()
        