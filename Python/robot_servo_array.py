import serial, time
from app_config import AppConfig
from  threading import Thread
from crccheck.crc import Crc16Modbus  #pip3 install crccheck
import sys
sys.path.append('/home/xm/pylib')
from terminal_font import TerminalFont
from robot_sensors import RobotSensors

# https://electronics.stackexchange.com/questions/109631/best-way-to-do-i2c-twi-over-long-distance
class ServoArrayDriver():

    def __init__(self):
        self.__COLS = 8
        self.__ROWS = 3
        self.__rows_range = range(0, self.__ROWS)
        self.__cols_range = range(0, self.__COLS)
        # self.chessboard_map = [[0] for i in self.__rows_range]
        self.chessboard_map = [0 for i in self.__rows_range]
        self.__minghao_chessboard_map = [0 for i in self.__rows_range]
        self.__chessboard_is_initialized_from_minghao = False
        self.__serialport = serial.Serial()
        self.__echo_is_on = False
        self.__spinning = False
        self.plate_id = 1
        self.controller_got_ok = False
        self.__current_plate_map = [0 for i in range(0,16)]

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
    
    def send_dual_map(self, plate_id, merged_map):
        # print('merged_map=' , merged_map)
        output = [0xaa, 0xaa, plate_id ]
        output += merged_map  # 19 bytes
        output += self.__get_crc16_list(output)
        output += [0x0d, 0x0a]
        print('>>>>>>>>>>  ',output)
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
                flag = self.chessboard_map[row_id] & (1 << col_id)
                if not flag:
                    # 1 == True == There is a seed in cell
                    # 0 == False == Cell is empty.
                    return row_id, col_id
        return (-1,-1)

    def inform_minghao_placed_one_cell(self, col_id,row_id):
        if col_id >= 0:
            # there is some change for cell status
            # but still need feed back from minghao controller. so do not update self.chessboard_map
            self.chessboard_map[row_id] += 1<<col_id
            # self.__synced_from_minghao = False
            return
            # pass
        
        dual_map = self.__current_plate_map + self.chessboard_map
        self.send_dual_map(self.plate_id, dual_map)

    def send_new_platmap(self, plate_map):
        self.plate_id += 1
        if self.plate_id >9:
            self.plate_id = 1
            
        self.__current_plate_map = plate_map
        self.__current_plate_map = [0x55,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff]
        self.inform_minghao_placed_one_cell(-1,-1)


    def compare_chessboard_map(self):
        for row_id in range(3):
            if self.chessboard_map[row_id] != self.__minghao_chessboard_map[row_id]:
                mask = self.chessboard_map[row_id] ^ self.__minghao_chessboard_map[row_id]
                mask &= self.chessboard_map[row_id]  # mask is the number that bits from one to zero 
                mask = - mask -1   # from 0b0000-0001 to 0b1111-1110 
                print('mask' , mask)
                self.chessboard_map[row_id] &= mask
                return False  
        return True

    def spin_once(self):
        print('-------------------------------------------------------------------------------------------------------------------------')
        # print('>>>    ' ,self.chessboard_map)
        time.sleep(0.5)   # TODO: async from os time, if not achive 0.5s, just return
        self.inform_minghao_placed_one_cell(-1,-1)
        controller_response = self.__serialport.read(size=11)
        if len(controller_response) > 0:
            xx = list(controller_response)
            print('++++++++++++++++++  ' ,len(xx),xx)
            # print(xx[0:2])
            if xx[0:2] == [0xaa,0xaa]:
                if len(xx) == 11:
                    # The controller got plate map
                    plate_id = xx[2]  # 1..10
                    result = xx[3]  # 1 / 0
                    self.__minghao_chessboard_map = xx[4:7]
                    # self.__synced_from_minghao = False
                    crc = xx[7:9]  
                    ender = xx[9:11]   # 0x0d,0x0a
                    if result == 0x01:
                        self.controller_got_ok = True
                        if not self.__chessboard_is_initialized_from_minghao:
                            self.chessboard_map[0] = xx[4]
                            self.chessboard_map[1] = xx[5]
                            self.chessboard_map[2] = xx[6]
                            self.__chessboard_is_initialized_from_minghao = True
                        # if self.__echo_is_on:
                        print('minghao got map, feed back a OK...')
                        print("minghao's chessboard_map = " ,self.__minghao_chessboard_map)

                    else:
                        print(TerminalFont.Color.Fore.red)
                        print(xx )
                        print(TerminalFont.Color.Fore.red + 'minghao said something is wrong!!!!!' + TerminalFont.Color.Control.reset)
                else:
                    print(TerminalFont.Color.Fore.red + 'Plate map lenth wrong , the received bytes length should be 11, but is  = %d' % len(xx))
                    print(xx)
                    print(TerminalFont.Color.Control.reset)

            else:
                print(TerminalFont.Color.Fore.red + 'Packet length is OK, but lost protocol head')
                print(xx)
                print(TerminalFont.Color.Control.reset)
            # elif xx[0:2] == [0xaa,0xbb]:
            #     # The controller got chessboard map
            #     result = xx[2]
            #     ender = xx[3:5]   # 0x0d,0x0a

            # elif xx[0:2] == [0xaa,0xcc]:
            #     # controller respomnse the chessboard map
            #     self.chessboard_map[0] = xx[2]
            #     self.chessboard_map[1] = xx[3]
            #     self.chessboard_map[2] = xx[4]
            #     print(self.chessboard_map)
            #     crc_high, crc_low = xx [5:7]
            #     ender = xx[7:9]
        else:
            print(TerminalFont.Color.Fore.yellow +  'minghao spin_once().  timeout , no response' + TerminalFont.Color.Control.reset)

            
    def spin_once_version1(self):
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

    # def __main_loop_new_threading(self):
    #     while True:
    #         self.spin_once()
    #         # time.sleep(0.02)

    # def spin(self):
    #     '''
    #     Will not block invoker
    #     '''
    #     if not self.__spinning:
    #         t = Thread(target=self.__main_loop_new_threading)
    #         t.start()
    #         self.__spinning = True

