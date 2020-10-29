

from plate import Plate, PlateRow, PlateCell, PLATE_STATE, PLATE_CELL_STATE

class Planner():

    def __init__(self, chessboard):
        self.__current_plate = Plate()
        self.__next_plate = Plate()
        self.__chessboard = chessboard
    
    def update_next_plate_from_eye_result(self, result):
        if True:
            # For solution voicevon@gmail.com
            plate_map = result
            self.__next_plate.from_map(plate_map)

    def create_plan(self):
        if self.__current_plate.state == PLATE_STATE.Mapped:
            unplanned_row_id = self.__current_plate.get_first_unplanned_row_id()
            if unplanned_row_id in range(0,18):
                # get shadow rows. should be counted in range(1,4)
                # return unplanned_row_id
                self.__create_plan_for_next_row(unplanned_row_id)
                
    def __try_to_renew_plate(self):
        #Check whether current plate is finished    ??
        if self.__current_plate.state == PLATE_STATE.Finished:
            map = self.__next_plate.to_map()
            self.__current_plate.from_map(map)
            self.__next_plate.to_state_begin()

    def __create_plan_for_next_row(self, unplanned_row_id):
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

        shadow_rows_range = self.__current_plate.get_shadow_rows_range(unplanned_row_id)
        for row_index in shadow_rows_range:
            this_row_is_full = True
            for col_id in range(0, 8):
                # Compare two cells between chessboard_cell and plate_cell
                plate_row_id = row_index + unplanned_row_id
                if self.__current_plate.is_empty_cell(plate_row_id, col_id):
                    # Got an empty plate_cell, Let's see whether we can refill this cell.
                    if self.__chessboard.is_planned_cell(row_index, col_id):
                        # got a matched cell from chessboard, Save plan, to plate and chessboard
                        self.__current_plate.set_cell_planned(plate_row_id, col_id)
                        self.__chessboard.set_cell_planned(plate_row_id, row_index, col_id)
                    else:
                        # Can't get matched cell from chessboard
                        this_row_is_full = False
                        
            if this_row_is_full:
                # all cells in this row are filled or refilled in plan
                self.__current_plate.finished_plan_for_this_row(unplanned_row_id)

    def main_loop(self):
        self.create_plan()
        self.__try_to_renew_plate()
