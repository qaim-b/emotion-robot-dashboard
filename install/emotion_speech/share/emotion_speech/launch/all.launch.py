#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1) Pulse-sensor publisher (pNN50 measurements)
        Node(
            package='emotion_speech',
            executable='pnnx2',               # or 'test_publisher' if you’re still mocking
            name='pulse_sensor_node',
            output='screen'
        ),

        # 2) pNN50 → Emotion mapping (pleasure/unpleasure)
        Node(
            package='emotion_speech',
            executable='pnnx_to_emotion_node',
            name='emotion_mapper_node',
            output='screen'
        ),

        # 3) Speech-to-Text node
        Node(
            package='emotion_speech',
            executable='speech_to_text_node',
            name='speech_to_text_node',
            output='screen'
        ),

        # 4) Gemini LLM response + TTS
        Node(
            package='emotion_speech',
            executable='gemini_node',
            name='gemini_node',
            output='screen'
        ),

        # 5) Face-display GUI node
        Node(
            package='emotion_speech',
            executable='face_display_node',
            name='face_display_node',
            output='screen'
        ),
    ])

