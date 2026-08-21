from PyQt5.QtWidgets import QLabel, QMenu
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QMovie, QCursor


class DesktopPet(QLabel):
    open_player = pyqtSignal()
    next_track = pyqtSignal()
    prev_track = pyqtSignal()
    toggle_play = pyqtSignal()
    quit_app = pyqtSignal()

    def __init__(self, gif_path, x=100, y=100, size=150, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MoonPet")
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        self._drag_pos = None
        self._size = size

        self._movie = QMovie(gif_path)
        self.setMovie(self._movie)
        self._movie.start()

        self.setFixedSize(size, size)
        self.setGeometry(x, y, size, size)

        QTimer.singleShot(100, self._fit_to_gif)
        self.show()

    def _fit_to_gif(self):
        frame = self._movie.currentImage()
        if not frame.isNull():
            scaled = frame.size().scaled(self._size, self._size, Qt.KeepAspectRatio)
            self._movie.setScaledSize(scaled)
            self.setFixedSize(scaled)

    def resize_pet(self, size):
        self._size = size
        frame = self._movie.currentImage()
        if not frame.isNull():
            scaled = frame.size().scaled(size, size, Qt.KeepAspectRatio)
            self._movie.setScaledSize(scaled)
            self.setFixedSize(scaled)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_play.emit()

    def _show_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b3d;
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 4px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #6c5ce7;
                border-radius: 4px;
            }
        """)

        action_play = menu.addAction("  播放/暂停")
        action_next = menu.addAction("  下一首")
        action_prev = menu.addAction("  上一首")
        menu.addSeparator()
        action_open = menu.addAction("  打开播放器")
        menu.addSeparator()
        action_quit = menu.addAction("  退出")

        action = menu.exec_(QCursor.pos())
        if action is None:
            return
        if action == action_play:
            self.toggle_play.emit()
        elif action == action_next:
            self.next_track.emit()
        elif action == action_prev:
            self.prev_track.emit()
        elif action == action_open:
            self.open_player.emit()
        elif action == action_quit:
            self.quit_app.emit()
