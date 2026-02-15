from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
import asyncio
import glob
from pathlib import Path
from ...utility.configHandler import readConfigItem, writeConfigItem
from ...utility.jsonParser import parseJson
from ...utility.data.languageHandler import setLanguage
from ...utility.data.textHandler import getText
from ...utility.ui.resolutionHandler import getResolution, lockWindowSize, centerWindow
from ...utility.data.projectNameHandler import getProjectNameLower
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
                getText("fullscreen"),
                getText("maximized")
            )
            self.all_task.add_done_callback(self.__tasks_loaded)

        def __tasks_loaded(self, task):
            try:
                if not self.layout_ref:
                    return
                resolutions, back_text, current_res, fullscreen_disp, maximized_disp = task.result()
            except Exception:
                return

            # Normalize display texts
            if isinstance(fullscreen_disp, list):
                fullscreen_disp = fullscreen_disp[0]
            if isinstance(maximized_disp, list):
                maximized_disp = maximized_disp[0]

            # Build internal - display map
            internal_items = list(resolutions)
            internal_items += ["fullscreen", "maximized"]

            display_map = {
                "fullscreen": fullscreen_disp,
                "maximized": maximized_disp
            }

            # Normal resolutions display as-is
            for r in resolutions:
                display_map[r] = r

            # Reverse map for saving
            self.reverse_map = {v: k for k, v in display_map.items()}

            # Dropdown menu
            res_dropdown = QComboBox()
            res_dropdown.setEditable(True)
            res_dropdown.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
            res_dropdown.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            res_dropdown.setMinimumHeight(40)
            res_dropdown.setMinimumWidth(200)

            # Populate dropdown with display values
            display_items = [display_map[i] for i in internal_items]
            res_dropdown.addItems(display_items) 

            # Set current resolution (convert internal - display)
            res_dropdown.setCurrentText(display_map.get(current_res, current_res))

            # Connect
            res_dropdown.currentTextChanged.connect(
                lambda display_value: asyncio.create_task(
                    self.setResolutionAndReload(display_value)
                )
            )

            self.layout_ref.addWidget(res_dropdown)

            # Back button
            back_btn = QPushButton(back_text)
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

        async def setResolutionAndReload(self, display_value):
            # Convert display - internal key
            resolution = self.reverse_map.get(display_value, display_value)

            # Save internal key
            await writeConfigItem("current_resolution", resolution)

            window = self.nativeParentWidget()
            if not window:
                return

            if resolution == "fullscreen":
                window.showFullScreen()
                return
            if resolution == "maximized":
                window.showMaximized()
                return

            try:
                width, height = map(int, resolution.split("x"))
                window.showNormal()
                lockWindowSize(window, width, height)
                window.adjustSize()
                QTimer.singleShot(0, lambda: centerWindow(window))
            except ValueError:
                print(f"Invalid resolution: {resolution}")

    return resolutionSelect(navigate, parent)