from PyQt6.QtCore import QObject, QEvent
from PyQt6.QtWidgets import QWidget
from ..audio.audioManager import audio

class SFXFilter(QObject):
    def eventFilter(self, obj, event):
        event_name = None
        if event.type() == QEvent.Type.MouseButtonPress:
            event_name = "MouseButtonPress"
        elif event.type() == QEvent.Type.MouseButtonRelease:
            event_name = "MouseButtonRelease"
        elif event.type() == QEvent.Type.Enter:
            event_name = "HoverEnter"
        elif event.type() == QEvent.Type.Leave:
            event_name = "HoverLeave"
        elif event.type() == QEvent.Type.Show:
            event_name = "PopupShow"

        if event_name:
            w = obj
            while w is not None:
                sfx = audio.get_sfx_for(w, event_name)
                if sfx:
                    audio.play_sfx(sfx)
                    break
                w = w.parent()

        return super().eventFilter(obj, event)