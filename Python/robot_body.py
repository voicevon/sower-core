import threading
from robot_servo_kit import SowerServoKit
from robot_xyz_arm import XyzArm

class RobotBody():

    def __init__(self, body_name, xyz_arm_serial_port_name, i2c_bus, kit_address):
        self.__body_name = body_name
        self.xyz_arm = XyzArm()
        self.xyz_arm.connect_and_init(xyz_arm_serial_port_name)
        self.xyz_arm.home_y_x()
        self.servos_kit = SowerServoKit(body_name, i2c_bus, kit_address)
        self.seed_buffer = [0x00,0x00]   #bit defination: 0 = BLANK,  1 = OCCUPIED
        
    def execute_dropping(self, dropping_plan):
        '''
        
        '''
        # print('eeeeeeeeeeeeeeeeeeeeeeeeeee', dropping_plan)
        drop_map=[0x00,0x00]   #bit defination: 0 = No drop,   1 = dropped
        drop_map[0] = self.seed_buffer[0] & dropping_plan[0]
        drop_map[1] = self.seed_buffer[1] & dropping_plan[1]
        self.seed_buffer[0] &= drop_map[0]
        self.seed_buffer[1] &= drop_map[1]
        print('===================' , drop_map)
        self.servos_kit.execute_dropping(drop_map)
        return drop_map

    def get_first_empty_cell(self):
        '''
            return row_id, col_id. 
            If no empty cell, return -1, -1 
        '''
        for row_id in range(0,2):
            for col_id in range(0,8):
                if self.seed_buffer[row_id] & 1<<col_id == 0:
                    return row_id, col_id
        return -1,-1


    def __spin_once(self):
        row_id, col_id = self.get_first_empty_cell()
        if row_id >=0:
            self.xyz_arm.pickup_from_warehouse(col_id)
            self.xyz_arm.place_to_cell(row=row_id, col=col_id)
            self.seed_buffer[row_id] += 1<<col_id
    
    def spin_once(self, new_thread=True):
        if new_thread:
            t1 = threading.Thread(target=self.__spin_once)
            t1.start()
            return
        self.__spin_once()
