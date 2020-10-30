from enum import Enum
from robot_servos import Servos
from global_const import  app_config


class CHESSBOARD_CELL_STATE(Enum):
    Empty = 1
    Unplanned = 2
    PlannedToDrop = 3
    Dropping = 5

class ChessboardCell():
    '''
    Empty  ---> Unplanned ---> planed_to_drop  ---> dropping
     ^                                                |
     |------------------------------------------------|    
    '''
    def __init__(self):
        self.planned_to_drop_for_plate_row_id = 0
        self.state = CHESSBOARD_CELL_STATE.Empty # Empty, filled_no_plan, planned_to_drop, 

class Chessboard():
    '''
    The Chessboard is a 2D  array .
        Rows from right to left
        Cols from top to bottom
            (2,7), (1,7), (0,7)   
                   ......
                          (0,2)
                          (0,1)
            (2,0), (1,0), (0,0)   
    '''
    def __init__(self):
        self.__servos = Servos()

        self.__ROWS = app_config.chessboard.rows_count
        self.__COLS = app_config.chessboard.cols_count
        self.__row_range = range(0, self.__ROWS)
        self.__col_range = range(0, self.__COLS)
        self.cells = [([ChessboardCell()] * self.__ROWS) for i in range(self.__COLS)]
        
    def get_first_empty_cell(self):
        for row_id in self.__row_range:
            for col_id in self.__col_range:
                if self.cells[row_id][col_id].state == CHESSBOARD_CELL_STATE.Empty:
                    return row_id, col_id
        return None

    def set_cell_planned(self, plate_coming_row_id, row_id, col_id):
        self.cells[row_id, col_id].state = CHESSBOARD_CELL_STATE.PlannedToDrop
        self.cells[row_id, col_id].planned_to_drop_for_coming_plate_row_id = plate_coming_row_id

    def is_planned_cell(self, row_id, col_id):
        # for row_id in self.__row_range:
        #     for col_id in self.__col_range:
        if self.cells[row_id][col_id].state == CHESSBOARD_CELL_STATE.PlannedToDrop:
            return True
        else:
            return False

    def __load_plan(self, the_plan_for_coming_row):
        '''
        some cell's state become to PlannedToDrop 
        '''
        command = [0, 0, 0]
        for row_id in self.__row_range:
            for col_id in self.__col_range:
                if self.cells[row_id, col_id].state == CHESSBOARD_CELL_STATE.PlannedToDrop:
                    if self.cells[row_id, col_id].state == the_plan_for_coming_row:
                        command[row_id] += 1
                command [row_id]*= 2
        
        return command

    def execute_plan(self, plate_coming_row_id):
        '''
        output plan to servos.
        some cell's (whose state == PlannedToDrop) state becomes to Empty.
        '''
        command = self.__load_plan(plate_coming_row_id)
        self.__servos.output_i2c(command)
        # update chessboard cells state.
        for row_id in range(0, 3):
            for col_id in range(0, 8):
                this_cell = self.cells[row_id][col_id]
                if this_cell.state == CHESSBOARD_CELL_STATE.PlannedToDrop:
                    this_cell.state = CHESSBOARD_CELL_STATE.Empty

            
if __name__ == "__main__":
    test = Chessboard()
