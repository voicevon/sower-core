#!/usr/bin/python3
# -*- coding: utf-8 -*-
# File  : robot_eye.py
# Author: bjq-znkzjs
# Date  : 2020-09-15

import paho.mqtt.client as mqtt
import numpy as np
import mvsdk
import platform
import cv2
import threading
import json
import time



#class eye_config:
#    topic_outside ={'width':16, 'height':8}
#    topic_inside_camera = {'trigger_mode':2, 'trigger_type':2}
#   
#   
#   class outside:
#        width = 16
#        height = 8
#    class inside:
#        class camera:
#            id = 1
#        class detector:
#            class roi:
#                a = 1
#                b = 2
#                f = 3
#

class myCamera(object):
    """
    acquire the image in callback method
    """

    def __init__(self):
        super(myCamera, self).__init__()
        self.pFrameBuffer = 0
        self.hCamera = 0
        self.frame = None  # 待识别图像
        self.frame_id = 0
        self.isopen = False

    def open(self):
        # 枚举相机
        DevList = mvsdk.CameraEnumerateDevice()
        nDev = len(DevList)
        if nDev < 1:
            print("No camera was found!")
            self.isopen = False
            return

        DevInfo = DevList[0]  # 默认打开0

        # 打开相机
        try:
            self.hCamera = mvsdk.CameraInit(DevInfo, -1, -1)
            self.isopen = True
        except mvsdk.CameraException as e:
            print("CameraInit Failed({}): {}".format(e.error_code, e.message))
            self.isopen = False
            return

    def setCameraResolution(self,h_camera, offsetx, offsety, width, height):
        img_res = mvsdk.tSdkImageResolution()
        img_res.iIndex = 0xFF
        img_res.iWidth = width
        img_res.iWidthFOV = width
        img_res.iHeight = height
        img_res.iHeightFOV = height
        img_res.iHOffsetFOV = offsetx
        img_res.iVOffsetFOV = offsety
        img_res.iWidthZoomSw = 0
        img_res.iHeightZoomSw = 0
        img_res.uBinAverageMode = 0
        img_res.uBinSumMode = 0
        img_res.uResampleMask = 0
        img_res.uSkipMode = 0
        mvsdk.CameraSetImageResolution(h_camera, img_res)


    def config(self, config_file=None, TriggerMode=2, TriggerType=1, AeState=False, ExposureTime=30):
        # 获取相机特性描述
        print('camera config:', TriggerMode,TriggerType, AeState, ExposureTime)
        cap = mvsdk.CameraGetCapability(self.hCamera)
        #print(cap)
        # 判断是黑白相机还是彩色相机
        monoCamera = (cap.sIspCapacity.bMonoSensor != 0)
        # 黑白相机让ISP直接输出MONO数据，而不是扩展成R=G=B的24位灰度
        if monoCamera:
            mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
        else:
            mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_BGR8)

        # 相机模式默认硬件触发采集
        mvsdk.CameraSetTriggerMode(self.hCamera, TriggerMode)  # TriggerMode = 0 连续采集 1 软件触发 2 硬件触发
        mvsdk.CameraSetExtTrigSignalType(self.hCamera, TriggerType)  # TriggerType = 0 上升沿 1 下降沿 2 高电平 3 低电平 4 上升+下降沿

        # 默认手动曝光，曝光时间默认30ms
        mvsdk.CameraSetAeState(self.hCamera, AeState)  # AeState = True 自动曝光 False 手动曝光
        mvsdk.CameraSetExposureTime(self.hCamera, ExposureTime * 1000)
        
        # 加载相机参数
        if config_file is not None:
            mvsdk.CameraLoadParameter(self.hCamera, config_file)

        #self.setCameraResolution(self.hCamera, 0, 0, 1280, 1024)
        # 让SDK内部取图线程开始工作
        mvsdk.CameraPlay(self.hCamera)

        # 计算RGB buffer所需的大小，这里直接按照相机的最大分辨率来分配
        #FrameBufferSize = 1280 * 1024 * (1 if monoCamera else 3)
        FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * (1 if monoCamera else 3)
        # 分配RGB buffer，用来存放ISP输出的图像
        # 备注：从相机传输到PC端的是RAW数据，在PC端通过软件ISP转为RGB数据（如果是黑白相机就不需要转换格式，但是ISP还有其它处理，所以也需要分配这个buffer）
        self.pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)

        # 设置采集回调函数
        mvsdk.CameraSetCallbackFunction(self.hCamera, self.GrabCallback, 0)

    @mvsdk.method(mvsdk.CAMERA_SNAP_PROC)
    def GrabCallback(self, hCamera, pRawData, pFrameHead, pContext):
        FrameHead = pFrameHead[0]
        pFrameBuffer = self.pFrameBuffer

        mvsdk.CameraImageProcess(hCamera, pRawData, pFrameBuffer, FrameHead)
        mvsdk.CameraReleaseImageBuffer(hCamera, pRawData)

        # windows下取到的图像数据是上下颠倒的，以BMP格式存放。转换成opencv则需要上下翻转成正的
        # linux下直接输出正的，不需要上下翻转
        if platform.system() == "Windows":
            mvsdk.CameraFlipFrameBuffer(pFrameBuffer, FrameHead, 1)

        # 此时图片已经存储在pFrameBuffer中，对于彩色相机pFrameBuffer=RGB数据，黑白相机pFrameBuffer=8位灰度数据
        # 把pFrameBuffer转换成opencv的图像格式以进行后续算法处理
        frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(pFrameBuffer)
        frame = np.frombuffer(frame_data, dtype=np.uint8)
        self.frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth,
                                    1 if FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3))
        self.frame_id += 1
        #cv2.imshow('bai cap', self.frame)
        #cv2.imwrite('bai_raw.jpg', self.frame)
        print('got image')

    def release(self):
        # 关闭相机
        mvsdk.CameraUnInit(self.hCamera)
        # 释放帧缓存
        mvsdk.CameraAlignFree(self.pFrameBuffer)


