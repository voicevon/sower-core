import sys
# sys.path.append('C:\\gitlab\\bot\\python\\reprap')  # on windows
# sys.path.append('/home/xm/gitrepo/bot/python/reprap')   # on linux
# sys.path.append('/home/znkzjs/bot/python/reprap')   # on Jetson Nano user
# sys.path.append('/home/xm/gitrepo/bot/python/reprap')   # on Jetson Nano xuming

sys.path.append('/home/xm/pylib')
# from singleton import Singleton
from app_config import AppConfig
from mqtt_helper import g_mqtt
from reprap_arm import ReprapArm

import time
from  threading import Thread

# class XyzArm(ReprapArm, metaclass=Singleton):
class XyzArm(ReprapArm):
    '''
    This robot arm is a human level robot.
    Warehouse postion: When idle, it's at bottom.
    '''
    def __init__(self, body_id):
        ReprapArm.__init__(self)
        self.__placed_counter = 0
        if body_id==0x41:
            self.__WAREHOUSE_X_POS = 180
            self.__DISTANCE_X_FROM_ROW_0_TO_WAREHOUSE = 132
            self.__DISTANCE_Y_FROM_COL_7_TO_HOME = 10
        if body_id==0x42:
            self.__WAREHOUSE_X_POS = 180
            self.__DISTANCE_X_FROM_ROW_0_TO_WAREHOUSE = 132
            self.__DISTANCE_Y_FROM_COL_7_TO_HOME = 15

    def connect_and_init(self, serial_port_name):
        ReprapArm.connect_reprap_controller(self, portname= serial_port_name, baudrate=115200)
        self.allow_cold_extrusion()
    
    # TODO: Check whether or not can remove this wrapper.
    def wait_for_movement_finsished_wrapper(self):
        self.wait_for_movement_finsished()

    def home_y_x(self):
        self.home(home_y=True)
        self.home(home_x=True)

    def __get_xy_from_col_row(self, col, row):
        '''
        Y+
        ^
        |      col=0
        |      col=1
        |      ...
        |      ...
        |      col=5
        |      col=6
        |      col=7
        |----- row=1,  row=0 ... ---------------> X+
        if row == -1, will return x position of warehouse

        From manual calibration:  col,row :(0,0)  maps to x,y (30,20)
        '''
        x = self.__DISTANCE_X_FROM_ROW_0_TO_WAREHOUSE - row * 32
        y = self.__DISTANCE_Y_FROM_COL_7_TO_HOME + (7-col) * 32
        if row == -1:
            x = self.__WAREHOUSE_X_POS
        return x, y

    def lift_warehouse(self):
        '''
        Wiring:  fan interface to control warehouse
        '''
        self.wait_for_movement_finsished()
        self.bridge_send_gcode_mcode('M106 S255')

    def drop_warehouse(self):
        self.wait_for_movement_finsished()
        self.bridge_send_gcode_mcode('M106 S0')

    
    def pickup_from_warehouse(self, col):
        WAREHOUSE_MOVEMENT_TIME = 1.5   # when warehouse moves from bottom to top(or reverse), will cost some time. 

        # move_to_warehouse(col)
        x, y = self.__get_xy_from_col_row(col=col, row=-1)
        self.move_to_xyz(x, y,speed_mm_per_min=18000)
        self.__current_y = y

        self.lift_warehouse()
        time.sleep(WAREHOUSE_MOVEMENT_TIME)
        self.drop_warehouse()
        time.sleep(WAREHOUSE_MOVEMENT_TIME /3 )

    def place_to_cell(self, col, row):
        '''
        A certain path, that based on cell position.
        Basically, The path looks like this, total composed from 3 segments

        (x,y+32)-------------------------->(WAREHOUSE_X_POS,y+32)
          |
          |
        (x,y) <--------------------------- (WAREHOUSE_X_POS,y)
        '''
        x, y = self.__get_xy_from_col_row(col,row)
        self.move_to_xyz (x , y )
        self.move_to_xyz(x , y+32,speed_mm_per_min= 3500)
        self.move_to_xyz(self.__WAREHOUSE_X_POS, y+32,speed_mm_per_min=15000)

        self.__placed_counter += 1
        g_mqtt.publish('sower/xyzarm/placed_counter', self.__placed_counter)

    def pickup_then_place_to_cell(self, col, row):
        self.pickup_from_warehouse(row)
        self.place_to_cell(col, row)

    def spin(self):
        t = Thread(target=self.__main_task_loop)
        t.start()

    def __main_loop(self):
        while True:
            self.spin_once()

    def spin_once(self):
        '''
        # This is mainly for debugging. do not use while loop in this function!
        # For better performance, invoke spin() instead. 
        # 
        # Check feeding_buffer is there any cave is empty
        '''
        col, row  = self.__target_plate.find_empty_cell()
        if col is not None:
            self.__robot .place_to_cell(col, row)
            self.__robot.pickup_from_warehouse(row)

    def calibrate_col_row(self, col, row):
        x, y = self.__get_xy_from_col_row(col, row)
        # x, y = (180,180)
        self.move_to_xyz(x, y, speed_mm_per_min=18000)



if __name__ == "__main__":
    my_arm = XyzArm(0x41)
    # my_arm.set_echo_on(True)
    my_arm.connect_and_init('/dev/ttyUSB1')
    my_arm.home_y_x()
    
    if True:
        my_arm.calibrate_col_row(0,0)

    if False:
        # moves a big squre/
        MAX_SPEED = 18000
        while True:
            my_arm.move_to_xyz(90, 10, 0, MAX_SPEED)
            my_arm.move_to_xyz(90, 280, 0, MAX_SPEED)
            my_arm.move_to_xyz(180, 280, 0, MAX_SPEED)
            my_arm.move_to_xyz(180, 10, 0, MAX_SPEED)

    if False:
        # test warehouse
        while True:
            my_arm.lift_warehouse()
            time.sleep(2)
            my_arm.drop_warehouse()
            time.sleep(3)

    if False:
        while True:
            for col_id in range(7,-1,-1):
                for row_id in range(0,2):
                    my_arm.pickup_from_warehouse(col_id)
                    my_arm.place_to_cell(col_id, row=row_id)



    # my_arm.Init_Marlin()
    # my_arm.Test2_home_sensor()
    # my_arm.set_fan_speed()


