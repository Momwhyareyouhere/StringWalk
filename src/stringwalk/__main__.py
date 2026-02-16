from PyQt6.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget, QVBoxLayout, QStackedLayout
from PyQt6.QtCore import Qt, QTimer
from .utility.qtMessageHandler import installQtMessageHandler
from .utility.filter.SFXFilter import SFXFilter
from .utility.video.videoManager import VideoManager
from .utility.ui.qssProcessor import applyGlobalStyles
from .utility.data.projectNameHandler import getProjectName
from .utility.ui.resolutionHandler import getResolution, centerWindow, lockWindowSize
from .gui.mainMenu import createMainMenu
import asyncio
import sys
import qasync
import nest_asyncio
nest_asyncio.apply()


def gameExec():
    # Configure logging
    installQtMessageHandler()

    # Create the Qt application
    app = QApplication(sys.argv)

    sfx_filter = SFXFilter()
    app.installEventFilter(sfx_filter)

    # Try applying the global styling on the application
    try:
        applyGlobalStyles(app, "gui/styles")
    except Exception as err:
        print(f"Styling couldn't be loaded: {err}")

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            title = getProjectName()
            self.setWindowTitle(title)

            # Central container
            self.central_container = QWidget(self)
            self.setCentralWidget(self.central_container)

            # Video background (fills whole container)
            self.video_manager = VideoManager(self.central_container)
            self.video_manager.setGeometry(self.central_container.rect())
            self.video_manager.show()
            self.video_manager.play_video("lobby.mp4")

            # Menu container on top (transparent)
            self.menu_container = QWidget(self.central_container)
            self.menu_container.setGeometry(self.central_container.rect())
            self.menu_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.menu_container.raise_()
            self.menu_container.show()

            # Stacked layout for smooth menu switching
            self.menu_layout = QStackedLayout(self.menu_container)
            self.menu_layout.setContentsMargins(0, 0, 0, 0)

            # Store already-created menus to avoid flicker
            self.menu_widgets = {}

        def navigate(self, factory):
            """Replace central widget with a new menu instance."""
            widget = factory(self.navigate)
            widget.setSizePolicy( QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding )
            self.setCentralWidget(widget)

            # Switch instantly
            self.menu_layout.setCurrentWidget(self.menu_widgets[key])

        def changeEvent(self, event):
            super().changeEvent(event)

            if event.type() == event.Type.WindowStateChange:
                new = self.windowState()
                old = event.oldState()

                # KDE fullscreen → normal fix
                if old == Qt.WindowState.WindowFullScreen and new == Qt.WindowState.WindowNoState:
                    # Step 1: hide to force decoration recalculation
                    self.hide()

                    # Step 2: showNormal and center after decorations are applied
                    QTimer.singleShot(0, lambda: self._kde_restore_and_center())
                    return

                # Normal unmaximize case
                if new == Qt.WindowState.WindowNoState:
                    QTimer.singleShot(0, lambda: centerWindow(self))

        def _kde_restore_and_center(self):
            self.showNormal()
            QTimer.singleShot(0, lambda: centerWindow(self))

        def resizeEvent(self, event):
            super().resizeEvent(event)
            self.video_manager.setGeometry(self.central_container.rect())
            self.menu_container.setGeometry(self.central_container.rect())

    async def setup():
        res = await getResolution()
    
        main_window = MainWindow()

        if res.lower() == "fullscreen":
            main_window.showFullScreen()
        elif res.lower() == "maximized":
            main_window.showMaximized()
        else:
            try:
                x, y = map(int, res.split("x"))
            except ValueError:
                x, y = 800, 600
            lockWindowSize(main_window, x, y)
            main_window.show()    
            QTimer.singleShot(0, lambda: centerWindow(main_window))

        main_window.navigate(createMainMenu)

        return main_window
    
    main_window = loop.run_until_complete(setup())

    with loop:
        loop.run_forever()

if __name__ == "__main__":
    try:
        gameExec()
    except Exception:
        print("Oh no! Something went wrong.")
        raise