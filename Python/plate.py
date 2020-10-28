
#  Jetson Expansion Header Tool
#       sudo /opt/nvidia/jetson-io/jetson-io.py
#           from: https://www.jetsonhacks.com/2020/05/04/spi-on-jetson-using-jetson-io/



from enum import Enum
import Jetson.GPIO as GPIO

from servos import Servos_action


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


# class PLATE_ROW_STATE(Enum):
#     Unplanned_Or_OnPlanning = 1
#     Planned = 2
#     InBuffer = 3        # Plan becomes to Action.


class PlateRow():
    '''
    Composed by an list of cells
    '''
    def __init__(self, id):
        self.id = id
        # self.cells=list(bool)
        self.cells=[]
        self.config_cols_lenth = 8
        self.is_planned = False
        # for i in range(0, self.config_cols_lenth):
        #     self.cells.append(True)


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
    def __init__(self, callback_release_servos):
        # self.rows = list(PlateRow)
        self.rows = []
        self.state = PLATE_STATE.Started
        self.has_got_map = False
        self.callback_release_servos = callback_release_servos

        self.__PIN_IR_SWITCH = 37
        self.__PIN_ENCODER_A = 31
        self.__PIN_ENCODER_B = 32
        self.next_enter_row_id = 0
        self.encoder_distance = 0
        self.__encoder_distance_per_row = 200
        self.__plate_counter = 0

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.__PIN_IR_SWITCH, GPIO.IN)
        GPIO.setup(self.__PIN_ENCODER_A, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.__PIN_ENCODER_B, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        GPIO.add_event_detect(self.__PIN_IR_SWITCH, GPIO.RISING, callback=self.on_gpio_rising)
        # GPIO.add_event_detect(self.__PIN_ENCODER_A, GPIO.RISING, callback=self.on_encoder_rising)


    def on_gpio_rising(self, channel):
        if channel == self.__PIN_IR_SWITCH:
            self.encoder_distance = 0
            self.next_enter_row_id = 0
            self.__plate_counter += 1

        elif channel == self.__PIN_ENCODER_A:
            self.encoder_distance += 1
            if self.encoder_distance / self.__encoder_distance_per_row == 0:
                # current row must be fininshed. new row is coming
                self.callback_release_servos()  #TODO: new threading
                self.next_enter_row_id += 1

    def get_row_map(self, row_id):
        '''
        return an array of empty cells in a row.
        '''
        return self.rows[row_id]

    def from_map(self, cells_map): 
        # print(cells_map)
        self.rows=[]
        for i in range(0,len(cells_map)):
            row = PlateRow(i)
            row.from_row_map(cells_map[i])
            self.rows.append(row)
        self.state = PLATE_STATE.Mapped

    def print_out_map(self):
        for row in self.rows:
            row_id_string = str(row.id)
            if row.id <10:
                row_id_string = '0' + row_id_string 
            row.print_out(row_id_string + '--  ','')

    def get_unplanned_row_id(self):
        for row_id in range(0,16):
            if not  self.rows[row_id].is_planned:
                return row_id

    def get_shadow_rows(self, target_row):
        rows = []
        for row_id in range(target_row, target_row -3, -1):
            if row_id >= 0:
                rows.append(rows[row_id])

    def finished_plan_for_this_row(self, target_row_id):
        self.rows[target_row_id].planed = True


    def main_loop(self):
        # pass
        print('Plate_id, row_id, encoder_distance %i, %i, %i' %(self.__plate_counter, self.next_enter_row_id, self.encoder_distance))
        # print(GPIO.input(self.__PIN_IR_SWITCH))


if __name__ == "__main__":
    plate = Plate()
    plate.setup()
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
    while True:
        plate.main_loop()