

from global_const import app_config

import sys
sys.path.append(app_config.path.text_color)
from color_print import const

from servo_array_driver import ServoArrayDriver
from plate_and_cell import Cell, Plate, FeedingBuffer
# from human_level_robot import HumanLevelRobot
from xyz_arm import XyzArm
from threading import Thread



class RobotArms():
    '''
    There are  two arms:  xyz_arm and servos
    '''
    def __init__(self):
        self.__servos = ServoArrayDriver()
        self.__robot = XyzArm()

        self.__feeding_buffer = FeedingBuffer()
        self.__plate_from_eye = Plate()
        self.__target_plate = Plate()

    def connect(self):
        self.__robot.connect_to_marlin()
        self.__robot.Init_Marlin()
        self.__servos.connect()

    def set_new_plate(self, new_plate):
        self.__plate_from_eye = new_plate

    def start_with_new_thread(self):
        self.__on_my_own_thread = True
        t = threading(self.__main_task)
        t.start

    def main_loop(self):
        # This is mainly for debugging. do not use while loop in this function!
        # For better performance, invoke start_with_new_thread() instead.
        self.__main_task()

    def __main_task(self):
        # Check feeding_buffer is there any cave is empty
        cell = self.__target_plate.find_empty_cell()
        if cell is not None:
            self.__robot.place_to_cell(cell.)
            self.__robot.pickup_from_warehouse()
        pass


if __name__ == "__main__":
    test = RobotArms()
