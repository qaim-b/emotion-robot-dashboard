from gtts import gTTS
import os

text = "Dear Mami, the Coolest of Them All, You've got the vibes, the charm, the style—no doubt! But there's one noble quest you've yet to fulfill... To treat our hero Qaim with sweetness and thrill. 🍦🎬 A scoop of ice cream, a movie to delight— Let tonight be magic, cozy and right. Say yes, and let the good vibes ignite! 💫"
tts = gTTS(text)
tts.save("test.mp3")
os.system("mpg123 test.mp3")

