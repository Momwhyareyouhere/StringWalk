from importlib import resources
from .audioManager import audio
from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer


def playSound(category: str, filename: str):
    """
    Categories: "music", "sfx", "ui" etc.
    Filename: "lobby.mp3", "click.wav" etc.
    """
    if category == "music":
        audio.play_music(filename)
    elif category == "sfx":
        audio.play_sfx(filename)