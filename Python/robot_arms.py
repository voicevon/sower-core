

# from global_const import app_config

# import sys
# sys.path.append(app_config.path.text_color)
# from color_print import const

# from servo_array_driver import ServoArrayDriver
# from plate_and_cell import Cell, Plate, FeedingBuffer
# from human_level_robot import HumanLevelRobot
from xyz_arm import XyzArm
from chessboard import ChessboardRow, Chessboard, ChessboardCell
from threading import Thread
from enum import Enum

class Servos_action():
    def __init__(self):
        self.row_id = 0
        self.row_action = list(bytes)

class Servos():
    # https://maker.pro/nvidia-jetson/tutorial/how-to-use-gpio-pins-on-jetson-nano-developer-kit
    def __init__(self, callback_on_finished_one_row):
        self.last_finished_row = 0
        self.__callback = callback_on_finished_one_row
        # self.__planned_actions = list(Servos_action)
        self.__planned_actions = []

    def append_planned_action(self, servos_action):
            self.__planned_actions.append(servos_action)


    def on_finished_one_row(self, row_id):
        self.last_finished_row = row_id
        self.__planned_actions.remove[0]
        self.__callback()

    def publish_planning(self):
        app_config.mqtt.publish('sower/servo/plan', planning)

class PlateRow():
    '''
    Composed by an array of cells
    cell == True: means empty. 
    '''
    def __init__(self):
        # self.cells=list(bool)
        self.cells=[]
        self.config_cols_lenth = 8
        for i in range(0, self.config_cols_lenth):
            self.cells.append(True)

    def from_row_map(self, row_map):
        for i in range(0,8):
            self.cells[i] = row_map[i]
    
    def print_out(self):
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        out = ''
        for c in self.cells:
            if c:
                out += 'O'
            else:
                out += '.'
        print(out)

class PLATE_STATE(Enum):
    Started = 1
    Mapped = 2
    Armed = 3
    Finished = 4 

class Plate():
    '''
    A plate is composed by array of PlateRows

    StateMachine of a plate:
          started ------->   mapped  ---------> armed  --------> finished
          ^                                                                                                  |
          |----------------------------------------------------------------|
    '''
    def __init__(self):
        # self.rows = list(PlateRow)
        self.rows = []
        self.state = PLATE_STATE.Started

    def get_row_map(self, row_id):
        '''
        return an array of empty cells in a row
        '''
        return self.rows[row_id]

    def from_map(self, cells_map):
        self.rows=[]
        for i in range(0,8):
            row = PlateRow()
            row.from_row_map(cells_map[i])
            self.rows.append(row)
        self.state = PLATE_STATE.Mapped

    def print_out_map(self):
        for row in self.rows:
            print('##################################')
            row.print_out()
class Planner():
    def __init__(self):
        self.__servos = Servos(self.on_servos_finished_one_row)
        # self.__robot = XyzArm()
        self.current_plate = Plate()
        self.__next_plate = Plate()
        self.__chessboard = Chessboard()
 
    def connect(self):
        self.__robot.connect_to_marlin()
        self.__robot.Init_Marlin()
        self.__servos.connect()
    
    def on_servos_finished_one_row(self, row_id):
        # update the chessboard, might be 3 rows will be effected.
        self.__chessboard.update_releasing(row_id)

        if row_id == 15:
            # finished current plate, point to next plate
            self.current_plate.to_finished()

    def __create_servos_plan_for_next_row(self):
        # try a new plan, only for one row.
        # When need a feeding plan?
        #   1. empty cell need to be filled.
        #   2. chessboard cell is avaliable to drop
        row = self.__chessboard.get_row_to_plan()
        
        if row == -1:
            # chessboard is full, no empty cell
            return
        row_map = self.__chessboard.rows[row]
        
        if True:
            # need to be filled.
            if True:
                # chessbord is avaliable
                
                # planed to drop
                row_map.cell[x].plan_to_drop()
                


        if empty_col_id  == -1:
            # No col is continuously empty. can create plan now.
            action = Servos_action()
            action.row_id = 5
            action.row_action = 6
            self.__servos.append_planned_action(action)

    def main_loop(self):
        self.__create_servos_plan_for_next_row()
        self.__xyz_arm_fill_buffer()

        #Check whether current plate is finished
        if self.current_plate.state == PLATE_STATE.Finished:
            map = self.__next_plate.to_map()
            self.current_plate.from_map(map)
            self.__next_plate.to_state_begin()

    def __xyz_arm_fill_buffer(self):
        row, col = self.__chessboard.get_one_empty_cell()
        if row == -1:
            return
        self.xyz_arm.pickup_from_warehouse()
        self.xyz_arm.place_to_cell(row, col)
        self.__chessboard.set_one_cell(row, col)


    def set_new_plate(self, plate_map):
        '''
        This will be invoked when camera got a new plate.
        '''
        self.__next_plate.from_map(plate_map)

        

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
            # self.__robot.place_to_cell(cell.)
            self.__robot.pickup_from_warehouse()
        pass


if __name__ == "__main__":
    runner = Planner()
    map = [[True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True],
    [True,True,True,True,True,True,True,True]]
    runner.set_new_plate(map)
    runner.main_loop()
    runner.main_loop()
    runner.main_loop()
    runner.main_loop()
    runner.current_plate.print_out_map()

