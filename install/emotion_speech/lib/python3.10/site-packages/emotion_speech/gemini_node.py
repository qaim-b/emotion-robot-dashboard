#!/usr/bin/env python3
from gtts import gTTS
import tempfile
import subprocess
import threading
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from example_interfaces.srv import Trigger    # <-- ROS 2 service import
import os
import google.generativeai as genai

class GeminiResponder(Node):
    def __init__(self):
        super().__init__('gemini_responder')

        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

        # Memory + service
        self.user_id       = 'default_user'
        self.turn_index    = 1
        self.current_valence = 0.0

        # Emotion & STT flow control
        self.current_emotion   = None
        self._stt_enabled      = True
        self._capturing        = False
        self._captured_text    = []
        self._capture_timer    = None

        # TTS lock & timer
        self.last_heard        = None
        self._speech_timer     = None
        self._speaking_lock    = threading.Lock()

        # Prevent self-echo
        self._last_bot_reply   = None

        # Subscriptions
        self.create_subscription(String, 'emotion_state', self.emotion_callback, 10)
        self.create_subscription(String, 'human_speech',   self.human_speech_callback, 10)

        # ROS2 Service client for memory context
        self.mem_cli = self.create_client(Trigger, 'get_context_memories')
        while not self.mem_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for get_context_memories service...')
        self.mem_req = Trigger.Request()

        # GUI sync publisher
        self.speak_pub = self.create_publisher(String, 'speak_emotion', 10)
        self.get_logger().info("Gemini responder node started; waiting for input...")

        # Hold user text for context fetch
        self._pending_user_text = None
        self._pending_mood      = None

    def emotion_callback(self, msg):
        state = msg.data.strip().lower()
        if state not in ('pleasure', 'unpleasure') or state == self.current_emotion:
            return
        self.current_emotion = state
        # Map emotion to valence: pleasure=1.0, unpleasure=-1.0
        self.current_valence = 1.0 if state == 'pleasure' else -1.0
        self.get_logger().info(f"[EMOTION] {self.current_emotion} (valence: {self.current_valence})")
        self.speak_pub.publish(String(data=self.current_emotion))

    def human_speech_callback(self, msg):
        text = msg.data.strip()

        # 1) Drop transcripts of our own last reply:
        if self._last_bot_reply and self._last_bot_reply.lower() in text.lower():
            return

        # 2) Drop anything while TTS is playing
        if self._speaking_lock.locked():
            return

        # 3) Drop if STT disabled or no emotion yet
        if not text or not self._stt_enabled or self.current_emotion is None:
            return

        # Begin 5 s capture window on first snippet
        if not self._capturing:
            self._capturing     = True
            self._captured_text = []
            self.get_logger().info("🔴 Starting 5s capture of user speech")
            threading.Thread(target=self._countdown, args=(5,), daemon=True).start()
            self._capture_timer = threading.Timer(5.0, self._on_capture_complete)
            self._capture_timer.start()

        # Accumulate all snippets
        self._captured_text.append(text)

    def _countdown(self, seconds):
        for remaining in range(seconds, 0, -1):
            self.get_logger().info(f"⏳ Capture ends in {remaining}s…")
            time.sleep(1)
        self.get_logger().info("✅ Capture window ended")

    def _on_capture_complete(self):
        # Stop further STT until after response
        self._stt_enabled = False
        full_text = ' '.join(self._captured_text)
        self.get_logger().info(f"[CAPTURE COMPLETE] \"{full_text}\"")
        self._process_user_speech(full_text)

    # --- Async Service Call ---
    def fetch_context_from_memory_service(self, user_text, mood):
        future = self.mem_cli.call_async(self.mem_req)
        # Store pending values so callback can access
        self._pending_user_text = user_text
        self._pending_mood = mood
        future.add_done_callback(self.on_memory_service_response)

    def on_memory_service_response(self, future):
        try:
            context_string = ""
            result = future.result()
            if result is not None and getattr(result, 'success', True):  # Trigger always has 'success'
                context_string = result.message if hasattr(result, 'message') else ""
        except Exception as e:
            self.get_logger().error(f"Memory service call failed: {e}")
            context_string = ""

        # Continue processing with context
        self._process_gemini_response(self._pending_user_text, self._pending_mood, context_string)

        # Clear pending
        self._pending_user_text = None
        self._pending_mood = None

    def _process_user_speech(self, user_text):
        mood = "pleasant" if self.current_emotion == 'pleasure' else "unpleasant"

        # 1. MEMORY CONTEXT via SERVICE (async)!
        self.fetch_context_from_memory_service(user_text, mood)

        # All further processing happens in on_memory_service_response

    def _process_gemini_response(self, user_text, mood, context_string):
        # 2. Build prompt with context
        prompt = (
            f"You are an open-minded, friendly robot. The user is feeling {mood} and said: \"{user_text}\".\n"
        )
        if context_string:
            prompt += "Here are some things the user said previously and how the robot replied:\n"
            prompt += context_string + "\n"
        prompt += "Respond kindly in one sentence, without emojis."

        self.get_logger().info(f"[PROMPT] {prompt}")

        try:
            response = self.model.generate_content(prompt)
            reply = response.text if response and hasattr(response, 'text') else "Sorry, I didn’t catch that."

            # **Remember what we just said** so we can ignore it
            self._last_bot_reply = reply

            self.get_logger().info(f"Gemini → {reply}")

            # Prevent overlap and robot self-capture
            if not self._speaking_lock.acquire(blocking=False):
                self.get_logger().info("🛑 Still speaking—skipping this utterance")
                return

            try:
                tts = gTTS(text=reply, lang='en')
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                    tts.save(fp.name)
                    subprocess.run(["mpg123", fp.name])
            finally:
                self._speaking_lock.release()

        except Exception as e:
            self.get_logger().error(f"Error in Gemini or TTS: {e}")
        finally:
            # **Delay re-enable** STT so we never capture lingering echo
            self.get_logger().info("🎤 Response done—STT will re-enable in 1s")
            self._capturing = False
            self.turn_index += 1  # Move turn forward after every user-bot exchange
            threading.Timer(1.0, self._enable_stt).start()

    def _enable_stt(self):
        self._stt_enabled = True
        self.get_logger().info("🔓 STT re-enabled")

def main(args=None):
    rclpy.init(args=args)
    node = GeminiResponder()
    try:
        rclpy.spin(node)
    finally:
        if node._capture_timer:
            node._capture_timer.cancel()
        if node._speech_timer:
            node._speech_timer.cancel()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

