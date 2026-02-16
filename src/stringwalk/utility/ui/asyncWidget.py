from PyQt6.QtWidgets import QWidget
from .menuRefresh import register_menu
import asyncio

class AsyncWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        register_menu(self)

    def run_task(self, coro, callback):
        task = asyncio.create_task(coro)
        task.add_done_callback(callback)
        self._tasks.append(task)
        return task

    def rebuild_buttons(self, back_text):
        """Clear existing buttons and recreate language + back buttons."""
        # Remove all widgets from the layout except stretches
        for i in reversed(range(self.layout_ref.count())):
            item = self.layout_ref.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        # Add language buttons
        for name, code in self.languages:
            lang_btn = QPushButton(name)
            lang_btn.setProperty("variant", "setting")
            lang_btn.clicked.connect(lambda checked, c=code: asyncio.create_task(self.setLanguageAndReload(c)))
            addMenuWidget(self.layout_ref, lang_btn)

        # Add back button
        back_btn = QPushButton(back_text)
        back_btn.clicked.connect(
            lambda: self.navigate(
                __import__(f"{getProjectNameLower()}.gui.settingsMenu", fromlist=["createSettingsMenu"]).createSettingsMenu
            )
        )
        addMenuWidget(self.layout_ref, back_btn)

        self.layout_ref.addStretch()
        finalizeMenuLayout(self)

    def closeEvent(self, event):
        for t in self._tasks:
            if not t.done():
                t.cancel()
        super().closeEvent(event)