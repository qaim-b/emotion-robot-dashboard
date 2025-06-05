import rclpy
from rclpy.node import Node
#from std_msgs.msg import Float32
from std_msgs.msg import String
import serial
import numpy as np

MAX_LEN_DATA = 30
X_PNN = 50

class PnnxNode(Node):
    def __init__(self):
        super().__init__('pnnx2_node')
        
        self.sensor = serial.Serial('/dev/ttyACM0', 115200)
        self.pub_pnnx = self.create_publisher(String, 'pnnx2', 10)
        self.pnnx = String() # pnnx
        self.pnnx.data = "0.0" # 送信データ
        # pnnxの計算に使用
        self.rri = 0
        self.rri_arr = []
        self.xx_count = 0
    
    def publish_pnnx(self):
        sensor_data = self.sensor.readline().decode(encoding='utf-8').strip()
        if sensor_data.startswith('Q'): # S123, Q689, B69 の形でシリアル通信が来る（Sがraw、QがRRI(IBI)、BがBPM）
            self.get_logger().info(f'Sensor_data:{sensor_data}')
            self.rri = float(sensor_data[1:])
            self.xx_count += 1
            
            # データ数が足りてる時はpnnx計算
            if self.xx_count >= MAX_LEN_DATA + 2:
                self.rri_arr.pop(0)
                self.rri_arr.append(self.rri)
                count = 0
                for i in range(MAX_LEN_DATA):
                    if abs(self.rri_arr[i] - self.rri_arr[i+1]) > X_PNN:
                        count += 1

                # pnnxを計算して更新、publish
                self.pnnx.data = str(float(count / 30))
                self.pub_pnnx.publish(self.pnnx)
                self.get_logger().info(f'Pnnx: {self.pnnx.data}')

            # pnnxに必要なデータ数が足りない時は貯める
            elif self.xx_count < MAX_LEN_DATA + 2:
                self.rri_arr.append(self.rri)
                self.get_logger().info(f'RRI_data_len: {len(self.rri_arr)}')
    
    def run(self):
        while rclpy.ok():
            self.publish_pnnx()

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
