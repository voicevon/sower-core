import serial, time
from global_const import app_config


class ServoArrayDriver():

    class ServoArray_serial:
        '''
        Hand shaking with controller through serial port.
        '''
        def __init__(self, portname, baudrate, on_received_line):
            self.__serialport = serial.Serial()
            self.__serialport.port = portname
            self.__serialport.baudrate = baudrate
            self.__serialport.timeout = 1
            self.__serialport.writeTimeout = 2
            self.__counter = 0
            self.__echo_is_on = False
            self.__on_received_line = on_received_line

        def connect(self):
            self.__serialport.open()
            if self.__echo_is_on:
                print ('Reprap_host::Serial port is opened.')
            while True:
                xx = self.__serialport.readline()
                mm = bytes.decode(xx)
                if (mm == ''):
                    break

        def set_echo_on(self, is_on):
            self.__echo_is_on = is_on

        def write_string(self, raw_string):
            self.__counter += 1
            self.__serialport.write(str.encode(raw_string +'\r\n'))
            if self.__echo_is_on:
                print ('>>> %s' % raw_string)

        def write_bytes(self, bytes_array):
            self.__serialport.write(bytes_array)

        def main_loop(self):
            # check what is received from serial port
            response_a = self.__serialport.readline()
            response = bytes.decode(response_a)
            if(response == 'ok\n'):
                self.__on_received_line(response)

    def __init__(self):
        # self.ServoArray_serial.__init__('dev/ttyUSB1', 115200, self.on_received_chessboard_map)
        self.__COLS = 8
        self.__ROWS = 3
        self.__SERIAL_PORT_NAME = 'dev/ttyUSB1'
        self.__serial = self.ServoArray_serial(self.__SERIAL_PORT_NAME, 115200, self.on_received_chessboard_map)
        self.__serial.connect()

        self.__rows_range = range(0, self.__ROWS)
        self.__cols_range = range(0, self.__COLS)
        self.chessboard_map = [0, 0, 0]

    def send_new_plate_map(self, plate_map):
        # send map via serial port
        self.__serial.write_string(plate_map)
    
    def on_received_chessboard_map(self, received_line):
        '''
        receive from serial port
        '''
        for row_id in self.__rows_range:
            self.chessboard_map[row_id] = received_line[row_id]

    def inform_minghao(self, row_id, col_id):
        # update map
        self.chessboard_map[row_id] += 1 << col_id
        # send new map to sub system via serial port
        self.__serial.write_string(self.chessboard_map)
    
    def on_servo_updated(self, top_buffer_map):
        if True:
            # one or more cells are empty now, place a seed to the cell with xyz_arm
            col = top_buffer_map.col
            row = top_buffer_map.row
            self.__callback_fill_cell(col, row)

    def get_first_empty_cell(self):
        for row_id in self.__rows_range:
            for col_id in self.__cols_range:
                flag = self.chessboard_map[row_id] & 1 << col_id
                if flag:
                    return row_id, col_id
        return (-1,-1)

    def setup(self, callback_xyz):
        self.__callback_fill_cell = callback_xyz

    def spin_once(self):
        pass


if __name__ == "__main__":
    tester = ServoArrayDriver()