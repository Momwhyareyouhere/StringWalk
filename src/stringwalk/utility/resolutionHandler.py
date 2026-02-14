from .configHandler import readConfigItem
from PyQt6.QtWidgets import QApplication


async def getResolution():
    """
    Get the currently selected resolution.
    :return: single string
    """
    # Get the current resolution in the config
    resolution = await readConfigItem("current_resolution")

    if resolution is None:
        # Set a default resolution if the current resolution cannot be read
        resolution = "640x480"
        result = resolution
    else:
        result = resolution

    # Return result
    return result

def centerWindow(window):
    QApplication.processEvents()

    qr = window.frameGeometry()
    cp = window.screen().availableGeometry().center()

    qr.moveCenter(cp)

    window.move(qr.topLeft())

def lockWindowSize(window, width, height):
    window.setMinimumSize(width, height)
    window.setMaximumSize(width, height)
    window.resize(width, height)