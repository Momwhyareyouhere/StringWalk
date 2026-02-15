from PyQt6.QtWidgets import QWidget, QPushButton, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
import asyncio
import glob
from pathlib import Path
from ...utility.ui.menuHandler import makeMenuLayout, addMenuWidget, finalizeMenuLayout
from ...utility.jsonParser import parseJson
from ...utility.data.languageHandler import setLanguage
from ...utility.data.textHandler import getText
from ...utility.data.projectNameHandler import getProjectNameLower
from functools import partial
import os


def createlangSelect(navigate, parent=None):
    class langSelect(QWidget):
        def __init__(self, navigate, parent=None):
            super().__init__(parent)
            self.navigate = navigate

            outer, inner = makeMenuLayout()

            self.layout_ref = inner
            self.setLayout(outer)

            current_dir = Path(__file__).resolve().parent
            i18n_dir = current_dir.parent.parent / "i18n"
            files = glob.glob(str(i18n_dir / "*.json"))

            self.languages = []
            for f in files:
                path = Path(f)
                code = path.stem
                name = parseJson(f, "lang_name")
                if name:
                    self.languages.append((name, code))

            loop = asyncio.get_event_loop()
            task = loop.create_task(getText("back"))
            task.add_done_callback(self.__texts_loaded)

        def __texts_loaded(self, task):
            try:
                if self.layout_ref is None: return
            except RuntimeError:
                return

            try:
                if not self.isVisible() or self.layout_ref is None:
                    return
            except (RuntimeError, AttributeError):
                return

            texts = task.result()

            # Create language buttons
            for name, code in self.languages:
                lang_btn = QPushButton(name)
                lang_btn.clicked.connect(lambda checked, c=code: asyncio.create_task(self.setLanguageAndReload(c)))
                addMenuWidget(self.layout_ref, lang_btn)

            # Back button
            back_btn = QPushButton(texts)
            back_btn.clicked.connect(
                lambda: self.navigate(
                    __import__(f"{getProjectNameLower()}.gui.settingsMenu", fromlist=["createSettingsMenu"]).createSettingsMenu
                )
            )
            addMenuWidget(self.layout_ref, back_btn)

            self.layout_ref.addStretch()
            finalizeMenuLayout(self)

        async def setLanguageAndReload(self, lang_code):
            await setLanguage(lang_code)

            # Reload settings menu
            self.navigate(
                __import__(
                    f"{getProjectNameLower()}.gui.settingsMenu",
                    fromlist=["createSettingsMenu"]
                ).createSettingsMenu
            )

    return langSelect(navigate, parent)
