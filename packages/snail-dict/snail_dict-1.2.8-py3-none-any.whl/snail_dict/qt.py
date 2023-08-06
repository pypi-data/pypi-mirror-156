from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWidgets import QWidget, QApplication, QVBoxLayout, QLineEdit
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import (
    Qt,
    QCoreApplication,
    QObject,
    QRunnable,
    QThreadPool,
    QMimeData,
)
from PyQt6.QtCore import pyqtSlot as slot
from PyQt6.QtCore import pyqtSignal as signal
import typing as t

GlobalColor = Qt.GlobalColor
WindowType = Qt.WindowType


class QThreadFuture(QRunnable):
    thread_pool = QThreadPool()
    thread_pool.setMaxThreadCount(1)

    class SignalHandler(QObject):
        done = signal(object)
        fail = signal(Exception)

    def __init__(self, task: t.Callable[..., t.Any], *args: t.Any):
        super().__init__()
        self.task = task
        self.result = self.SignalHandler()
        self.done = self.result.done
        self.fail = self.result.fail
        self.args = args

    def run(self):
        try:
            result = self.task(*self.args)
            self.result.done.emit(result)
        except Exception as err:
            self.result.fail.emit(err)

    def submit(self):
        self.thread_pool.start(self)
