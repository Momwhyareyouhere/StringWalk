from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QSizePolicy
from ..utility.ui.asyncWidget import AsyncWidget
from ..utility.ui.menuHandler import makeMenuLayout, addMenuWidget, finalizeMenuLayout
from ..utility.data.textHandler import getText
from ..utility.audio.soundHandler import playSound
from ..utility.data.projectNameHandler import getProjectNameLower
from ..utility.ui.buttonHandler import create_action
from ..utility.video.videoManager import VideoManager
from ..gui.gameWidget import GameWidget
from functools import partial
import asyncio


def createMainMenu(navigate, parent=None):
    class MainMenu(AsyncWidget):
        def __init__(self, navigate, parent=None):
            super().__init__(parent)
            self.navigate = navigate
            self.parent_window = parent

            print(">>> MainMenu.__init__ called")
            print("    parent:", parent)
            print("    type(parent):", type(parent))
            print("    isinstance parent MainWindow?", isinstance(parent, QWidget))

            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            # Main layout
            outer, inner = makeMenuLayout()
            self.keys = ["start", "settings", "exit"]
            self.layout_ref = inner

            playSound("music", "lobby.mp3")

            self._reload_texts()

            self.setLayout(outer)

        def _reload_texts(self):
            """Fetch texts and rebuild buttons."""
            self.run_task(getText(self.keys), self.__texts_loaded)

        def __texts_loaded(self, task):
            texts = task.result()

            actions = [
                lambda w=None: self.start_game(),
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

        def start_game(self):
            if not self.parent_window:
                print("Error: parent_window is None! Cannot start game.")
                return

            # Stop background video
            if hasattr(self.parent_window, "video_manager"):
                try:
                    self.parent_window.video_manager.stop_video()
                except AttributeError:
                    print("Warning: video_manager.stop_video failed.")

            # Hide menu container
            if hasattr(self.parent_window, "menu_container"):
                self.parent_window.menu_container.hide()

            # Launch the game
            self.parent_window.game_widget = GameWidget(on_exit=self.return_to_menu)

        def return_to_menu(self):
            # Show menu container again when exiting game
            if self.parent_window and hasattr(self.parent_window, "menu_container"):
                self.parent_window.menu_container.show()

    return MainMenu(navigate, parent=parent)
