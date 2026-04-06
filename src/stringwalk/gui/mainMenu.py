from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QSizePolicy
from ..utility.ui.asyncWidget import AsyncWidget
from ..utility.ui.menuHandler import makeMenuLayout, addMenuWidget, finalizeMenuLayout
from ..utility.data.textHandler import getText
from ..utility.data.projectNameHandler import getProjectNameLower
from ..utility.ui.buttonHandler import create_action
from functools import partial
import asyncio


def createMainMenu(navigate, parent=None):
    class MainMenu(AsyncWidget):
        def __init__(self, navigate, parent=None):
            super().__init__(parent)
            self.navigate = navigate
            self.parent_window = parent

            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            # Main layout
            outer, inner = makeMenuLayout()
            self.keys = ["start", "settings", "exit"]
            self.layout_ref = inner

            self._reload_texts()

            self.setLayout(outer)

        def _reload_texts(self):
            """Fetch texts and rebuild buttons."""
            self.run_task(getText(self.keys), self.__texts_loaded)

        def __texts_loaded(self, task):
            texts = task.result()

            actions = [
                lambda w=None: self.navigate(
                    __import__(
                        f"{getProjectNameLower()}.gui.lobbyMenu",
                        fromlist=["createLobbyMenu"]
                    ).createLobbyMenu,
                    key="LobbyMenu",
                    parent=self.parent_window
                ),
                lambda w=None: self.navigate(
                    __import__(
                        f"{getProjectNameLower()}.gui.settingsMenu",
                        fromlist=["createSettingsMenu"]
                    ).createSettingsMenu,
                    key="SettingsMenu",
                    parent=self.parent_window
                ),
                lambda w=None: QApplication.quit()
            ]

            # Clear old widgets first
            for i in reversed(range(self.layout_ref.count())):
                item = self.layout_ref.itemAt(i)
                widget = item.widget()
                if widget:
                    widget.setParent(None)

            # Add buttons
            for text, action in zip(texts, actions):
                btn = QPushButton(text)
                btn.clicked.connect(action)
                addMenuWidget(self.layout_ref, btn)

            self.layout_ref.addStretch()
            finalizeMenuLayout(self)

    return MainMenu(navigate, parent=parent)
