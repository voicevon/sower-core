import cv2
import threading


class RobotEye():

    def __init__(self):
        self.__on_saw_caves = None
        self.__on_my_own_thread = False

    def start_with_new_thread(self):
        self.__on_my_own_thread = True
        t = threading(self.__main_task)
        t.start

    def start_with_main_thread(self):
        # This is mainly for debugging. 
        # For better performance, invoke start_with_new_thread() instead.
        self.__main_task()

    def __main_task(self):
        pass

    def set_service_saw_caves(self, callback):
        self.__on_saw_caves = callback


if __name__ == "__main__":
    runner = RobotEye()
