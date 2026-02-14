from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtCore import QTimer
from .utility.projectNameHandler import getProjectName
from .utility.resolutionHandler import getResolution, centerWindow, lockWindowSize
from .gui.mainMenu import createMainMenu
from .gui.settingsMenu import createSettingsMenu
import asyncio
import sys
import qasync
import nest_asyncio
nest_asyncio.apply()


def gameExec():
    # Create the Qt application
    app = QApplication(sys.argv)

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
        try:
            x, y = map(int, res.split("x"))
        except (ValueError, AttributeError):
            x, y = 800, 600
    
        main_window = MainWindow()
        lockWindowSize(main_window, x, y)
        main_window.navigate(createMainMenu)
        main_window.show()
        
        QTimer.singleShot(0, lambda: centerWindow(main_window))

    main_window = loop.run_until_complete(setup())

    with loop:
        loop.run_forever()

if __name__ == "__main__":
    try:
        gameExec()
    except Exception:
        print("Oh no! Something went wrong.")
        raise