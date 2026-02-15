from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QTimer
from .utility.qtMessageHandler import installQtMessageHandler
from .utility.ui.qssHandler import applyGlobalStyles
from .utility.data.projectNameHandler import getProjectName
from .utility.ui.resolutionHandler import getResolution, centerWindow, lockWindowSize
from .utility.data.textHandler import getText
from .gui.mainMenu import createMainMenu
from .gui.settingsMenu import createSettingsMenu
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

        def navigate(self, factory):
            """Replace central widget with a new menu instance."""
            widget = factory(self.navigate, parent=self)
            self.setCentralWidget(widget)

    async def setup():
        res = await getResolution()
        fullscreen_text = await getText("fullscreen")
        if isinstance(fullscreen_text, list):
            fullscreen_text = fullscreen_text[0]
    
        main_window = MainWindow()

        if res.lower() == fullscreen_text.lower():
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

    main_window = loop.run_until_complete(setup())

    with loop:
        loop.run_forever()

if __name__ == "__main__":
    try:
        gameExec()
    except Exception:
        print("Oh no! Something went wrong.")
        raise