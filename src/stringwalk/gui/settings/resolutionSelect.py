from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
import asyncio
import glob
from pathlib import Path
from ...utility.configHandler import readConfigItem, writeConfigItem
from ...utility.jsonParser import parseJson
from ...utility.languageHandler import setLanguage
from ...utility.textHandler import getText
from ...utility.resolutionHandler import getResolution, centerWindow, lockWindowSize
from ...utility.projectNameHandler import getProjectNameLower
from functools import partial
import os


def createresolutionSelect(navigate, parent=None):
    class resolutionSelect(QWidget):
        def __init__(self, navigate, parent=None):
            super().__init__(parent)
            self.navigate = navigate

            self.layout_ref = QVBoxLayout()
            self.layout_ref.setContentsMargins(50, 50, 50, 50)
            self.layout_ref.setSpacing(20)
            self.layout_ref.addStretch()
            self.setLayout(self.layout_ref)

            self.all_task = asyncio.gather(
                readConfigItem("resolutions", default=["800x600"]),
                getText("back"),
                getResolution(),
                getText("fullscreen")
            )
            self.all_task.add_done_callback(self.__tasks_loaded)

        def __tasks_loaded(self, task):
            try:
                if not self.layout_ref: return
                resolutions, texts, current_res, fullscreen = task.result()
            except (RuntimeError, Exception):
                return
           
            # Dropdown menu
            res_dropdown = QComboBox()
            res_dropdown.setEditable(True)
            res_dropdown.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
            res_dropdown.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            res_dropdown.setMinimumHeight(40)
            res_dropdown.setMinimumWidth(200)

            res_dropdown.clear()

            items = list(resolutions)

            if fullscreen and fullscreen not in items:
                items.append(fullscreen)
            res_dropdown.addItems(items)
            if current_res and current_res not in items:
                res_dropdown.addItem(current_res)
            res_dropdown.setCurrentText(current_res)
            res_dropdown.currentTextChanged.connect(
                lambda r: asyncio.create_task(self.setResolutionAndReload(r))
            )
            self.layout_ref.addWidget(res_dropdown)

            # Back button
            back_btn = QPushButton(texts)
            back_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            back_btn.setMinimumHeight(40)
            back_btn.setMinimumWidth(200)
            back_btn.clicked.connect(
                lambda: self.navigate(
                    __import__(f"{getProjectNameLower()}.gui.settingsMenu", fromlist=["createSettingsMenu"]).createSettingsMenu
                )
            )
            self.layout_ref.addWidget(back_btn)

            self.layout_ref.addStretch()

        async def setResolutionAndReload(self, resolution):
            await writeConfigItem("current_resolution", resolution)

            window = self.nativeParentWidget()
            if not window:
                return

            fullscreen_text = (await getText("fullscreen"))
            if isinstance(fullscreen_text, list):
                fullscreen_text = fullscreen_text[0]

            if resolution.lower() == fullscreen_text.lower():
                window.showFullScreen()
            elif resolution.lower() == "maximized":
                window.showMaximized()
            else:
                try:
                    width, height = map(int, resolution.split("x"))
                    lockWindowSize(window, width, height)
                    window.adjustSize()
                    QTimer.singleShot(0, lambda: centerWindow(window))
                except ValueError:
                    print(f"Invalid resolution: {resolution}")

    return resolutionSelect(navigate, parent)