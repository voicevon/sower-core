

# from servos import Servos_action

from enum import Enum


class Plate_Ver2():
    '''
    A plate is composed by array of PlateRows
    '''
    def __init__(self):
        self.__ROWS = 16
        self.__rows_range = range(0,self.__ROWS)
        self.rows = [0x00,0x00,0x00,0x00,  0x00,0x00,0x00,0x00,  0x00,0x00,0x00,0x00,  0x00,0x00,0x00,0x00]
        '''
        bit defination: 0 = Empty,  1 = Occupied
        '''


    def from_map(self, rows_map): 
        for i in range(0,self.__ROWS):
            self.rows[i] = rows_map[i]

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

    def update_dropping(self,row_id,dropped_map):
        '''
        update plate_map after dropping
        '''
        self.rows[row_id] |= dropped_map[0]
        self.rows[row_id+1] = dropped_map[1]

         


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