class corn_detection(object):
    """
    detect the tray
    recognize the corn
    """

    # 识别空穴
    def __init__(self, tray_height=8, tray_width=16):
        super(corn_detection, self).__init__()
        self.ROI = None  # 穴盘轮廓
        self.tray_height = tray_height  # 穴盘规格
        self.tray_width = tray_width
        self.corn_img = None  # 有效玉米区域
        self.capture_img = None

    def extractROI(self, raw_img):
        # 检测穴盘外围轮廓
        print("detect tray contour....")
        try:
            raw_img.shape
        except:
            self.ROI = None
            return self.ROI
        #cv2.imshow('bai extract roi', raw_img)
        #cv2.waitKey(0)

        H_img = cv2.cvtColor(raw_img, cv2.COLOR_RGB2GRAY)
        res, img_detected = cv2.threshold(H_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        img_detected = cv2.morphologyEx(img_detected, cv2.MORPH_CLOSE, kernel=(5, 5))
        #chy = cv2.findContours(img_detected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 检测轮廓
        #print(chy[0],chy[1])
        img, contours, hierarchy = cv2.findContours(img_detected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 检测轮廓
        areas = []
        contour = []
        for cont in contours:
            area = cv2.contourArea(cont)  # 计算包围性状的面积
            if area < 10000:  # 过滤面积较小的形状
                continue
            else:
                areas.append(area)
                contour.append(cont)
        cont_max = contour[np.argmax(areas)]
        self.ROI = cv2.boundingRect(cont_max)  # 提取矩形坐标
        return self.ROI

    def corn_recognition(self, raw_img, ROI=None, display=False, theshold_R=200, theshold_G=200, theshold_B=150,
                         theshold_size=8):
        # 检测玉米     
        try:
            raw_img.shape
        except:
            return np.ones((self.tray_height, self.tray_width)).astype(bool)

        if ROI is not None:
            self.ROI = ROI

        corn_result = np.zeros((self.tray_height, self.tray_width)).astype(bool)
        if self.ROI is not None:
            self.corn_img = raw_img[self.ROI[1]:(self.ROI[1] + self.ROI[3]), self.ROI[0]:(self.ROI[0] + self.ROI[2])]
            cv2.imwrite('bai.jpg', self.corn_img)
            self.corn_img = cv2.resize(self.corn_img, (int(self.ROI[2]/2), int(self.ROI[3]/2)))
            # img_test  = self.corn_img.copy()
            # img_test[(img_test[:,:,0]>150]=0
            # cv2.imwrite('bai_test.jpg', img_test)
            img_mask = self.corn_img.copy()
            print(theshold_R, theshold_G,theshold_B,theshold_size)
            img_mask[(img_mask[:, :, 0] > theshold_B) | (img_mask[:, :, 1] < theshold_G) |
                                     (img_mask[:, :, 2] < theshold_R)] = 0  # make mask | (self.corn_img[:, :, 2] < 100)

            print("img shape: ", img_mask.shape)
            img_gray = cv2.cvtColor(img_mask, cv2.COLOR_RGB2GRAY)
            cv2.imwrite('bai_mask.jpg', img_gray)
            res, img_binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # 分割
            element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))  # 形态学去噪
            img_binary = cv2.morphologyEx(img_binary, cv2.MORPH_CLOSE, element)  # 闭运算连接空洞
            # img_binary = cv2.morphologyEx(img_binary, cv2.MORPH_OPEN, element)  # 开运算去噪
            # cv2.imwrite('gray.jpg', img_binary)
            img, contours, hierarchy = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 检测轮廓

            areas = []
            for cont in contours:
                area = cv2.contourArea(cont)  # 计算包围性状的面积
                areas.append(area)

            if len(areas)!=0:
                max_area = np.max(areas)
            else:
                max_area=0
            cont_res =[]
            for cont in contours:
                if cv2.contourArea(cont)> max_area/theshold_size:
                    cont_res.append(cont)
                    x,y,w,h = cv2.boundingRect(cont)  # 提取矩形坐标
                    if display:
                        cv2.rectangle(self.corn_img, (x,y),(x+w,y+h), (0, 0, 255), 5)  # 绘制矩形
            # contours = np.array(contours)
            # print(contours)
            # cont_res = contours[np.argwhere(areas > max_area / theshold_size).squeeze()]  # 计算有效玉米轮廓
            # print(cont_res)   
            #if display:
            #    cv2.drawContours(self.corn_img, cont_res, -1, (255, 0, 0), 2)  # 绘制轮廓
                #cv2.drawContours(self.corn_img, cont_res.tolist(), -1, (255, 0, 0), 2)  # 绘制轮廓

            interval_h = int(self.ROI[3] /2 / self.tray_height)  # 穴大小
            interval_w = int(self.ROI[2] / 2/ self.tray_width)
            print("int_h:", interval_h, "int_w:", interval_w)

            for row in range(self.tray_height):
                for col in range(self.tray_width):
                    #tray_rect = [self.ROI[0] + interval_w * col, self.ROI[1] + interval_h * row]
                    tray_rect = [interval_w * col, interval_h * row]
                    # 遍历找到的所有玉米粒
                    for cont in cont_res:
                        x,y,w,h = cv2.boundingRect(cont)  # 提取矩形坐标
                        if x + w > tray_rect[0] and tray_rect[0] + interval_w >x and \
                                y+ h > tray_rect[1] and tray_rect[1] + interval_h > y:
                            corn_result[row, col] = True
                            break
            return corn_result


