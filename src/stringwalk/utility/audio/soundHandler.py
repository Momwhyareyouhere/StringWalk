from importlib import resources
from .audioManager import get_audio
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer


def playSound(category: str, filename: str):
    """
    Categories: "music", "sfx", "ui" etc.
    Filename: "lobby.mp3", "click.wav" etc.
    """
    audio = get_audio()
    if category == "music":
        audio.play_music(filename)
    elif category == "sfx":
        audio.play_sfx(filename)


def stopSound(category: str):
    audio = get_audio()
    if category == "music":
        audio.stop_music()
