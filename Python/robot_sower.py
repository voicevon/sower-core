import sys
sys.path.append('/home/xm/gitrepo/pylib')
from app_config import AppConfig
from devices_helper import DevicesHelper

from robot_sensors import RobotSensors
from robot_eye import RobotEye
from plate_Ver2 import Plate_Ver2
from robot_body import RobotBody



import Jetson.GPIO as GPIO
import board  # pip3 install adafruit-blinka
import busio
import threading


class RobotSower():
    # '''
    # There are two RobotBody()
    # each body have a set of XYZ_arm + servo_gates + current_plate,  we call it RobotBody
    # '''


    def __init__(self):
        self.__eye = RobotEye()
        helper = DevicesHelper()
        helper.serial_port_list_all()

        self.__current_plate = Plate_Ver2()
        self.__next_plate = Plate_Ver2() # Current version , we don't apply this.
        
        self.__sensors = RobotSensors(self.__on_new_row_enter)
        self.__sensors.setup()

        i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1,frequency=400000))
        xyz_arm_serial_port_name = helper.serial_port_from_location('1-2.1.1')
        self.__first_robot_body = RobotBody(xyz_arm_serial_port_name, i2c_bus0, 0x41)

        xyz_arm_serial_port_name = helper.serial_port_from_location('1-2.1.3')
        self.__second_robot_body = RobotBody(xyz_arm_serial_port_name, i2c_bus0, 0x42)  

    def on_eye_got_new_plate(self, plate_map):

        self.__current_plate.from_map(plate_map)

    def __new_row_enter_first_robot_body(self, row_id):
        if row_id >= 0:
            # get plan for the two rows of the first robot.
            plan = self.__current_plate.get_window_map(row_id)
            # execute the plan, This will update the plate map.
            action_map = self.__first_robot_body.execute_dropping(plan)
            self.__current_plate.update_dropping(row_id, action_map)

    def __new_row_enter_second_robot_body(self, row_id):
        if row_id >= 0:
            # get plan for the two rows of the first robot.
            plan = self.__current_plate.get_window_map(row_id)
            # execute the plan, This will update the plate map.
            action_map = self.__second_robot_body.execute_dropping(plan)
            self.__current_plate.update_dropping(row_id,action_map)

    def __on_new_row_enter(self):
        '''
        Should be a new thread.
        '''
        print("RobotSower.__on_new_row_enter()  comming row_id = ", self.__sensors.coming_row_id_to_first_robot_body, self.__sensors.coming_row_id_to_second_robot_body)
        row_id_first = self.__sensors.coming_row_id_to_first_robot_body
        row_id_second = self.__sensors.coming_row_id_to_second_robot_body
        if AppConfig.multi_thread:
            t1 = threading.Thread(target=self.__new_row_enter_first_robot_body, args=[row_id_first])
            t2 = threading.Thread(target=self.__new_row_enter_second_robot_body, args=[row_id_second])
            t1.start()
            t2.start()
        else:
            self.__new_row_enter_first_robot_body(row_id_first)
            self.__new_row_enter_second_robot_body(row_id_second)

        # can report the sower result here   
        

    def turn_on_light_fan_conveyor(self):
        self.__sensors.output_conveyor_motor(1)
        self.__sensors.output_vacuum_fan(1)
        self.__sensors.ouput_light(1)

    def spin_once(self):
        self.__first_robot_body.spin_once(new_thread=AppConfig.multi_thread)
        self.__second_robot_body.spin_once(new_thread=AppConfig.multi_thread)
        self.__eye.spin_once()



if __name__ == "__main__":
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)

    t = RobotSower()
    t.turn_on_light_fan_conveyor()