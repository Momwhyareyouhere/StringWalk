from PyQt6.QtWidgets import QApplication
from ..utility.ui.asyncWidget import AsyncWidget
from PyQt6.QtGui import QPainter, QColor, QKeyEvent
from PyQt6.QtCore import Qt, QTimer

class GameWidget(AsyncWidget):
    def __init__(self, parent=None, on_exit=None):
        super().__init__()
        self.on_exit = on_exit
        self.setWindowTitle("Simple Game")
        self.setFixedSize(600, 400)

        # Player block properties
        self.player_x = 50
        self.player_y = 300
        self.player_width = 50
        self.player_height = 50
        self.player_color = QColor("red")
        self.speed = 5

        # Floor
        self.floor_y = 350
        self.floor_height = 50
        self.floor_color = QColor("darkgreen")

        # Timer to update the game (60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS

        # Currently pressed keys
        self.keys_pressed = set()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw floor
        painter.fillRect(0, self.floor_y, self.width(), self.floor_height, self.floor_color)

        # Draw player block
        painter.fillRect(self.player_x, self.player_y, self.player_width, self.player_height, self.player_color)

    def keyPressEvent(self, event: QKeyEvent):
        self.keys_pressed.add(event.key())
        self.handle_movement()

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() in self.keys_pressed:
            self.keys_pressed.remove(event.key())

    def handle_movement(self):
        if Qt.Key.Key_Left in self.keys_pressed:
            self.player_x = max(0, self.player_x - self.speed)
        if Qt.Key.Key_Right in self.keys_pressed:
            self.player_x = min(self.width() - self.player_width, self.player_x + self.speed)
        if Qt.Key.Key_Up in self.keys_pressed:
            self.player_y = max(0, self.player_y - self.speed)
        if Qt.Key.Key_Down in self.keys_pressed:
            self.player_y = min(self.floor_y - self.player_height, self.player_y + self.speed)

if __name__ == "__main__":
    app = QApplication([])
    window = GameWindow()
    window.show()
    app.exec()
