import serial, time
from app_config import AppConfig
from  threading import Thread
from crccheck.crc import Crc16Modbus  #pip3 install crccheck
import sys
sys.path.append('/home/znkzjs/pylib')
from terminal_font import TerminalFont

# https://electronics.stackexchange.com/questions/109631/best-way-to-do-i2c-twi-over-long-distance
class ServoArrayDriver():

    def __init__(self):
        self.__COLS = 8
        self.__ROWS = 3
        self.__rows_range = range(0, self.__ROWS)
        self.__cols_range = range(0, self.__COLS)
        self.chessboard_map = [[0] for i in self.__rows_range]
        self.__serialport = serial.Serial()
        self.__echo_is_on = False
        self.__spinning = False
        self.plate_id = 0
        self.controller_got_ok = False

    def connect_serial_port(self, serial_port_name, baudrate,echo_is_on):
        self.__serialport.port = serial_port_name
        self.__serialport.baudrate = baudrate
        self.__serialport.timeout = 0.5
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
        if self.__echo_is_on:
            print('>>>' + str(bytes_array))

    def __get_crc16_list(self, origin):
        # origin_bytes is an bytes list
        crc16 = Crc16Modbus()
        origin_tuple = tuple(origin)
        # print(origin_tuple)
        crc16.process(origin_tuple)
        crc16_bytes = list(crc16.finalbytes())
        crc16_bytes.reverse()
        # print('crc16_bytes= ',crc16_bytes)
        return crc16_bytes

    def send_plate_map(self, plate_id, plate_map):
        output = [0xaa, 0xaa, plate_id ]
        output += plate_map  # 16 bytes
        output += self.__get_crc16_list(output)
        output += [0x0d, 0x0a]
        self.write_bytes(output)

    def send_chessboard_map(self, chessboard_map):
        output = [0xaa,0xbb]
        output += chessboard_map  # 3 bytes
        output += self.__get_crc16_list(output)
        output += [0x0d, 0x0a]
        self.write_bytes(output)

    def request_chessboard_map(self):
        output = [0xaa, 0xcc]
        output += self.__get_crc16_list(output)
        output += [0x0d, 0x0a]
        self.write_bytes(output)
        
    def get_first_empty_cell(self):
        for row_id in self.__rows_range:
            for col_id in self.__cols_range:
                flag = self.chessboard_map[row_id] & 1 << col_id
                if flag:
                    return row_id, col_id
        return (-1,-1)

    def spin_once(self):
        # self.request_chessboard_map()
        # check what is received from serial port
        controller_response = self.__serialport.readline()
        if len(controller_response) > 0:
            xx = list(controller_response)
            # print(xx)
            # print(xx[0:2])
            if xx[0:2] == [0xaa,0xaa]:
                if len(xx) == 6:
                    # The controller got plate map
                    plate_id = xx[2]
                    result = xx[3]
                    ender = xx[4:6]   # 0x0d,0x0a
                    if result == 0x01:
                        self.controller_got_ok = True
                        print('minghao got map, feed back a OK...')
                    else:
                        print(TerminalFont.Color.Fore.red + 'minghao said something is wrong!!!!!' + TerminalFont.Control.reset)
                else:
                    print(TerminalFont.Color.Fore.red + 'Plate map lenth wrong , the received bytes length  = %d' % len(xx) + TerminalFont.Control.reset)

            elif xx[0:2] == [0xaa,0xbb]:
                # The controller got chessboard map
                result = xx[2]
                ender = xx[3:5]   # 0x0d,0x0a

            elif xx[0:2] == [0xaa,0xcc]:
                # controller respomnse the chessboard map
                self.chessboard_map[0] = xx[2]
                self.chessboard_map[1] = xx[3]
                self.chessboard_map[2] = xx[4]
                print(self.chessboard_map)
                crc_high, crc_low = xx [5:7]
                ender = xx[7:9]
    
    def __main_loop_new_threading(self):
        while True:
            self.spin_once()
            # time.sleep(0.02)

    def spin(self):
        '''
        Will not block invoker
        '''
        if not self.__spinning:
            t = Thread(target=self.__main_loop_new_threading)
            t.start()
            self.__spinning = True

if __name__ == "__main__":
    tester = ServoArrayDriver()
    tester.connect_serial_port('/dev/ttyUSB1', 115200, echo_is_on=False)
    # tester.spin()


    # tester2 = ServoArrayDriver()
    # tester2.connect_serial_port('/dev/ttyUSB0', 115200, echo_is_on=False)
    # while True:
    #     tester.write_bytes([0xcc])
    #     time.sleep(1)
    #     tester.write_bytes([0xbb])
    #     time.sleep(1)
    #     tester.spin_once()
    #     # tester2.spin_once()

    map1=[0x55,0xaa,0xff,0x55,0xaa,0xff,0xff,0x55,     0xaa,0xff,0xff,0xff,0xff,0xff,0xff,0xff]
    map1.reverse()
    map2=[0,0xff, 0xff]
    while True:
        # tester.send_plate_map(plate_id=1, plate_map = map1)
        tester.send_plate_map(plate_id=tester.plate_id, plate_map = map1)
        print('sending.............')
        # tester.send_chessboard_map(map2)
        tester.spin_once()
        if tester.controller_got_ok:
            print('Plate_id = %d' %tester.plate_id)
            time.sleep(1)
            tester.plate_id += 1
            if tester.plate_id > 255:
                tester.plate_id = 0
            if tester.plate_id == 10:
                tester.plate_id += 1
            tester.controller_got_ok = False
        else:
            time.sleep(0.5)