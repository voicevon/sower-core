from enum import Enum

class CHESSBOARD_CELL_STATE(Enum):
    Empty = 1
    ForPlanning = 2
    PlannedToDrop = 3

class ChessboardCell():
    '''
    Empty  ---> filled_no_plan ---> planed_to_drop
     ^                                   |
     |-----------------------------------|    
    '''
    def __init__(self):
        self.state = CHESSBOARD_CELL_STATE.Empty # Empty, filled_no_plan, planned_to_drop, 

class CHESSBOARD_ROW_STATE(Enum):
    Unplanned = 1
    PlannedToDrop = 2
    Executing = 3
    Executed = 4

class ChessboardRow():
    def __init__(self):
        self.state = CHESSBOARD_ROW_STATE.Unplanned  # Unplanned, Planed, Executing, Executed
        self.planned_action = 0
        
    def set_plan(self,action):
        self.planned_action = action

class Chessboard():
    '''
    The Chessboard is a 2D  array .
        Rows from right to left
        Cols from top to bottom
             (3,0), (2,0), (1,0), (0,0)   
                                  (0,1)
                                  (0,2)
                                 ......
                                  (0,7)
    '''
    def __init__(self):
        # self.rows = list(ChessboardRow)
        self.rows = []

    def get_one_empty_cell(self):
        row_id = 0
        col_id = 2
        if True:
            return row_id, col_id
        
        return None

    def get_one_empty_row_id(self):
        empty_col_id = -1
        if True:
             empty_col_id =7
        
        return empty_col_id

    def set_one_cell(self, row_id, col_id):

        rowl_map = self.rows[row_id]
        rowl_map |= 1 << col_id
        self.rows[row_id]= rowl_map

