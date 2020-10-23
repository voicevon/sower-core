
import Jetson.GPIO as GPIO
class Servos_action():
    def __init__(self):
        self.row_id = 0
        self.row_action = list(bytes)


class Servos():
    # https://maker.pro/nvidia-jetson/tutorial/how-to-use-gpio-pins-on-jetson-nano-developer-kit
    # https://pypi.org/project/Jetson.GPIO/
    # https://www.jetsonhacks.com/2019/07/22/jetson-nano-using-i2c/
    def __init__(self, callback_on_finished_one_row):
        self.last_finished_row = 0
        self.__callback = callback_on_finished_one_row
        # self.__planned_actions = list(Servos_action)
        self.__planned_actions = []
        self.

    def append_planned_action(self, servos_action):
            self.__planned_actions.append(servos_action)


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
    servos = Servos(callback)
    while True:
        servos.main_loop()