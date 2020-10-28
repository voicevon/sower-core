

from global_const import app_config

import sys
sys.path.append(app_config.path.text_color)
from color_print import const

# from servo_array_driver import ServoArrayDriver

from xyz_arm import XyzArm
from chessboard import ChessboardRow, Chessboard, ChessboardCell, CHESSBOARD_CELL_STATE
from plate import Plate, PlateCell, PLATE_CELL_STATE
from servos import Servos
from threading import Thread



class Planner():
    def __init__(self):
        self.__servos = Servos(self.on_servos_finished_one_row)
        self.__robot = XyzArm()
        self.__current_plate = Plate()
        self.__next_plate = Plate()
        self.__chessboard = Chessboard()
        self.__coming_row_id_of_current_plate = 0
 
    def connect(self):
        self.__robot.connect_to_marlin()
        self.__robot.Init_Marlin()
        self.__servos.connect()
    
    def on_servos_finished_one_row(self, row_id):
        # update the chessboard, might be 3 rows will be effected.
        self.__coming_row_id_of_current_plate = row_id + 1

        if row_id == 15:
            # finished current plate, point to next plate
            self.__current_plate.to_finished()

    def __create_servos_plan_for_next_row(self):
        '''
        # try a new plan, only plan for one row entering
        #   This function will be invoked from main_loop()
        # When need a feeding plan?
        #   1. At least one shadow cells is empty.
        #       - What is shadow cells?
        #           - When the plate entered, one or two or three rows of the plate will be seen by chessboard,
        #           -  The cells those are inside of the three rows, is called shadow cells, 
        #       - How to calculate shadow cells?
        #           - Class Plate will help to get shadow cells.
        #   2. Chessboard cell is avaliable to drop.
        #       - How to decide chessboard cell is avaliable to drop ?
        #           - chessboard.cell(row, col).state == CHESSBOARD_CELL_STATE.Unplanned
        #   3. How is the plan orgnized?
        #       - To chessboard, will plan to each cell.
        #       - To plate, will plan to each row ??   
        #   4. When to finish plan to a row entering?
        #       - A: All cells in this row is not empty (Prefilled or planned)
        #       - B: Target row of plate has moved into shadow area.
        '''
        if not self.__current_plate.has_got_map():
            return

        unplanned_row_id = self.__current_plate.get_unplanned_row_id()
        
        if unplanned_row_id in range(0,16):
            # get shadow rows. should be counted in range(1,4)
            shadow_rows = self.__current_plate.get_shadow_rows(unplanned_row_id)
            for row_index in range (0, len(shadow_rows)):
                plate_row = self.__current_plate.get_row_map(unplanned_row_id + row_index)
                chessboard_row = self.__chessboard.get_row_map(row_index)
                this_row_is_full = True
                for col in range(0, 8):
                    # Compare two cells between chessboard_cell and plate_cell
                    plate_cell = PlateCell()
                    plate_cell.from_row_col(unplanned_row_id + row_index, col)
                    chessboard_cell = ChessboardCell()
                    chessboard_cell.from_row_col(row_index, col)
                    if plate_cell.state == PLATE_CELL_STATE.Emppty_Unplanned:
                        # Got an empty plate_cell, Let's see whether we can refill this cell.
                        if chessboard_cell.state == CHESSBOARD_CELL_STATE.Unplanned:
                            # got a matched cell from chessboard
                            plate_cell.to_state(PLATE_CELL_STATE.Empty_Planned)
                            chessboard_cell.to_state(CHESSBOARD_CELL_STATE.PlannedToDrop)
                        else:
                            # Can't get matched cell from chessboard
                            this_row_is_full = False
                            
                if this_row_is_full:
                    # all cells in this row are filled or refilled
                    self.__current_plate.finished_plan_for_this_row(unplanned_row_id)





        entering_row = self.__chessboard.rows[row]
        
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
        if self.__current_plate.state == PLATE_STATE.Finished:
            map = self.__next_plate.to_map()
            self.__current_plate.from_map(map)
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

