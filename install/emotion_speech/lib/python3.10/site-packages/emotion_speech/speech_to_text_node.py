import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import pyaudio
import json
from vosk import Model, KaldiRecognizer

class SpeechToTextNode(Node):
    def __init__(self):
        super().__init__('speech_to_text_node')
        self.publisher_ = self.create_publisher(String, 'human_speech', 10)
        
        # Initialize Vosk model (make sure to set the correct model path)
        self.model = Model("/home/qaim/Downloads/vosk-model-small-en-us-0.15")
        self.recognizer = KaldiRecognizer(self.model, 16000)

        # Set up PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=8000)
        self.stream.start_stream()
        self.get_logger().info("Speech-to-text node started...")

    def run(self):
        while rclpy.ok():
            data = self.stream.read(4000, exception_on_overflow = False)
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "")
                if text:
                    msg = String()
                    msg.data = text
                    self.publisher_.publish(msg)
                    self.get_logger().info(f"Published human speech: {text}")

def main(args=None):
    rclpy.init(args=args)
    node = SpeechToTextNode()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
