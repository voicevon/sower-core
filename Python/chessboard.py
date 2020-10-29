from enum import Enum

class CHESSBOARD_CELL_STATE(Enum):
    Empty = 1
    Unplanned = 2
    PlannedToDrop = 3
    Dropping = 4

class ChessboardCell():
    '''
    Empty  ---> Unplanned ---> planed_to_drop  ---> dropping
     ^                                                |
     |------------------------------------------------|    
    '''
    def __init__(self):
        self.state = CHESSBOARD_CELL_STATE.Empty # Empty, filled_no_plan, planned_to_drop, 

# class CHESSBOARD_ROW_STATE(Enum):

# class ChessboardRow():
#     def __init__(self):
#         # self.state = CHESSBOARD_ROW_STATE.Unplanned  # Unplanned, Planed, Executing, Executed
#         self.planned_action = 0
        
#     def set_plan(self,action):
#         self.planned_action = action

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
        # self.rows = list(ChessboardRow)
        self.cells = []
        # self.__row_id_to_be_planned = 0
        # self.size = (8,3)
        self.__row_range = range(0, 3)
        self.__col_range = range(0, 8)

    def get_one_empty_cell(self):
        for row_id in self.__row_range:
            for col_id in self.__col_range:
                if self.cells[row_id][col_id].state == CHESSBOARD_CELL_STATE.Empty:
                    return row_id, col_id
        return None

    def is_planned_cell(self, row_id, col_id):
        # for row_id in self.__row_range:
        #     for col_id in self.__col_range:
        if self.cells[row_id][col_id].state == CHESSBOARD_CELL_STATE.PlannedToDrop:
            return True
        else:
            return False

    def set_cell_planned(self, row_id, col_id):
        self.cells[row_id, col_id].state = CHESSBOARD_CELL_STATE.PlannedToDrop

    # def get_row_to_plan(self):
    #     return self.rows[self.__row_id_to_be_planned]

    # def get_next_empty_row_id_in_plan(self):
    #     empty_col_id = -1
    #     if True:
    #          empty_col_id =7
        
    #     return empty_col_id

    # def set_one_cell(self, row_id, col_id):

    #     rowl_map = self.rows[row_id]
    #     rowl_map |= 1 << col_id
    #     self.rows[row_id]= rowl_map

    def execute_plan(self):
        '''
        some cells becomes empty
        '''
        for row_id in range(0, 3):
            for col_id in range(0, 8):
                this_cell = self.cells[row_id][col_id]
                if this_cell.state == CHESSBOARD_CELL_STATE.PlannedToDrop:
                    this_cell.state = CHESSBOARD_CELL_STATE.Empty


    # def on_servos_released(self, bytes):

            
