import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import tkinter as tk
from PIL import Image, ImageTk
import os
import random

class FaceDisplayNode(Node):
    def __init__(self):
        super().__init__('face_display_node')

        self.subscription = self.create_subscription(
            String,
            'speak_emotion',
            self.update_face,
            10)

        # Create the GUI window
        self.root = tk.Tk()
        self.root.title("Robot Face")

        self.label = tk.Label(self.root)
        self.label.pack()

        # Correct path to face_DB
        from ament_index_python.packages import get_package_share_directory
        self.face_dir = os.path.join(get_package_share_directory('emotion_speech'), 'face_DB')


        # Show default neutral face
        self.show_image("neutral.JPG")

        # Start GUI loop
        self.update_gui()

    def show_image(self, filename):
        try:
            img_path = os.path.join(self.face_dir, filename)
            img = Image.open(img_path)
            img = img.resize((300, 300))  # Adjust size if needed
            photo = ImageTk.PhotoImage(img)
            self.label.config(image=photo)
            self.label.image = photo  # Keep a reference
        except Exception as e:
            self.get_logger().error(f"Could not load image {filename}: {e}")

    def update_face(self, msg):
        emotion = msg.data.strip().lower()
        self.get_logger().info(f"Received emotion for GUI: {emotion}")

        if "q1" in emotion:
            folder = "happy"
        elif "q2" in emotion:
            folder = "anger"
        elif "q3" in emotion:
            folder = "sadness"
        elif "q4" in emotion:
            folder = "relax"
        else:
            self.show_image("neutral.JPG")
            return

        # Pick a random face from 1 to 5
        face_name = f"{folder}{random.randint(1,5)}.JPG"
        self.show_image(face_name)

    def update_gui(self):
        self.root.update()
        self.root.after(100, self.update_gui)

def main(args=None):
    rclpy.init(args=args)
    node = FaceDisplayNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

