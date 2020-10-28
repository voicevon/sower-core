
#  Jetson Expansion Header Tool
#       sudo /opt/nvidia/jetson-io/jetson-io.py
#           from: https://www.jetsonhacks.com/2020/05/04/spi-on-jetson-using-jetson-io/



from enum import Enum
import Jetson.GPIO as GPIO

class RobotSensors():

    def __init__(self, on_new_plate_enter, on_new_row_enter):
        self.__PIN_IR_SWITCH = 37
        self.__PIN_ENCODER_A = 31
        self.__PIN_ENCODER_B = 32

        self.__on_new_plate_enter = on_new_plate_enter
        self.__on_new_row_enter = on_new_row_enter

        self.__encoder_distance_per_row = 200
        self.__encoder_distance = -12345
        self.coming_row_id  = -1
        self.current_speed = 30
        '''
        unit is mm/second
        '''


    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.__PIN_IR_SWITCH, GPIO.IN)
        GPIO.setup(self.__PIN_ENCODER_A, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.__PIN_ENCODER_B, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        GPIO.add_event_detect(self.__PIN_IR_SWITCH, GPIO.RISING, callback=self.on_gpio_rising)
        GPIO.add_event_detect(self.__PIN_ENCODER_A, GPIO.RISING, callback=self.on_gpio_rising)
        # GPIO.add_event_detect(self.__PIN_IR_SWITCH, GPIO.FALLING, callback=self.on_gpio_falling)


    def on_gpio_rising(self, channel):
        if channel == self.__PIN_IR_SWITCH:
            self.__encoder_distance = -12345

        elif channel == self.__PIN_ENCODER_A:
            self.__encoder_distance += 1
            
            if self.__encoder_distance / self.__encoder_distance_per_row == 0:
                # current row must be fininshed. new row is coming
                self.__on_new_row_enter()

    # def on_gpio_falling(self, channel):
    #     if channel == self.__PIN_IR_SWITCH:
    #         self.coming_row_id = -1
