#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import rclpy
from rclpy.node import Node
import sys
import time
import os
import psutil
import filecmp
import threading
import cv2
from std_msgs.msg import String

class FaceCtrlCv(Node):
  def __init__(self):
    super().__init__('face_ctrl2_cv_node')
    
    self.target_image = ""
    self.stop_flg = 0
    self.home_dir = os.environ["HOME"]
    
    t = threading.Thread(args=(), target=self.disp_thread)
    t.start()
    self.create_subscription(String, 'face', self.callback, 10)
    
  def cmp_file(self, fn1, fn2):
    f1 = open(fn1, 'rb')
    f2 = open(fn2, 'rb')

    string1 = f1.read()
    string2 = f2.read()

    if string1 == string2: return True
    return False

  ### 採用版 ###
  def disp_cv(self, img_file):
    fff = self.home_dir + "/ros2_ws/src/emotion_speech/face_DB/" + img_file + ".JPG"
    img = cv2.imread(fff)
    img_resize = img#cv2.resize(img, (320,180))
    cv2.imshow("Face", img_resize)
    cv2.waitKey(1)
    #self.get_logger().info("\n###\n### Disp " + str(fff) + "\n###")

  def disp_thread(self):
    self.get_logger().info("######### disp_thread #########")
    while 1:
        if self.stop_flg:
            break
        if self.target_image == "":
            continue
        #self.disp(self.target_image)
        self.disp_cv(self.target_image)
        time.sleep(0.1)
        
  def callback(self, msg):
    self.get_logger().info("Message " + str(msg.data) + " recieved")
    self.target_image = msg.data

def main(args=None):
  try:
    rclpy.init(args=args)
    talker = FaceCtrlCv()
    rclpy.spin(talker)
    talker.stop_flg = 1
  except KeyboardInterrupt:
    pass
  finally:
    talker.destroy_node()
    rclpy.shutdown()
  
if __name__ == '__main__':
  main()

