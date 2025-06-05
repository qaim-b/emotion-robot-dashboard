#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class PnnxToEmotionNode(Node):
    def __init__(self):
        super().__init__('pnnx_to_emotion_node')
        self.create_subscription(
            String,
            'pnnx2',
            self.listener_callback,
            10
        )
        self.publisher_ = self.create_publisher(String, 'emotion_state', 10)
        self.get_logger().info('pnnx_to_emotion_node started.')

    def listener_callback(self, msg):
        raw = msg.data.strip()
        emotion = self.map_pnnx_to_emotion(raw)
        self.get_logger().info(f'Mapped Emotion: {emotion}')
        out = String()
        out.data = emotion
        self.publisher_.publish(out)

    def map_pnnx_to_emotion(self, raw_value):
        """
        raw_value may be:
         - a numeric string (pNN50, e.g. "0.27")
         - or a legacy label like "Q1: Excited"
        We map both into two states: 'pleasure' vs 'unpleasure'.
        """
        # 1) Try numeric interpretation
        try:
            pnn50 = float(raw_value)
            threshold = 0.236
            return "pleasure" if pnn50 > threshold else "unpleasure"
        except ValueError:
            # 2) Fallback to quadrant label
            quadrant = raw_value.split(":", 1)[0].upper()  # e.g. "Q1"
            if quadrant in ("Q1", "Q4"):
                return "pleasure"
            else:
                return "unpleasure"

def main(args=None):
    rclpy.init(args=args)
    node = PnnxToEmotionNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

