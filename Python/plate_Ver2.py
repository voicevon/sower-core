

# from servos import Servos_action

from enum import Enum


class PlateRow():
    '''
    Composed by an list of cells
    '''
    def __init__(self):
        # self.cells=list(PlateCell)
        self.cells=[]
        self.config_cols_lenth = 8


    def from_row_map(self, row_map):
        for i in range(0,len(row_map)):
            cell = PlateCell()
            cell.from_cell_map(row_map[i])
            self.cells.append(cell)  
    
    def print_out(self, string_head, string_tail):
        out = string_head
        for cell in self.cells:
            out += cell.to_string()
        out += string_tail
        print(out)


class Plate_Ver2():
    '''
    A plate is composed by array of PlateRows
    '''
    def __init__(self):
        # self.rows = list(PlateRow)
        self.__ROWS = 16
        self.__rows_range = range(0,self.__ROWS)
        self.rows = [(PlateRow()) for i in self.__rows_range]


    def from_map(self, cells_map): 
        i = 0
        for row in self.rows:
            row.from_row_map(cells_map[i])
            i += 1

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

    def get_window_map(self, target_row):
        range_max = target_row
        range_min = target_row - 2
        if range_min < 0:
            range_min = 0
        return range(range_min, range_max)

    def executed_dropping(self,row_id,dropped_map):
        '''
        update plate_map after dropping
        '''
        self.rows[row_id] |= dropped_map
         


if __name__ == "__main__":
    plate = Plate_Ver2()
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