
#  Jetson Expansion Header Tool
#       sudo /opt/nvidia/jetson-io/jetson-io.py
#           from: https://www.jetsonhacks.com/2020/05/04/spi-on-jetson-using-jetson-io/


# Length = 1440*2 + 100 = 2980
# Expected = 93

from enum import Enum
import Jetson.GPIO as GPIO
import time
import os
class RobotSensors():

    # def __init__(self, on_new_plate_enter, on_new_row_enter):
    def __init__(self, on_new_row_enter):
        self.__PIN_IR_SWITCH = 37    # confirmed 33
        self.__PIN_ENCODER_C = 33    # 29 or 37
 

        self.__PIN_CONVEYOR_MOTOR = 15
        self.__PIN_VACUUM_FAN = 13 
        self.__PIN_LIGHTER = 7

        # self.__on_new_plate_enter = on_new_plate_enter
        self.__on_new_row_enter = on_new_row_enter

        self.__encoder_distance = 0
        self.__current_plate_enter_point = 0
        self.__next_plate_enter_point = 0
        self.coming_row_id_to_first_robot_body  = -100_000
        self.coming_row_id_to_second_robot_body = -100_000
        self.__current_speed = 30
        self.__debug_ir_count = 0
        '''
        unit is mm/second
        '''


    def setup(self, calibrate_mode=False):
        GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.__PIN_IR_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.__PIN_ENCODER_C, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.__PIN_LIGHTER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.__PIN_VACUUM_FAN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.__PIN_CONVEYOR_MOTOR, GPIO.OUT, initial=GPIO.LOW)

        if calibrate_mode:    
            GPIO.add_event_detect(self.__PIN_IR_SWITCH, GPIO.RISING, callback=self.on_gpio_falling_calibrate)
            GPIO.add_event_detect(self.__PIN_ENCODER_C, GPIO.RISING, callback=self.on_gpio_falling_calibrate)
        else:
            GPIO.add_event_detect(self.__PIN_IR_SWITCH, GPIO.RISING, callback=self.on_gpio_falling)
            GPIO.add_event_detect(self.__PIN_ENCODER_C, GPIO.RISING, callback=self.on_gpio_falling)


    def on_gpio_falling(self, channel):
        if channel == self.__PIN_IR_SWITCH:
            # self.__on_new_plate_enter()
            print('IR_Falling  %d'  %self.__debug_ir_count)
            self.__debug_ir_count += 1
            self.coming_row_id_to_first_robot_body = -int(280/32)
            self.coming_row_id_to_second_robot_body = -int(680/32)

        if channel == self.__PIN_ENCODER_C:
            # There are possible two plates in operation. We consider only one.
            self.coming_row_id_to_first_robot_body += 1
            self.coming_row_id_to_second_robot_body += 1
            self.__on_new_row_enter()

    def on_gpio_falling_calibrate(self, channel):
        if channel == self.__PIN_IR_SWITCH:
            print( 'For this circle ==== ', self.__debug_ir_count,self.coming_row_id_to_first_robot_body)
            self.coming_row_id_to_first_robot_body = 0
            self.__debug_ir_count += 1

        if channel == self.__PIN_ENCODER_C:
            # There are possible two plates in operation. We consider only one.
            self.coming_row_id_to_first_robot_body += 1
            self.coming_row_id_to_second_robot_body += 1
            self.__on_new_row_enter()


    def update_current_plate(self):
        self.__current_plate_enter_point = self.__next_plate_enter_point

    def read_gpio_input(self):
        print('IR= %i, ENCODER_B= %i' %(GPIO.input(self.__PIN_IR_SWITCH),GPIO.input(self.__PIN_ENCODER_C)))


    def ouput_light(self, ON_OFF):
        GPIO.output(self.__PIN_LIGHTER, ON_OFF)
    def output_vacuum_fan(self, ON_OFF):
        GPIO.output(self.__PIN_VACUUM_FAN, ON_OFF)
    def output_conveyor_motor(self, ON_OFF):
        GPIO.output(self.__PIN_CONVEYOR_MOTOR, ON_OFF)        

def test_b():
    pass

if __name__ == "__main__":
    tester = RobotSensors(test_b)
    if False:
        tester.setup()
        while True:
            tester.output_conveyor_motor(1)
            tester.read_gpio_input()
            time.sleep(0.3)

    while False:
        # turn off all
        tester.setup()
        tester.ouput_light(0)
        tester.output_vacuum_fan(0)
        tester.output_conveyor_motor(0)
        time.sleep(5)

        # turn on 
        tester.ouput_light(1)
        tester.output_vacuum_fan(1)
        tester.output_conveyor_motor(1)
        time.sleep(5)

    if False:
        tester.setup()
        tester.ouput_light(0)
        tester.output_vacuum_fan(0)
        tester.output_conveyor_motor(1)
        
    if True:
        tester.setup(calibrate_mode=True)
        tester.output_conveyor_motor(1)
        time.sleep(0.005)
        while True:
            pass