
#  Jetson Expansion Header Tool
#       sudo /opt/nvidia/jetson-io/jetson-io.py
#           from: https://www.jetsonhacks.com/2020/05/04/spi-on-jetson-using-jetson-io/





# List I2C devices
#   ls /dev/i2c*
# List I2C address on device 0
#   i2cdetect -r -y 0




#  https://learn.adafruit.com/16-channel-pwm-servo-driver/python-circuitpython
import time
import board  # pip3 install adafruit-blinka
import busio
from adafruit_servokit import ServoKit

# import adafruit_pca9685 # sudo pip3 install adafruit-circuitpython-pca9685 ???? Looks like this is a micro-python libery
# from adafruit_servokit import ServoKit  # sudo pip3 install adafruit-circuitpython-servokit
# import adafruit_motor.servo
# View GPIO pinout
#   sudo /opt/nvidia/jetson-io/jetson-io.py

# Try to create an I2C device
  

class Servos_action():
    '''
    From right to left, named byte_0, byte_1, byte_2
    '''
    def __init__(self):
        self.row_id = 0
        self.byte_0 = 0
        self.byte_1 = 0
        self.byte_2 = 0


class Servos():
    # https://pypi.org/project/Jetson.GPIO/
    # https://www.jetsonhacks.com/2019/07/22/jetson-nano-using-i2c/
    # https://elinux.org/Jetson/I2C
    def __init__(self):
        self.last_finished_row = 0
        self.__planned_actions = []

    def setup(self):
        print("Initializing Servos")
        i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1))
        print("Initializing ServoKit")
        kit = ServoKit(channels=16, i2c=i2c_bus0)
        # kit[0] is the bottom servo
        # kit[1] is the top servo
        print("Done initializing")
        while True:
            # sweep = range(0,180)
            #for degree in sweep:
            kit.servo[0].angle=180

    def append_planned_action(self, servos_action):
        # ??? 
        self.__planned_actions.append(servos_action)

    def output_i2c(self, row_id):
        # https://learn.adafruit.com/circuitpython-libraries-on-linux-and-the-nvidia-jetson-nano?view=all#i2c-sensors-devices
        pass


if __name__ == "__main__":
    pass
    servos = Servos()
    while True:
        servos.main_loop()