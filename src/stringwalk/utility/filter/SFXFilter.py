from PyQt6.QtCore import QObject, QEvent
from PyQt6.QtWidgets import QPushButton
from ..audio.audioManager import audio

class ButtonSFXFilter(QObject):
    def eventFilter(self, obj, event):
        if isinstance(obj, QPushButton) and event.type() == QEvent.Type.MouseButtonPress:
            audio.play_sfx("button_click.mp3")
        return super().eventFilter(obj, event)