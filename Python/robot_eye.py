import cv2
import threading
import paho.mqtt.client as mqtt


class RobotEye():

    def __init__(self):
        self.__mqtt = mqtt
        self.__on_got_new_plate_callback = None
        self.__running_on_my_own_thread = False

    def start_with_new_thread(self, mqtt):
        self.__mqtt = mqtt
        self.__running_on_my_own_thread = True
        t = threading(self.__main_task)
        t.start

    def setup(self, mqtt, callback):
        self.__mqtt = mqtt
        self.__on_got_new_plate_callback = callback

    def main_loop(self):
        # This is mainly for debugging. do not use while loop in this function!
        # For better performance, invoke start_with_new_thread() instead.

        #stop my_own_thread
        self.__running_on_my_own_thread = False
        self.__main_task()

    def __main_task(self):
        # Try to get a plate map, When it happened, invoke the callback
        pass

    def on_mqtt_message(self, topic, payload):
        # will be invoked from manager, not mqtt_client directly
        # only the topic like "sower/eye/*" would trigger the invoking.
        pass


if __name__ == "__main__":
    runner = RobotEye()
