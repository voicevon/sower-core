import time
from board import SCL, SDA
from board import SCL_1, SDA_1
from busio import I2C
from adafruit_pca9685 import PCA9685
# from adafruit_motor import servo
import Jetson.GPIO as GPIO
# import ipywidgets.widgets as widgets
# from IPython.display import display
# import traitlets
# from jetbot import Camera, bgr8_to_jpeg
print (SCL)
print (SDA)

print (SCL_1)
print (SDA_1)



i2c_bus = I2C(SCL_1, SDA_1)
# i2c_bus = I2C(27, 28)
print('1111111111111111111111111')
pca = PCA9685(i2c_bus)
print('22222222222222222222')
pca.frequency = 50

# camera_tilt = servo.Servo(pca.channels[6], min_pulse=500, max_pulse=2600, actuation_range=180)
# camera_pan = servo.Servo(pca.channels[7], min_pulse=500, max_pulse=2600, actuation_range=180)
# camera_z = servo.Servo(pca.channels[8], min_pulse=500, max_pulse=2600, actuation_range=180)
