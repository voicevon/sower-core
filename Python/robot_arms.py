

from global_const import app_config

import sys
sys.path.append(app_config.path.text_color)
from color_print import const

from servo_array_driver import ServoArrayDriver
from plate_and_cell import Cell, Plate, FeedingBuffer
# from human_level_robot import HumanLevelRobot
from xyz_arm import XyzArm
from threading import Thread

class Servos_action():
    def __init__(self):
        self.row_id = 0
        self.row_action = list(bytes)


class Servos():
    def __init__(self, callback_on_finished_one_row):
        self.last_finished_row
        self.__callback = callback_on_finished_one_row
        self.__planned_actions = list(Servos_action)

    def append_planned_action(self, servos_action):
            self.__planned_actions.append(servos_action)


    def on_finished_one_row(self,  row_id):
        self.last_finished_row = row_id
        self.__planned_actions.remove[0]
        self.__callback()

    def publish_planning(self):
        app_config.mqtt.publish('sower/servo/plan', planning)

class Buffer():
    def __init__(self):
        self.map = list(bytes)
        self.map.append (0x00)
        self.map.append (0x00)
        self.map.append (0x00)

    def get_one_empty_cell(self):
        row_id = 0
        col_id = 2
        if True:
            return row_id, col_id
        
        return None

    def get_one_empty_col_id(self):
        empty_col_id = -1
        if True:
             empty_col_id =7
        
        return empty_col_id
    def set_one_cell(self, row_id, col_id):
        rowl_map = self.map[row_id]
        rowl_map |= 1 << col_id
        self.map[row_id]= rowl_map

class Planner():
    def __init__(self):
        self.__servos = Servos(self.on_servos_finished_one_row)
        self.__robot = XyzArm()
        self.__current_plate_map = None
        self.__next_plate_map = None
        self.__buffer = Buffer()
 

    def connect(self):
        self.__robot.connect_to_marlin()
        self.__robot.Init_Marlin()
        self.__servos.connect()
    
    def on_servos_finished_one_row(self, row_id):
        if row_id == 15:
            # finished current plate
            self.__current_plate_map = self.__next_plate_map
            self.__next_plate_map = None

        # try a batch of  new plan, utill one or more cols in buffer is empty.
        while True:
            empty_col_id = self.__buffer.get_one_empty_col_id()
            if empty_col_id  == -1:
                # No col is continuously empty. can create plan now.
                action = Servos_action()
                action.row_id = 5
                action.row_action = 6
                self.__servos.append_planned_action(action)

        # send plan to servo


    def fill_buffer(self):
        row, col = self.__buffer.get_one_empty_cell()
        if row == -1:
            return
        self.xyz_arm.pickup_from_warehouse()
        self.xyz_arm.place_to_cell(row, col)
        self.__buffer.set_one_cell(row, col)


    def set_new_plate(self, plate_map):
        if self.__current_plate_map is None:
            self.__current_plate_map = plate_map
        else:
            self.__next_plate_map = plate_map


class RobotArms():
    '''
    There are  two arms:  xyz_arm and servos
    '''
    def __init__(self):
        # self.__servos = ServoArrayDriver()
        self.__servos = Servos()
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
