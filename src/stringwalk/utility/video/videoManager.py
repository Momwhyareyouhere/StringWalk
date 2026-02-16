from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QFrame
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtCore import QUrl, Qt, QSizeF

class VideoManager(QWidget):
    """Hardware-accelerated background video that fills the widget."""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Scene & view
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setFrameShape(QFrame.Shape.NoFrame)
        self.view.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        # Video item
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)

        # Media player
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.audio_output.setVolume(0)
        self.player.setAudioOutput(self.audio_output)
        self.player.setVideoOutput(self.video_item)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Fill the QGraphicsView
        self.view.setGeometry(self.rect())
        # Scale the video item to fill the view (keep aspect ratio)
        rect = self.view.rect()
        self.video_item.setSize(QSizeF(rect.width(), rect.height()))

    def play_video(self, filename: str):
        from pathlib import Path
        path = Path(__file__).resolve().parent.parent.parent / "assets" / "video" / filename
        if not path.exists():
            print(f"ERROR: Video not found: {path}")
            return
        self.player.setSource(QUrl.fromLocalFile(str(path)))
        self.player.setLoops(QMediaPlayer.Loops.Infinite)
        self.player.play()

    def stop_video(self):
        """Stops the video playback and resets the media player."""
        if self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            self.player.stop()
        # Optionally clear the video item
        self.player.setVideoOutput(None)