class RobotEye(object):
    def __init__(self):
        super(RobotEye, self).__init__()
        self.__mqtt = mqtt
        self.__on_got_new_plate_callback = None
        self.__running_on_my_own_thread = False
        self.__camera = myCamera()
        self.__corn_detect = corn_detection()
        #self.__camera_config = {'config_file': '/home/znkzjs/sower-core/camera.config'}
        self.__camera_config = dict() 
        self.__detect_config = {'ROI': [80,405,1872,975]}
        self.__tray_config = dict()

    def start_with_new_thread(self, mqtt):
        self.__mqtt = mqtt
        self.__running_on_my_own_thread = True
        t = threading(self.__main_task)
        t.start

    def setup(self, mqtt, callback):
        self.__mqtt = mqtt
        self.__on_got_new_plate_callback = callback
        #self.__mqtt.subscribe("sower/eye/outside/width")
        #self.__mqtt.subscribe("sower/eye/outside/height")
        #self.__mqtt.subscribe("sower/eye/inside/camera/config_file")
        #self.__mqtt.subscribe("sower/eye/inside/camera/trigger_mode")
        #self.__mqtt.subscribe("sower/eye/inside/camera/trigger_type")
        #self.__mqtt.subscribe("sower/eye/inside/camera/aestate")
        #self.__mqtt.subscribe("sower/eye/inside/camera/exposure_time")
        #self.__mqtt.subscribe("sower/eye/inside/detect/threshold_r")
        #self.__mqtt.subscribe("sower/eye/inside/detect/threshold_g")
        #self.__mqtt.subscribe("sower/eye/inside/detect/threshold_b")
        #self.__mqtt.subscribe("sower/eye/inside/detect/threshold_size")
        #self.__mqtt.subscribe("sower/eye/inside/detect/display")
        #self.__mqtt.subscribe("sower/eye/inside/detect/roi/x")
        #self.__mqtt.subscribe("sower/eye/inside/detect/roi/y")
        #self.__mqtt.subscribe("sower/eye/inside/detect/roi/width")
        #self.__mqtt.subscribe("sower/eye/inside/detect/roi/height")

        self.__camera.open()  # open camera
        if self.__camera.isopen:
            print('camera open')
        else:
            print('camera open failed')
        if self.__camera_config.get('config_file', "") != "":
            self.__camera.config(self.__camera_config['config_file'])
            print("camera config from file!")
        else:
            trigger_mode = self.__camera_config.get('trigger_mode', 2)
            trigger_type = self.__camera_config.get('trigger_type', 1)
            aestate = self.__camera_config.get('aestate', False)
            exposure_time = self.__camera_config.get('exposure_time', 10)
            self.__camera.config(TriggerMode=trigger_mode, TriggerType=trigger_type, AeState=aestate, ExposureTime=exposure_time)
        print('camera config done')

    def main_loop(self):
        # This is mainly for debugging. do not use while loop in this function!
        # For better performance, invoke start_with_new_thread() instead.

        # stop my_own_thread
        self.__running_on_my_own_thread = False
        self.__main_task()

    def __main_task(self):
        # Try to get a plate map, When it happened, invoke the callback
        #self.__camera.open()  # open camera
        message_id = 0
        last_frame_id = 0
        if self.__camera.isopen:
            # while self.__mqtt.mqtt_system_turn_on:
            while True:   #TODO
                if self.__camera.frame_id != last_frame_id:
                    print('capture image done')
                    last_frame_id = self.__camera.frame_id
                    if self.__detect_config.get('ROI', []):
                        if len(self.__detect_config['ROI']) == 4 and self.__detect_config['ROI'][0] != 0 \
                                and self.__detect_config['ROI'][1] !=0 and self.__detect_config['ROI'][2] !=0 and self.__detect_config['ROI'][3] != 0:
                            roi = self.__detect_config['ROI']
                        else:
                            print('invalid ROI')
                            continue
                    else:
                        cap_img = self.__camera.frame.copy()
                        roi = self.__corn_detect.extractROI(self.__camera.frame)
                        if roi is None:
                            print("extract tray contour failed!")
                            continue
                    print('roi:', roi)
                    thres_R = self.__detect_config.get('threshold_R', 190)
                    thres_G = self.__detect_config.get('threshold_G', 190)
                    thres_B = self.__detect_config.get('threshold_B', 150)
                    thres_size = self.__detect_config.get('threshold_size', 8)
                    display = self.__detect_config.get('display', False)
                    print('start detect.................')
                    start_time = time.perf_counter()
                    result = self.__corn_detect.corn_recognition(self.__camera.frame, roi, display, thres_R, thres_G,
                                                                 thres_B, thres_size)
                    end_time = time.perf_counter()
                    print("corn result: ", result)
                    print("detection time:", end_time-start_time)
                    self.__mqtt.publish("sower/eye/detect", result.tostring(),retain=True)
                    self.__on_got_new_plate_callback(result, self.__corn_detect.corn_img)
                    if display:
                        img_show = cv2.resize(self.__corn_detect.corn_img, (400, 200))
                        is_success, img_encode = cv2.imencode(".jpg", img_show)
                        if is_success:
                            img_pub = img_encode.tobytes()
                            self.__mqtt.publish("sower/img/bin", img_pub, retain=True)
                            print("show image")
                    #self.__on_got_new_plate_callback(result, cap_img)


    def on_mqtt_message(self, topic, payload):
        # will be invoked from manager, not mqtt_client directly
        # only the topic like "sower/eye/*" would trigger the invoking.


        #topic_outside ={'width':16, 'height':8}
        #topic_inside_camera = {'trigger_mode':2, 'trigger_type':2}
        #for k,v in topic_outside:
        #    if topic == 'sower/eye/outside/' + k
        #    self.__tray_config[topic] = int (payload)
        
        print("robot_eye:",topic, payload)
        #self.__detect_config['ROI'] = [0,0,0,0]
        if topic == "sower/eye/outside/width":
            self.__tray_config['width'] = int(payload)
        elif topic == "sower/eye/outside/height":
            self.__tray_config['height'] = int(payload)
        elif topic == "sower/eye/inside/camera/trigger_mode":
            self.__camera_config['trigger_mode'] = int(payload)
        elif topic == "sower/eye/inside/camera/trigger_type":
            self.__camera_config['trigger_type'] = int(payload)
        elif topic == "sower/eye/inside/camera/ae_state":
            self.__camera_config['aestate'] = int(payload)
        elif topic == "sower/eye/inside/camera/exposure_time":
            self.__camera_config['exposure_time'] = int(payload)
        elif topic == "sower/eye/inside/detect/threshold_r":
            self.__detect_config['threshold_R'] = int(payload)
        elif topic == "sower/eye/inside/detect/threshold_g":
            self.__detect_config['threshold_G'] = int(payload)
        elif topic == "sower/eye/inside/detect/threshold_b":
            self.__detect_config['threshold_B'] = int(payload)
        elif topic == "sower/eye/inside/detect/threshold_size":
            self.__detect_config['threshold_size'] = int(payload)
        elif topic == "sower/eye/inside/detect/display":
            if payload == "ON":
                self.__detect_config['display'] = True
            else:
                self.__detect_config['display'] = False
        elif topic == "sower/eye/inside/detect/roi/x":
            self.__detect_config['ROI'][0] = int(payload)
            print("ROI.x:",int(payload))
        elif topic == "sower/eye/inside/detect/roi/y":
            self.__detect_config['ROI'][1] = int(payload)
            print("ROI.y:",int(payload))
        elif topic == "sower/eye/inside/detect/roi/width":
            self.__detect_config['ROI'][2] = int(payload)
            print("ROI.w:",int(payload))
        elif topic == "sower/eye/inside/detect/roi/height":
            self.__detect_config['ROI'][3] = int(payload)
            print("ROI.h:",int(payload))


        if self.__tray_config.get('width') is not None and self.__tray_config.get('height') is not None:
            self.__corn_detect.__init__(self.__tray_config['height'], self.__tray_config['width'])
            print('tray config done')

        #if topic == "sower/eye/outside/width":
        #    # payload is like "{"width":16, "height":8}"
        #    self.__tray_config = json.loads(payload)
        #    if self.__tray_config.get('width') is not None and self.__tray_config.get('height') is not None:
        #        self.__corn_detect.__init__(self.__tray_config['height'], self.__tray_config['width'])
        #elif topic == "sower/eye/inside":
        #    # payload is like "{        "id": 1
        #    #                           "camera":
        #    #                            {
        #    #                                "trigger mode": 2,
        #    #                                "trigger type": 0,
        #    #                                "aestate": false,
        #    #                                "exposure time": 30,
        #    #                                "config file": "/home/camera.Config"
        #    #                            },
        #    #                    "detect":
        #    #                            {
        #    #                               "threshold_R": 200,
        #    #                               "threshold_G": 200,
        #    #                               "threshold_B": 150,
        #    #                               "threshold_size": 8,
        #    #                               "display": true,
        #    #                               "ROI": [20,30,500,500]
        #    #                            }
        #    #                  }"
        #    config = json.loads(payload)
        #    self.__message_id = config['id']
        #    if config.get('camera') is not None:
        #        self.__camera_config = config['camera']
        #    if config.get('detect') is not None:
        #        self.__detect_config = config['detect']


if __name__ == "__main__":
    runner = RobotEye()








# sudo ./scripts/setPermissions.sh $USER

#!/bin/bash
# $1 should be the name of the user to add
# usermod -aG i2c $1
# groupadd -f -r gpio
# sudo usermod -a -G gpio $1
# cp /opt/nvidia/jetson-gpio/etc/99-gpio.rules /etc/udev/rules.d/
# udevadm control --reload-rules && sudo udevadm trigger