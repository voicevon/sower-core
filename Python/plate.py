

# from servos import Servos_action

from enum import Enum

class PLATE_CELL_STATE(Enum):
    Emppty_Unplanned = 1
    Empty_Planned = 2
    Prefilled = 3
    Refilled = 4

class PlateCell():
    def __init__(self):
        self.state = PLATE_CELL_STATE.Emppty_Unplanned

    def from_cell_map(self, cell_map):
        # at the moment , cell_map is bool
        if cell_map:
            self.state = PLATE_CELL_STATE.Emppty_Unplanned
        else:
            self.state = PLATE_CELL_STATE.Prefilled

    def to_string(self):
        table = {PLATE_CELL_STATE.Emppty_Unplanned:'. ',
                 PLATE_CELL_STATE.Empty_Planned: '= ',
                 PLATE_CELL_STATE.Prefilled: 'P ',
                 PLATE_CELL_STATE.Refilled: 'R '
                 }
        return table[self.state]


class PLATE_ROW_STATE(Enum):
    Unplanned_Or_OnPlanning = 1
    Planned = 2
    Executed = 3        # Plan becomes to Action.


class PlateRow():
    '''
    Composed by an list of cells
    '''
    def __init__(self):
        # self.cells=list(PlateCell)
        self.cells=[]
        self.config_cols_lenth = 8
        self.state = PLATE_ROW_STATE.Unplanned_Or_OnPlanning


    def from_row_map(self, row_map):
        for i in range(0,len(row_map)):
            cell = PlateCell()
            cell.from_cell_map(row_map[i])
            self.cells.append(cell)  
        self.state = PLATE_ROW_STATE.Unplanned_Or_OnPlanning   #????  
    
    def print_out(self, string_head, string_tail):
        out = string_head
        for cell in self.cells:
            out += cell.to_string()
        out += string_tail
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
        self.__ROWS = 16
        self.__rows_range = range(0,self.__ROWS)
        self.rows = [(PlateRow()) for i in self.__rows_range]
        self.state = PLATE_STATE.Started

        self.next_enter_row_id = 0
        self.__plate_counter = 0

    def is_empty_cell(self, row_id, col_id):
        if self.rows[row_id].cells[col_id].state == PLATE_CELL_STATE.Emppty_Unplanned:
            return True
        return False

    def set_cell_planned(self, row_id, col_id):
        self.rows[row_id].cells[col_id].state = PLATE_CELL_STATE.Empty_Planned

    def from_map(self, cells_map): 
        # print(cells_map)
        # for i in range(0,len(cells_map)):
        #     row = self.
        #     row.from_row_map(cells_map[i])
        #     self.rows.append(row)
        # self.state = PLATE_STATE.Mapped
        i = 0
        for row in self.rows:
            row.from_row_map(cells_map[i])
            i += 1
        self.state = PLATE_STATE.Mapped

    def to_map(self):
        map=[]
        for row_id in range(0, len(self.rows)):
            for col_id in range(0,8):
                map.append( self.rows[row_id].cells[col_id].state)
        return map

    def print_out_map(self):
        index = 0
        for row in self.rows:
            str_index = str(index)
            if index <10:
                str_index = '0' + str(index) 
            row.print_out(str_index + '--  ','')
            index += 1

    def get_first_unplanned_row_id(self):
        for row_id in range(0,16):
            if not  self.rows[row_id].is_planned:
                return row_id

    def get_shadow_rows_range(self, target_row):
        range_max = target_row
        range_min = target_row - 2
        if range_min < 0:
            range_min = 0
        return range(range_min, range_max)

    def finished_plan_for_this_row(self, target_row_id):
        self.rows[target_row_id].planed = True


    def main_loop(self):
        pass


if __name__ == "__main__":
    plate = Plate()
    map = [[True,True,True,True,False,True,False,True],
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
    plate.from_map(map)
    plate.print_out_map()
    # while True:
    #     plate.main_loop()