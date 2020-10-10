
from global_const import app_config

import sys
sys.path.append(app_config.path.text_color)
from color_print import const

import paho.mqtt.client as mqtt


class MqttAgent(mqtt.Client):
    def __init__(self):
        super(MqttAgent, self).__init__()
        self.__is_connected = False
        self.__mqtt = mqtt
        self.__mqtt = mqtt.Client("sower-2039-1004")  # create new instance

        self.__YELLOW = const.print_color.fore.yellow
        self.__GREEN = const.print_color.fore.green
        self.__RESET = const.print_color.control.reset
        self.mqtt_system_turn_on = False
        self.__invoke_eye = None

    def connect(self, invoke_eye, broker='', port=0, uid='', psw=''):
        self.__invoke_eye = invoke_eye

        if broker == '':
            broker = app_config.server.mqtt.broker_addr
        if uid == '':
            uid = app_config.server.mqtt.username
        if psw == '':
            psw = app_config.server.mqtt.password
        if port == 0:
            port = app_config.server.mqtt.port

        self.__mqtt.username_pw_set(username=uid, password=psw)
        self.__mqtt.connect(broker)
        print(self.__GREEN + '[Info]: MQTT has connected to: %s' % broker + self.__RESET)

        self.__mqtt.loop_start()
        self.__mqtt.subscribe("sower/outside/system/state")
        self.__mqtt.subscribe("sower/eye/outside/width")
        self.__mqtt.subscribe("sower/eye/outside/height")
        self.__mqtt.subscribe("sower/eye/inside/camera/config_file")
        self.__mqtt.subscribe("sower/eye/inside/camera/trigger_mode")
        self.__mqtt.subscribe("sower/eye/inside/camera/trigger_type")
        self.__mqtt.subscribe("sower/eye/inside/camera/aestate")
        self.__mqtt.subscribe("sower/eye/inside/camera/exposure_time")
        self.__mqtt.subscribe("sower/eye/inside/detect/threshold_r")
        self.__mqtt.subscribe("sower/eye/inside/detect/threshold_g")
        self.__mqtt.subscribe("sower/eye/inside/detect/threshold_b")
        self.__mqtt.subscribe("sower/eye/inside/detect/threshold_size")
        self.__mqtt.subscribe("sower/eye/inside/detect/display")
        self.__mqtt.subscribe("sower/eye/inside/detect/roi/x")
        self.__mqtt.subscribe("sower/eye/inside/detect/roi/y")
        self.__mqtt.subscribe("sower/eye/inside/detect/roi/width")
        self.__mqtt.subscribe("sower/eye/inside/detect/roi/height")
        self.__mqtt.publish(topic="fishtank/switch/r4/command", payload="OFF", retain=True)
        self.__mqtt.on_message = self.__mqtt_on_message
        # self.__mqtt.loop_stop()
        return self.__mqtt

    def __mqtt_on_message(self, client, userdata, message):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)

        payload = str(message.payload.decode("utf-8"))
        if message.topic == "sower/outside/system/state":
            if message.payload:
                self.mqtt_system_turn_on = True
            else:
                self.mqtt_system_turn_on = False
        else:
            #self.__eye.on_mqtt_message(message.topic, payload)
            self.__invoke_eye(message.topic, payload)

    def publish_init(self):
        #  traverse app_config, publish all elements to broker.
        pass


if __name__ == "__main__":
    test = MqttAgent()
    test.connect()
