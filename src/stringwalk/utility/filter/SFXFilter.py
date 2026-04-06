from PyQt6.QtCore import QObject, QEvent
from PyQt6.QtWidgets import QWidget
from ..audio.audioManager import get_audio

class SFXFilter(QObject):
    def eventFilter(self, obj, event):
        # Only handle mouse press/release and hover events
        if event.type() in (QEvent.Type.MouseButtonPress,
                            QEvent.Type.MouseButtonRelease,
                            QEvent.Type.Enter,
                            QEvent.Type.Leave,
                            QEvent.Type.Show):
            audio = get_audio()
            sfx = audio.get_sfx_for(obj, event.type().name)
            if sfx:
                audio.play_sfx(sfx)
        return super().eventFilter(obj, event)
