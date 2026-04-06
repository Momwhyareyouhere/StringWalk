from PyQt6.QtWidgets import QPushButton
from ..audio.audioManager import get_audio


def handleButton(action, widget=None):
    """
    Universal handler: executes the action passed.
    The menu decides which action to pass per button.
    """
    if callable(action):
        action(widget)

def create_action(button: QPushButton, func):
    """
    Wraps a function with SFX logic.
    Ensures SFX only plays when clicking the actual button area.
    """
    def wrapper(event=None):
        if isinstance(button, QPushButton):
            # Only play SFX if event position is inside the button
            if event is None or button.rect().contains(button.mapFromGlobal(event.globalPosition().toPoint())):
                audio = get_audio()
                sfx = audio.get_sfx_for(button, "MouseButtonPress")
                if sfx:
                    audio.play_sfx(sfx)

        # Call the real action
        func()

    return wrapper
