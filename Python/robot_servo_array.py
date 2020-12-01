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
        # self.__chessboard_map = [[0] for i in self.__rows_range]
        self.__chessboard_map = [0 for i in self.__rows_range]
        self.__minghao_chessboard_map = [0 for i in self.__rows_range]
        # self.__edges_of_updating_pre_feeded = [0,0,0]
        self.__edges_unsynced = [0,0,0]
        self.__edges_syncing = [0,0,0]

        self.__chessboard_is_initialized_from_minghao = False
        self.__serialport = serial.Serial()
        self.__echo_is_on = False
        self.__spinning = False
        self.plate_id = 1
        self.controller_got_ok = False
        self.__current_plate_map = [0xff for i in range(0,16)]

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
    
    # def get_edges(self):
    #     '''
    #     For sending via serial port
    #     get data from self.__edges_unsynced
    #     '''
    #      self.__edges_unsynced 
    
    def __reset_sync_download_data(self):
        '''
        Will be invoked after receiving from minghao's controller.
        After this functin invoked, please call transfer_edges_from_unsynced_to_synced() ??
        '''
        # transfer edges from unsynced to syncing
        for row_id in range(0,3):
            self.__edges_syncing[row_id] += self.__edges_unsynced[row_id]
        # clear unsynced
        self.__edges_unsynced = [0,0,0]

    def write_via_serial_port(self, plate_id):
        # print('merged_map=' , merged_map)
        data = self.__current_plate_map + self.__edges_syncing
        output = [0xaa, 0xaa, plate_id ]
        output += data  # 19 bytes
        output += self.__get_crc16_list(output)
        output += [0x0d, 0x0a]
        print('>>>>>>>>>>  ',output)
        self.__serialport.write(output)
        if self.__echo_is_on:
            print('>>>' + str(output))

    def send_new_platmap(self, plate_map):
        self.plate_id += 1
        if self.plate_id >9:
            self.plate_id = 1
            
        self.__current_plate_map = plate_map
        # self.__current_plate_map = [0x00,0x00,0x00,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff]
        # self.inform_minghao_placed_one_cell(-1,-1)
        self.write_via_serial_port(self.plate_id)

    def get_first_empty_cell(self):
        print ('calling get_empty_cell()')
        print('My chessboard map', self.__chessboard_map)
        for row_id in self.__rows_range:
            for col_id in self.__cols_range:
                flag = self.__chessboard_map[row_id] & (1 << col_id)
                if not flag:
                    # 1 == True == There is a seed in cell
                    # 0 == False == Cell is empty.
                    print ('empty cell at ', row_id, col_id)
                    return row_id, col_id

        return (-1,-1)

    def update_chessmap_from_xyz_arm(self, col_id, row_id):
        self.__chessboard_map[row_id] += 1 << col_id
        # append_edges_unsynced
        self.__edges_unsynced[row_id] += 1 << col_id
        print('update_my_chessbaord_map', self.__chessboard_map)
        print('unsynced edges =', self.__edges_unsynced)
        print('syncing edges =', self.__edges_syncing)

    def update_chessmap_from_minghao_controller(self):
        # update chessboard_map from minghao's controller, Only from one to zero is acceptable.
        # if there is update, return True
        print('mymap-------------------------------------------',self.__chessboard_map)
        for row_id in range(3):
            if self.__chessboard_map[row_id] != self.__minghao_chessboard_map[row_id]:
                mask = self.__chessboard_map[row_id] ^ self.__minghao_chessboard_map[row_id]
                mask &= self.__chessboard_map[row_id]  # mask is the number that bits from one to zero 
                mask = - mask -1   # from 0b0000-0001 to 0b1111-1110 
                print('mask' , mask)
                self.__chessboard_map[row_id] &= mask
        #         return True  
        # return False

    def spin_once(self):
        # print('>>>    ' ,self.__chessboard_map)
        time.sleep(0.5)   # TODO: async from os time, if not achive 0.5s, just return
        # self.inform_minghao_placed_one_cell(-1,-1)
        self.__reset_sync_download_data()
        self.write_via_serial_port(self.plate_id)
        controller_response = self.__serialport.read(size=11)
        controller_response2 = self.__serialport.read(size=11)
        if len(controller_response2) > 0:
            print('22222222222222222222222222222222222222222222222222222222222222', controller_response2)
        # controller_response = self.__serialport.read(size=11)
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
                        self.update_chessmap_from_minghao_controller()
                        self.__edges_syncing = [0,0,0]
                        if not self.__chessboard_is_initialized_from_minghao:
                            self.__chessboard_map[0] = xx[4]
                            self.__chessboard_map[1] = xx[5]
                            self.__chessboard_map[2] = xx[6]
                            self.__chessboard_is_initialized_from_minghao = True
                            # if self.__echo_is_on:
                        # print('minghao got map, feed back a OK...')
                        if self.__chessboard_map[0] != 0xff or self.__chessboard_map[1] != 0xff or self.__chessboard_map[2] != 0xff:
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
            #     self.__chessboard_map[0] = xx[2]
            #     self.__chessboard_map[1] = xx[3]
            #     self.__chessboard_map[2] = xx[4]
            #     print(self.__chessboard_map)
            #     crc_high, crc_low = xx [5:7]
            #     ender = xx[7:9]
        else:
            print(TerminalFont.Color.Fore.yellow +  'minghao spin_once().  timeout , no response' + TerminalFont.Color.Control.reset)

            

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
    # tester.inform_minghao_placed_one_cell(1,2)
    tester.write_dual_map_via_serial_port(1)
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
        tester.write_dual_map_via_serial_port(plate_id=tester.plate_id, merged_map = map)
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