import serial, time
from global_const import app_config


class ServoArrayDriver():

    def __init__(self):
        self.__COLS = 8
        self.__ROWS = 3
        self.__rows_range = range(0, self.__ROWS)
        self.__cols_range = range(0, self.__COLS)
        self.chessboard_map = [[0] for i in self.__rows_range]
        self.__serialport = serial.Serial()
        self.__echo_is_on = False

    def connect_serial_port(self, serial_port_name, baudrate,echo_is_on):
        self.__serialport.port = serial_port_name
        self.__serialport.baudrate = baudrate
        self.__serialport.timeout = 1
        self.__serialport.writeTimeout = 2
        self.__serialport.open()
        self.__echo_is_on = echo_is_on

        if self.__echo_is_on:
            if self.__serialport.is_open:
                print ('Minghao servos::Serial port is opened.')
            else:
                print ('Minghao servos::Serial port is NOT  opened.')

    def set_echo_on(self, is_on):
        self.__echo_is_on = is_on

    def write_string(self, raw_string):
        self.__serialport.write(str.encode(raw_string +'\r\n'))
        if self.__echo_is_on:
            print ('>>> %s' % raw_string)

    def write_bytes(self, bytes_array):
        self.__serialport.write(bytes_array)

    def read_serial(self):
        # check what is received from serial port
        # response_a = self.__serialport.readline()
        # response_a = self.__serialport.read_all()
        # response_a = self.__serialport.readall()
        response_a = self.__serialport.read(size=1)
        listTestByte = list(response_a)
        print('>>>>>><<<<<<<' , len(response_a),listTestByte)

        response = bytes.decode(response_a)
        print('>>>>>>>%s<<<<<<<' % response)

    def send_new_plate_map(self, plate_map):
        # send map via serial port
        self.__serialport.write_string(plate_map)
    
    def on_received_chessboard_map(self, received_line):
        '''
        receive from serial port
        '''
        for row_id in self.__rows_range:
            self.chessboard_map[row_id] = received_line[row_id]

    def get_first_empty_cell(self):
        for row_id in self.__rows_range:
            for col_id in self.__cols_range:
                flag = self.chessboard_map[row_id] & 1 << col_id
                if flag:
                    return row_id, col_id
        return (-1,-1)

    def spin_once(self):
        self.read_serial()

    def spin(self):
        while True:
            self.read_serial()

if __name__ == "__main__":
    tester = ServoArrayDriver()
    tester.connect_serial_port('/dev/ttyUSB1', 115200, echo_is_on=False)
    tester2 = ServoArrayDriver()
    tester2.connect_serial_port('/dev/ttyUSB0', 115200, echo_is_on=False)
    while True:
        tester2.write_string('abc  ')
        tester.spin_once()
        tester2.spin()