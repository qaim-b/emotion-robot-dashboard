#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import rclpy
from rclpy.node import Node
import math
from std_msgs.msg import String
import pylab



class PlotPnnx(Node):
  def __init__(self):
    super().__init__('plot_pnnx_node')
    self.create_subscription(String, 'pnnx2', self.callback_pnnx, 10)
    self.THRESHOLD = 0.236
    self.datalen = 0
    self.datamax = 100
    self.pnn50que = [0] * self.datamax
    self.pnn50th = [0.236] * self.datamax
    self.fig = pylab.figure("pNN50 Data")
    self.xx = range(0,self.datamax)
    self.ax1 = self.fig.add_subplot(1, 1, 1)
    self.ax1.set_ylim(0.0, 1.0)
    self.ax1.grid()
    self.lines1, = self.ax1.plot(self.xx, self.pnn50que, color="blue", label="pNN50")
    self.lines2, = self.ax1.plot(self.xx, self.pnn50th, color="red", label="Threshold")
    self.ax1.legend(loc=0)
    self.ax1.set_title("pNN50")
    self.fig.tight_layout()

  def callback_pnnx(self, msg):
    pnn50 = float(msg.data)
    self.get_logger().info("pNN50: " + str(pnn50))
    ### Display ###
    if self.datalen < self.datamax:
      self.pnn50que[self.datalen] = pnn50
      self.datalen = self.datalen + 1
    else:
      for kk in range(self.datamax - 1):
        self.pnn50que[kk] = self.pnn50que[kk+1]
      self.pnn50que[self.datamax - 1] = pnn50
    self.lines1.set_data(self.xx, self.pnn50que)
    self.lines2.set_data(self.xx, self.pnn50th)
    pylab.pause(.01)

def main(args=None):
  try:
    rclpy.init(args=args)
    talker = PlotPnnx()
    rclpy.spin(talker)
  except KeyboardInterrupt:
    pass
  finally:
    talker.destroy_node()
    rclpy.shutdown()
  
if __name__ == '__main__':
  main()
