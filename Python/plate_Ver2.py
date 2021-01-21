

# from servos import Servos_action

from enum import Enum


class Plate_Ver2():
    '''
    A plate is composed by array of PlateRows
    '''
    def __init__(self):
        self.__ROWS = 16
        self.__rows_range = range(0,self.__ROWS)
        self.rows = [0xfe,0xff,0xff,0xff,  0xff,0xff,0xff,0xff,
                    0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff]
        '''
        bit defination: 0 = Empty  ,  1 = Occupied
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
        for col_id in range(0,8):
            col_map = ''
            for row_id in range(self.__ROWS-1,-1,-1):
                byte = self.rows[row_id]
                if (byte & (1<<col_id)) == 0:
                    col_map += ' .'
                else:
                    col_map += ' X'
            print (col_map)        

    def get_window_map(self, start_row_id):
        window = [0x00,0x00]
        # print('Plate_Ver2.get_window_map(): start_row_id= ', start_row_id)
        window[0] = self.rows[start_row_id]
        if start_row_id<15:
            window[1] = self.rows[start_row_id + 1]
        else:
            window[1] = 0xff   # 1 is occupied
        return window

    def update_with_dropping(self,row_id,dropped_map):
        '''
        update plate_map after dropping
        '''
        self.rows[row_id] |= dropped_map[0]
        if row_id <15:
            self.rows[row_id+1] |= dropped_map[1]

         


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
    map = [0xfe,0x55,0xff,0xff,  0xff,0xff,0xff,0xff,
           0xff,0xff,0xff,0xff,  0xff,0xff,0xff,0xaa]
    plate.from_map(map)
    plate.print_out_map()
    # while True:
    #     plate.main_loop()