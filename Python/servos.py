
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
import adafruit_pca9685 # sudo pip3 install adafruit-circuitpython-pca9685 ???? Looks like this is a micro-python libery
# from adafruit_servokit import ServoKit  # sudo pip3 install adafruit-circuitpython-servokit
# import adafruit_motor.servo
# View GPIO pinout
#   sudo /opt/nvidia/jetson-io/jetson-io.py

# Try to create an I2C device
dir(board)

print(board.__name__)



i2c = busio.I2C(board.SCL_1, board.SDA_1)
print("I2C is ok!")
pca = adafruit_pca9685.PCA9685(i2c, address=0x40,reference_clock_speed=400000)
print('PCA is ok')
pca.frequency = 20
print('PCA frequency is OK')

# kit = ServoKit(channels=8)
# print('kit is ok')
# servo = adafruit_motor.servo.Servo(0)
# print('servo is ok')


led_channel = pca.channels[0]
led_channel.duty_cycle = 0xfff
while True:
    # Increase brightness:
    for i in range(0, 0xfff, 10):
        led_channel.duty_cycle = i
        
    # Decrease brightness:
    for i in range(0xfff, 0, -10):
        led_channel.duty_cycle = i


    # kit.servo[0].angle = 180
    # time.sleep(3)

    # kit.servo[0].angle = 0
    # time.sleep(3)



kit = ServoKit(channels=16)

# sudo pip3 install adafruit-servokit

# kit = ServoKit(channels=16)  
# from adafruit_motor import servo
# camera_tilt = servo.Servo(pca.channels[6], min_pulse=500, max_pulse=2600, actuation_range=180)




class Servos_action():
    def __init__(self):
        self.row_id = 0
        self.row_action = list(bytes)


class Servos():
    # https://pypi.org/project/Jetson.GPIO/
    # https://www.jetsonhacks.com/2019/07/22/jetson-nano-using-i2c/
    # https://elinux.org/Jetson/I2C
    def __init__(self, callback_on_finished_one_row):
        self.last_finished_row = 0
        self.__callback = callback_on_finished_one_row
        # self.__planned_actions = list(Servos_action)
        self.__planned_actions = []

    def append_planned_action(self, servos_action):
            self.__planned_actions.append(servos_action)

    def output_i2c(self):
        # https://learn.adafruit.com/circuitpython-libraries-on-linux-and-the-nvidia-jetson-nano?view=all#i2c-sensors-devices
        pass

    def on_finished_one_row(self, row_id):
        self.last_finished_row = row_id
        self.__planned_actions.remove[0]
        self.__callback()

    def publish_planning(self):
        app_config.mqtt.publish('sower/servo/plan', planning)



    def main_loop(self):
        pass

def callback(row_id):
    print(row_id)


if __name__ == "__main__":
    pass
    servos = Servos(callback)
    while True:
        servos.main_loop()