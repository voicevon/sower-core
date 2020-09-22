import cv2
import threading
import paho.mqtt.client as mqtt


class RobotEye():

    def __init__(self):
        self.__mqtt = mqtt
        self.__on_saw_caves = None
        self.__on_my_own_thread = False

    def start_with_new_thread(self, mqtt):
        self.__mqtt = mqtt
        self.__on_my_own_thread = True
        t = threading(self.__main_task)
        t.start

    def setup(self, mqtt):
        self.__mqtt = mqtt

    def main_loop(self):
        # This is mainly for debugging. do not use while loop in this function!
        # For better performance, invoke start_with_new_thread() instead.
        self.__main_task()

    def __main_task(self):
        # Try to get a plate map, When it happened, invoke the callback
        pass

    # def set_service_saw_caves(self, matt, on_message_callback):
    #     self.__on_saw_caves = on_message_callback
    def on_mqtt_message(self, topic, payload):
        pass


if __name__ == "__main__":
    runner = RobotEye()
