from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QPalette, QColor
import asyncio
import glob
from pathlib import Path
from ...utility.ui.menuHandler import makeMenuLayout, addMenuWidget, finalizeMenuLayout
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
            self.valid_resolution = True

            outer, inner = makeMenuLayout()

            self.layout_ref = inner
            self.setLayout(outer)

            self.all_task = asyncio.gather(
                readConfigItem("resolutions", default=["800x600"]),
                getText("back"),
                getResolution(),
                getText("fullscreen"),
                getText("maximized")
            )
            self.all_task.add_done_callback(self.__tasks_loaded)

        def __tasks_loaded(self, task):
            # Widget destroyed? Abort.
            if not self.isVisible():
                return
            if self.layout() is None:
                return
            if self.layout_ref is None:
                return

            try:
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

            self.res_dropdown = res_dropdown

            line = res_dropdown.lineEdit()
            line.textEdited.connect(self._validate_resolution)

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

            addMenuWidget(self.layout_ref, res_dropdown)
            
            QTimer.singleShot(0, lambda: res_dropdown.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter))

            # Back button
            back_btn = QPushButton(back_text)
            back_btn.clicked.connect(
                lambda: self.navigate(
                    __import__(f"{getProjectNameLower()}.gui.settingsMenu", fromlist=["createSettingsMenu"]).createSettingsMenu
                )
            )
            addMenuWidget(self.layout_ref, back_btn)

            self.layout_ref.addStretch()
            finalizeMenuLayout(self)

        def _validate_resolution(self, text):
            # Only validate numeric resolutions, ignore fullscreen/maximized
            if text.lower() in ("fullscreen", "maximized"):
                self._set_valid()
                return

            if "x" not in text.lower():
                self._set_invalid()
                return

            try:
                w, h = map(int, text.lower().split("x"))
            except ValueError:
                self._set_invalid()
                return

            # Minimum allowed resolution
            MIN_W, MIN_H = 640, 480

            if w < MIN_W or h < MIN_H:
                self._set_invalid()
            else:
                self._set_valid()

        def _set_invalid(self):
            self.valid_resolution = False
            line = self.res_dropdown.lineEdit()
            line.setStyleSheet("color: darkred;")

        def _set_valid(self):
            self.valid_resolution = True
            line = self.res_dropdown.lineEdit()
            line.setStyleSheet("color: white;")

        async def setResolutionAndReload(self, display_value):
            # Convert display - internal key
            resolution = self.reverse_map.get(display_value, display_value)

            # If invalid, do nothing
            if not self.valid_resolution:
                print("Resolution invalid — not applying")
                return

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

                def apply_lock():
                    lockWindowSize(window, width, height)
                    window.adjustSize()
                    centerWindow(window)

                QTimer.singleShot(0, apply_lock)

            except ValueError:
                print(f"Invalid resolution: {resolution}")

    return resolutionSelect(navigate, parent)