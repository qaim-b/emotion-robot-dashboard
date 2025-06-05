import rclpy
from rclpy.node import Node
#from std_msgs.msg import Float32
from std_msgs.msg import String
#import serial
import numpy as np
import random
import time

MAX_LEN_DATA = 30
X_PNN = 50

class PnnxNode(Node):
    def __init__(self):
        super().__init__('pnnx2_dummy_node')
        
        #self.sensor = serial.Serial('/dev/ttyACM0', 115200)
        self.pub_pnnx = self.create_publisher(String, 'pnnx2', 10)
        self.pnnx = String() # pnnx
        self.pnnx.data = "0.0" # 送信データ
    
    def publish_pnnx(self):
        self.pnnx.data = str(float(random.uniform(0.0, 1.0)))
        self.pub_pnnx.publish(self.pnnx)
        self.get_logger().info(f'Pnnx: {self.pnnx.data}')
            
    def run(self):
        while rclpy.ok():
            self.publish_pnnx()
            time.sleep(1)

def main(args=None):
    rclpy.init(args=args)
    talker = PnnxNode()
    try:
        talker.run()
    except KeyboardInterrupt:
        pass
    finally:
        talker.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
