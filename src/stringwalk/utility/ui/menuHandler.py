from PyQt6.QtWidgets import QVBoxLayout


def makeMenuLayout():
    layout = QVBoxLayout()
    layout.setContentsMargins(50, 50, 50, 50)
    layout.setSpacing(20)
    layout.addStretch()
    return layout
