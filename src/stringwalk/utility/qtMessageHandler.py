from PyQt6.QtCore import qInstallMessageHandler, QtMsgType

def qtMessageHandler(mode, context, message):
    if "ffmpeg" in message.lower():
        return
    if "vdpau" in message.lower():
        return
    if "lsfg-vk" in message.lower():
        return
    if "qt.multimedia" in message.lower():
        return
    
    # Otherwise print normally
    print(message)

def installQtMessageHandler():
    qInstallMessageHandler(qtMessageHandler)