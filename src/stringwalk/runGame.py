import asyncio
from qasync import QEventLoop
from .__main__ import gameExec
from PyQt6.QtWidgets import QApplication

def main():
    """Synchronous entry point for console/pyproject scripts."""
    app = QApplication([])

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    loop.create_task(gameExec())

    with loop:
        loop.run_forever()