def test1():
    pass
def test2():
    pass

if __name__ == "__main__":

    tester = ServoArrayDriver()
    col,row = tester.get_first_empty_cell()
    print(col,row)
    
    tester.connect_serial_port('/dev/ttyUSB1', 115200, echo_is_on=False)
    tester.inform_minghao_placed_one_cell(1,2)
    while True:
        tester.spin_once()


    # tester2 = ServoArrayDriver()
    # tester2.connect_serial_port('/dev/ttyUSB0', 115200, echo_is_on=False)
    # while True:
    #     tester.write_bytes([0xcc])
    #     time.sleep(1)
    #     tester.write_bytes([0xbb])
    #     time.sleep(1)
    #     tester.spin_once()
    #     # tester2.spin_once()

    map1=[0xf3,0xcf,0xff,0xff,0xff,0xff,0xff,0x3f,     0xff,0xff,0xff,0xff,0xf3,0xcf,0xff,0x3f]
    # map1=[0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5]
   # map1.reverse()
    map2=[0xff,0xff, 0xff]
    # map2=[0xff,2,3]
    map = map1 + map2
    while True:
        # tester.send_plate_map(plate_id=1, plate_map = map1)
        tester.send_dual_map(plate_id=tester.plate_id, merged_map = map)
        print('sending.............')
        # tester.send_chessboard_map(map2)
        tester.spin_once()
        if tester.controller_got_ok:
            print('Plate_id = %d' %tester.plate_id)
            time.sleep(15)
            tester.plate_id += 1
            if tester.plate_id > 9:
                tester.plate_id = 1
            tester.controller_got_ok = False
        else:
            time.sleep(0.5)