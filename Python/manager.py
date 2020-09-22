
from global_const import app_config

import sys
sys.path.append(app_config.path.text_color)
from color_print import const

from robot_eye import RobotEye
from robot_arm import RobotArm

class SowerManager():
    def __init__(self):
        self.__eye = RobotEye()
        self.__arm = RobotArm()

        self.__YELLOW = const.print_color.fore.yellow

    def start(self):
        self.__hello_world()

    def main_loop(self):
        pass

    def __hello_world(self):
        print(self.__YELLOW + 'Hello team!')

if __name__ == "__main__":
    runner = SowerManager()
    runner.start()
