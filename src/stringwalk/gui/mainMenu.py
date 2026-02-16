from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QSizePolicy, QVBoxLayout
from ..utility.ui.menuHandler import makeMenuLayout, addMenuWidget, finalizeMenuLayout
from ..utility.data.textHandler import getText
from ..utility.audio.soundHandler import playSound
from ..utility.data.projectNameHandler import getProjectNameLower
from ..utility.ui.buttonHandler import handleButton
from functools import partial
import asyncio


def createMainMenu(navigate, parent=None):
    class MainMenu(QWidget):
        def __init__(self, navigate, parent=None):
            super().__init__(parent)
            self.navigate = navigate

            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            # Main layout
            outer, inner = makeMenuLayout()

            self.keys = ["start", "settings", "exit"]
            self.layout_ref = inner
    
            loop = asyncio.get_event_loop()

            playSound("music", "lobby.mp3")

            task = loop.create_task(getText(self.keys))
            task.add_done_callback(self.__texts_loaded)

            self.setLayout(outer)

        def __texts_loaded(self, task):
            texts = task.result()

            actions = [
                lambda w=None: print("Start pressed!"),
                lambda w=None: self.navigate(
                    __import__(
                        f"{getProjectNameLower()}.gui.settingsMenu",
                        fromlist=["createSettingsMenu"]
                    ).createSettingsMenu
                ),
                lambda w=None: QApplication.quit()
            ]

            for text, action in zip(texts, actions):
                btn = QPushButton(text)
                btn.clicked.connect(partial(handleButton, action, self))
                addMenuWidget(self.layout_ref, btn)

            self.layout_ref.addStretch()
            finalizeMenuLayout(self)

    return MainMenu(navigate)
