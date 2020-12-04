
#  Jetson Expansion Header Tool
#       sudo /opt/nvidia/jetson-io/jetson-io.py
#           from: https://www.jetsonhacks.com/2020/05/04/spi-on-jetson-using-jetson-io/



from enum import Enum
import Jetson.GPIO as GPIO
import time
import os
class RobotSensors():

    def __init__(self, on_new_plate_enter, on_new_row_enter):
        self.__PIN_IR_SWITCH = 33
        self.__PIN_ENCODER_A = 37
        self.__PIN_ENCODER_B = 35
        # self.__PIN_POWER_OFF = 29
        # self.__PIN_INPUT_TEST = 35

        self.__PIN_CONVEYOR_MOTOR = 13
        self.__PIN_VACUUM_FAN = 15
        self.__PIN_LIGHTER = 7

        self.__on_new_plate_enter = on_new_plate_enter
        self.__on_new_row_enter = on_new_row_enter

        self.__encoder_distance_per_row = 200
        self.__encoder_distance = -12345
        self.__current_plate_enter_point = 0
        self.__next_plate_enter_point = 0
        self.coming_row_id  = -1
        self.current_speed = 30
        self.ir_count = 0
        '''
        unit is mm/second
        '''


    def setup(self):
        # GPIO.cleanup()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.__PIN_IR_SWITCH, GPIO.IN)
        GPIO.setup(self.__PIN_ENCODER_A, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.__PIN_ENCODER_B, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.__PIN_LIGHTER, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.__PIN_VACUUM_FAN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.__PIN_CONVEYOR_MOTOR, GPIO.OUT, initial=GPIO.LOW)

        GPIO.add_event_detect(self.__PIN_IR_SWITCH, GPIO.FALLING, callback=self.on_gpio_falling)
        GPIO.add_event_detect(self.__PIN_ENCODER_A, GPIO.RISING, callback=self.on_gpio_rising)
        # GPIO.add_event_detect(self.__PIN_IR_SWITCH, GPIO.FALLING, callback=self.on_gpio_falling)

    def ouput_light(self, ON_OFF):
        GPIO.output(self.__PIN_LIGHTER, ON_OFF)
    def output_vacuum_fan(self, ON_OFF):
        GPIO.output(self.__PIN_VACUUM_FAN, ON_OFF)
    def output_conveyor_motor(self, ON_OFF):
        GPIO.output(self.__PIN_CONVEYOR_MOTOR, ON_OFF)

    def on_gpio_falling(self, channel):
        if channel == self.__PIN_IR_SWITCH:
            # There are two plates in operation.
            self.__next_plate_enter_point = self.__encoder_distance
            print('IR_Falling  %d'  %self.ir_count)
            self.ir_count += 1

    def on_gpio_rising(self, channel):
        if channel == self.__PIN_ENCODER_A:
            self.__encoder_distance += 1
            print('encoder_distance=%d' %self.__encoder_distance)
            if self.__encoder_distance / self.__encoder_distance_per_row == 0:
                # current row must be fininshed. new row is coming
                self.__on_new_row_enter()
        
        # elif channel == self.__PIN_POWER_OFF:
        #     # poew off the linux system.
        #     os.system('systemctl poweroff') 

    def update_current_plate(self):
        self.__current_plate_enter_point = self.__next_plate_enter_point

    def read_gpio_input(self):
        # print(GPIO.input(self.__PIN_INPUT_TEST))
        print(GPIO.input(self.__PIN_IR_SWITCH))
        # print(GPIO.input(self.__PIN_POWER_OFF))
        print(GPIO.input(self.__PIN_ENCODER_A))
        print(GPIO.input(self.__PIN_ENCODER_B))
        print('---------------------------------------')

        
    # def on_gpio_falling(self, channel):
    #     if channel == self.__PIN_IR_SWITCH:
    #         self.coming_row_id = -1

def test_a():
    pass
def test_b():
    pass

if __name__ == "__main__":
    tester = RobotSensors(test_a,test_b)
    tester.setup()
    while False:
        tester.read_gpio_input()
        time.sleep(0.3)

    while False:
        # turn off all
        tester.ouput_light(0)
        tester.output_vacuum_fan(0)
        tester.output_conveyor_motor(0)
        time.sleep(5)

        # turn on 
        tester.ouput_light(1)
        tester.output_vacuum_fan(1)
        tester.output_conveyor_motor(1)
        time.sleep(5)

    while True:
        pass