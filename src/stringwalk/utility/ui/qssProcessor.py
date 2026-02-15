from pathlib import Path
from PyQt6.QtWidgets import QApplication


def applyGlobalStyles(app, folder_name="styles"):
    """
    Reads out all QSS files from a folder and applies them to the application.
    """
    combined_qss = ""

    # Searches the directory relative to the root of the project
    base_path = Path(__file__).parent.parent.parent / folder_name

    if base_path.exists():
        for qss_file in sorted(base_path.glob("*.qss")):
            with open(qss_file, "r", encoding="utf-8") as f:
                combined_qss += f.read() + "\n"

    app.setStyleSheet(combined_qss)