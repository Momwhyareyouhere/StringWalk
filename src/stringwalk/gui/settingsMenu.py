from PyQt6.QtWidgets import QWidget, QPushButton, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from ..utility.ui.menuHandler import makeMenuLayout, addMenuWidget, finalizeMenuLayout
from ..utility.data.textHandler import getText
from ..utility.data.projectNameHandler import getProjectNameLower
from ..utility.ui.buttonHandler import handleButton
from functools import partial
import asyncio


def createSettingsMenu(navigate, parent=None):
    class SettingsMenu(QWidget):
        def __init__(self, navigate, parent=None):
            super().__init__(parent)
            self.navigate = navigate

            outer, inner = makeMenuLayout()

            self.keys = ["language", "resolution", "back"]
            self.layout_ref = inner

            loop = asyncio.get_event_loop()
            task = loop.create_task(getText(self.keys))
            task.add_done_callback(self.__texts_loaded)

            self.setLayout(outer)

        def __texts_loaded(self, task):
            texts = task.result()

            actions = [
                lambda w=None: self.navigate(
                    __import__(
                        f"{getProjectNameLower()}.gui.settings.langSelect",
                        fromlist=["createlangSelect"]
                    ).createlangSelect
                ),
                lambda w=None: self.navigate(
                    __import__(
                        f"{getProjectNameLower()}.gui.settings.resolutionSelect",
                        fromlist=["createresolutionSelect"]
                    ).createresolutionSelect
                ),
                lambda w=None: self.navigate(
                    __import__(
                        f"{getProjectNameLower()}.gui.mainMenu",
                        fromlist=["createMainMenu"]
                    ).createMainMenu
                ),
            ]

            for text, action in zip(texts, actions):
                btn = QPushButton(text)
                btn.clicked.connect(partial(handleButton, action, self))
                addMenuWidget(self.layout_ref, btn)

            self.layout_ref.addStretch()
            finalizeMenuLayout(self)

    return SettingsMenu(navigate, parent)
