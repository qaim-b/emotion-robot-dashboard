import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time

class EmotionPublisher(Node):
    def __init__(self):
        super().__init__('emotion_publisher')
        self.publisher_ = self.create_publisher(String, 'emotion_state', 10)

        # Publish some emotions for testing
        emotions = ['happy', 'sad', 'stressed', 'excited']
        for emotion in emotions:
            msg = String()
            msg.data = emotion
            self.get_logger().info(f'Publishing emotion: {emotion}')
            self.publisher_.publish(msg)
            time.sleep(5)  # wait a bit before sending next one

def main(args=None):
    rclpy.init(args=args)
    node = EmotionPublisher()
    time.sleep(1)  # give it a second to connect
    rclpy.spin_once(node, timeout_sec=1.0)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

