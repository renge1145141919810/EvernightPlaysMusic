import os
import sys

if getattr(sys, 'frozen', False):
    _RESOURCE_DIR = sys._MEIPASS
else:
    _RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QListWidget, QListWidgetItem, QFileDialog,
    QMessageBox, QComboBox, QTabWidget, QAbstractItemView,
    QFrame, QMenu
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QPixmap
from scanner import scan_folders
from config_manager import save_config

BG_IMAGE = os.path.join(_RESOURCE_DIR, "longmoon.webp")

BTN_STYLE = """
    QPushButton {
        background-color: rgba(108, 92, 231, 0.55);
        color: #f0f0f0;
        border: 1px solid rgba(108, 92, 231, 0.7);
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 13px;
    }
    QPushButton:hover { background-color: rgba(108, 92, 231, 0.75); }
    QPushButton:pressed { background-color: rgba(108, 92, 231, 0.9); }
"""

BTN_PLAY_STYLE = """
    QPushButton {
        background-color: rgba(108, 92, 231, 0.65);
        color: white; border: none; border-radius: 20px;
        font-size: 18px; min-width: 40px; max-width: 40px;
        min-height: 40px; max-height: 40px;
    }
    QPushButton:hover { background-color: rgba(125, 109, 247, 0.8); }
"""

BTN_CTRL_STYLE = """
    QPushButton {
        background-color: rgba(108, 92, 231, 0.45);
        color: #e0e0e0; border: none; border-radius: 6px;
        font-size: 16px; min-width: 36px; max-width: 36px;
        min-height: 36px; max-height: 36px;
    }
    QPushButton:hover { background-color: rgba(108, 92, 231, 0.7); }
"""

BTN_SMALL_STYLE = """
    QPushButton {
        background-color: rgba(108, 92, 231, 0.45);
        color: #e0e0e0; border: none; border-radius: 6px;
        padding: 5px 10px; font-size: 12px;
    }
    QPushButton:hover { background-color: rgba(108, 92, 231, 0.7); }
"""

BTN_FAV_STYLE = """
    QPushButton {
        background-color: transparent; color: #e0e0e0;
        border: none; font-size: 18px; padding: 4px 8px;
    }
    QPushButton:hover { background-color: rgba(108, 92, 231, 0.3); border-radius: 4px; }
"""


class MusicPlayerWindow(QWidget):
    play_index = pyqtSignal(int)
    pause_signal = pyqtSignal()
    resume_signal = pyqtSignal()
    stop_signal = pyqtSignal()
    next_signal = pyqtSignal()
    prev_signal = pyqtSignal()
    volume_changed = pyqtSignal(float)
    mode_changed = pyqtSignal(str)
    playlist_changed = pyqtSignal(list)
    favorites_changed = pyqtSignal(list)

    MODES = [
        ("sequential", "顺序播放"),
        ("loop", "列表循环"),
        ("single", "单曲循环"),
        ("random", "随机播放"),
    ]

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.songs = []
        self.all_songs = []
        self.favorites = set(config.get("favorite_songs", []))
        self.current_mode = config.get("play_mode", "sequential")
        self.current_playing_index = -1

        self.setWindowTitle("MoonPet Music Player")
        self.setMinimumSize(820, 580)
        self.resize(820, 580)
        self._apply_style()
        self._build_ui()
        self._load_songs_from_config()

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#bg-container {
                background-color: transparent;
            }
            QLabel { color: #c8c8e0; }
            QSlider::groove:horizontal {
                height: 6px; background: rgba(58, 58, 92, 0.7); border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #6c5ce7; width: 14px; height: 14px;
                margin: -4px 0; border-radius: 7px;
            }
            QSlider::sub-page:horizontal { background: #6c5ce7; border-radius: 3px; }
            QListWidget {
                background-color: rgba(22, 22, 43, 0.75);
                border: 1px solid rgba(58, 58, 92, 0.6);
                border-radius: 6px; padding: 4px; font-size: 13px; outline: none;
                color: #f0f0f0; font-weight: bold;
            }
            QListWidget::item { padding: 8px 10px; border-radius: 4px; font-weight: bold; }
            QListWidget::item:selected { background-color: rgba(108, 92, 231, 0.7); color: white; }
            QListWidget::item:hover { background-color: rgba(45, 45, 80, 0.6); }
            QComboBox {
                background-color: rgba(45, 45, 80, 0.65); color: #e0e0e0;
                border: 1px solid rgba(108, 92, 231, 0.5); border-radius: 6px;
                padding: 5px 10px; font-size: 13px; min-width: 100px;
            }
            QComboBox::drop-down { border: none; width: 24px; }
            QComboBox QAbstractItemView {
                background-color: #2d2d50; color: #e0e0e0;
                selection-background-color: #6c5ce7; border: 1px solid #4a4a6a;
            }
            QTabWidget::pane {
                border: 1px solid rgba(58, 58, 92, 0.6); border-radius: 6px;
                background-color: rgba(22, 22, 43, 0.65);
            }
            QTabBar::tab {
                background-color: rgba(45, 45, 80, 0.6); color: #a0a0c0;
                border: 1px solid rgba(58, 58, 92, 0.6); padding: 8px 20px;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: rgba(22, 22, 43, 0.65); color: #e0e0e0;
                border-bottom-color: rgba(22, 22, 43, 0.65);
            }
            QTabBar::tab:hover { background-color: rgba(61, 61, 106, 0.6); }
            QFrame#now-playing-bar {
                background-color: rgba(18, 18, 42, 0.8);
                border-top: 1px solid rgba(108, 92, 231, 0.3);
            }
            QMenu {
                background-color: rgba(43, 43, 61, 0.95); color: #e0e0e0;
                border: 1px solid #555; border-radius: 6px;
                padding: 4px; font-size: 13px;
            }
            QMenu::item:selected { background-color: #6c5ce7; border-radius: 4px; }
        """)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._bg_label = QLabel(self)
        self._bg_label.setScaledContents(True)
        self._bg_label.lower()
        self._bg_pixmap = None
        if os.path.exists(BG_IMAGE):
            self._bg_pixmap = QPixmap(BG_IMAGE)

        content = QWidget()
        content.setObjectName("bg-container")
        content.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(20, 14, 20, 8)
        title = QLabel("MoonPet Player")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #d4c8ff; border: none; background: transparent;")
        header.addWidget(title)
        header.addStretch()
        btn_add_folder = QPushButton("+ 扫描文件夹")
        btn_add_folder.setStyleSheet(BTN_STYLE)
        btn_add_folder.clicked.connect(self._add_folder)
        header.addWidget(btn_add_folder)

        btn_add_file = QPushButton("+ 添加单曲")
        btn_add_file.setStyleSheet(BTN_STYLE)
        btn_add_file.clicked.connect(self._add_single_file)
        header.addWidget(btn_add_file)
        content_layout.addLayout(header)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: rgba(108, 92, 231, 0.3); max-height: 1px;")
        content_layout.addWidget(sep)

        body = QHBoxLayout()
        body.setContentsMargins(12, 8, 12, 0)
        body.setSpacing(10)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(6)

        left_header = QHBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.list_all = QListWidget()
        self.list_all.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_all.itemDoubleClicked.connect(self._on_double_click_all)
        self.list_all.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_all.customContextMenuRequested.connect(lambda pos: self._show_song_menu(pos, "all"))

        self.list_fav = QListWidget()
        self.list_fav.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_fav.itemDoubleClicked.connect(self._on_double_click_fav)
        self.list_fav.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_fav.customContextMenuRequested.connect(lambda pos: self._show_song_menu(pos, "fav"))

        self.tabs.addTab(self.list_all, "所有音乐")
        self.tabs.addTab(self.list_fav, "我喜欢的")
        left_panel.addWidget(self.tabs)

        btn_bar_all = QHBoxLayout()
        btn_bar_all.setSpacing(6)
        btn_select_all = QPushButton("全选")
        btn_select_all.setStyleSheet(BTN_SMALL_STYLE)
        btn_select_all.clicked.connect(self._select_all_songs)
        btn_bar_all.addWidget(btn_select_all)

        btn_add_selected = QPushButton("添加选中到播放列表")
        btn_add_selected.setStyleSheet(BTN_SMALL_STYLE)
        btn_add_selected.clicked.connect(self._add_selected_to_playlist)
        btn_bar_all.addWidget(btn_add_selected)

        btn_fav_selected = QPushButton("添加选中到喜欢")
        btn_fav_selected.setStyleSheet(BTN_SMALL_STYLE)
        btn_fav_selected.clicked.connect(self._add_selected_to_favorites)
        btn_bar_all.addWidget(btn_fav_selected)

        btn_bar_all.addStretch()

        self.lbl_count = QLabel("0 首")
        self.lbl_count.setStyleSheet("font-size: 12px; color: #9090b0; border: none; background: transparent;")
        btn_bar_all.addWidget(self.lbl_count)
        left_panel.addLayout(btn_bar_all)

        body.addLayout(left_panel, 3)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(6)
        right_header_row = QHBoxLayout()
        right_label = QLabel("播放列表")
        right_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #d4c8ff; border: none; background: transparent;")
        right_header_row.addWidget(right_label)
        right_header_row.addStretch()

        btn_clear = QPushButton("清空列表")
        btn_clear.setStyleSheet(BTN_SMALL_STYLE)
        btn_clear.clicked.connect(self._clear_playlist)
        right_header_row.addWidget(btn_clear)

        btn_remove = QPushButton("移除选中")
        btn_remove.setStyleSheet(BTN_SMALL_STYLE)
        btn_remove.clicked.connect(self._remove_selected)
        right_header_row.addWidget(btn_remove)

        right_panel.addLayout(right_header_row)

        self.playlist_widget = QListWidget()
        self.playlist_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.playlist_widget.itemDoubleClicked.connect(self._on_double_click_playlist)
        self.playlist_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.playlist_widget.customContextMenuRequested.connect(self._show_playlist_menu)
        right_panel.addWidget(self.playlist_widget)

        self.lbl_pl_count = QLabel("0 首")
        self.lbl_pl_count.setStyleSheet("font-size: 12px; color: #9090b0; border: none; background: transparent;")
        right_panel.addWidget(self.lbl_pl_count)

        body.addLayout(right_panel, 2)
        content_layout.addLayout(body, 1)

        bar = QFrame()
        bar.setObjectName("now-playing-bar")
        bar_layout = QVBoxLayout(bar)
        bar_layout.setContentsMargins(16, 8, 16, 10)
        bar_layout.setSpacing(6)

        info_row = QHBoxLayout()
        self.lbl_now = QLabel("未播放")
        self.lbl_now.setStyleSheet("font-size: 14px; font-weight: bold; color: #d4c8ff; border: none; background: transparent;")
        info_row.addWidget(self.lbl_now)
        info_row.addStretch()

        self.lbl_song_detail = QLabel("")
        self.lbl_song_detail.setStyleSheet("font-size: 11px; color: #8888aa; border: none; background: transparent;")
        info_row.addWidget(self.lbl_song_detail)

        self.btn_fav_current = QPushButton("♡")
        self.btn_fav_current.setObjectName("fav-btn")
        self.btn_fav_current.setStyleSheet(BTN_FAV_STYLE)
        self.btn_fav_current.setFixedSize(32, 32)
        self.btn_fav_current.clicked.connect(self._toggle_fav_current)
        info_row.addWidget(self.btn_fav_current)
        bar_layout.addLayout(info_row)

        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)

        btn_prev = QPushButton("⏮")
        btn_prev.setStyleSheet(BTN_CTRL_STYLE)
        btn_prev.setFixedSize(36, 36)
        btn_prev.clicked.connect(self.prev_signal.emit)
        ctrl_row.addWidget(btn_prev)

        self.btn_play = QPushButton("▶")
        self.btn_play.setStyleSheet(BTN_PLAY_STYLE)
        self.btn_play.clicked.connect(self._toggle_play)
        ctrl_row.addWidget(self.btn_play)

        btn_next = QPushButton("⏭")
        btn_next.setStyleSheet(BTN_CTRL_STYLE)
        btn_next.setFixedSize(36, 36)
        btn_next.clicked.connect(self.next_signal.emit)
        ctrl_row.addWidget(btn_next)

        ctrl_row.addSpacing(12)

        self.slider_vol = QSlider(Qt.Horizontal)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(int(self.config.get("volume", 50)))
        self.slider_vol.setFixedWidth(120)
        self.slider_vol.valueChanged.connect(self._on_volume)
        ctrl_row.addWidget(self.slider_vol)

        self.lbl_vol = QLabel(f"{self.slider_vol.value()}%")
        self.lbl_vol.setFixedWidth(36)
        self.lbl_vol.setStyleSheet("font-size: 12px; border: none; background: transparent; color: #b0b0d0;")
        ctrl_row.addWidget(self.lbl_vol)

        ctrl_row.addSpacing(12)

        self.combo_mode = QComboBox()
        for mode_id, mode_name in self.MODES:
            self.combo_mode.addItem(mode_name, mode_id)
        idx = next((i for i, (m, _) in enumerate(self.MODES) if m == self.current_mode), 0)
        self.combo_mode.setCurrentIndex(idx)
        self.combo_mode.currentIndexChanged.connect(self._on_mode_change)
        ctrl_row.addWidget(self.combo_mode)

        ctrl_row.addStretch()
        bar_layout.addLayout(ctrl_row)

        content_layout.addWidget(bar)
        root.addWidget(content)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._bg_pixmap and not self._bg_pixmap.isNull():
            self._bg_label.setGeometry(0, 0, self.width(), self.height())
            scaled = self._bg_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            self._bg_label.setPixmap(scaled)

    def _load_songs_from_config(self):
        folders = self.config.get("scan_folders", [])
        if folders:
            self.all_songs = scan_folders(folders)
            self._refresh_all_list()
            self._refresh_fav_list()

        saved_paths = self.config.get("playlist_paths", [])
        if saved_paths:
            path_to_song = {s["path"]: s for s in self.all_songs}
            restored = []
            for p in saved_paths:
                if p in path_to_song:
                    restored.append(path_to_song[p])
            if restored:
                self.songs = restored
                self._refresh_playlist_widget()

    def _save_playlist_to_config(self):
        self.config["playlist_paths"] = [s["path"] for s in self.songs]
        save_config(self.config)

    def _save_fav_to_config(self):
        self.config["favorite_songs"] = list(self.favorites)
        save_config(self.config)

    def _refresh_all_list(self):
        self.list_all.clear()
        for song in self.all_songs:
            item = QListWidgetItem(f"  {song['name']}")
            item.setData(Qt.UserRole, song)
            self.list_all.addItem(item)
        self.lbl_count.setText(f"{self.list_all.count()} 首")

    def _refresh_fav_list(self):
        self.list_fav.clear()
        for song in self.all_songs:
            if song["path"] in self.favorites:
                item = QListWidgetItem(f"  {song['name']}")
                item.setData(Qt.UserRole, song)
                self.list_fav.addItem(item)

    def _refresh_playlist_widget(self):
        self.playlist_widget.clear()
        for i, song in enumerate(self.songs):
            prefix = "♪ " if i != self.current_playing_index else "▶ "
            item = QListWidgetItem(f"{prefix}{song['name']}")
            item.setData(Qt.UserRole, i)
            self.playlist_widget.addItem(item)
        if 0 <= self.current_playing_index < self.playlist_widget.count():
            self.playlist_widget.setCurrentRow(self.current_playing_index)
        self.lbl_pl_count.setText(f"{len(self.songs)} 首")

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择音乐文件夹")
        if folder:
            if folder not in self.config["scan_folders"]:
                self.config["scan_folders"].append(folder)
            new_songs = scan_folders([folder])
            existing = {s["path"] for s in self.all_songs}
            for s in new_songs:
                if s["path"] not in existing:
                    self.all_songs.append(s)
                    existing.add(s["path"])
            self._refresh_all_list()
            self._refresh_fav_list()
            save_config(self.config)

    def _add_single_file(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择音频文件", "",
            "音频文件 (*.mp3 *.wav *.ogg *.flac *.aac *.wma *.m4a);;所有文件 (*)"
        )
        if not files:
            return
        existing = {s["path"] for s in self.all_songs}
        added = 0
        for f in files:
            if f not in existing:
                name = os.path.splitext(os.path.basename(f))[0]
                self.all_songs.append({"name": name, "path": f})
                existing.add(f)
                added += 1
        if added:
            self._refresh_all_list()
            self._refresh_fav_list()
            save_config(self.config)

    def _on_double_click_all(self, item):
        song = item.data(Qt.UserRole)
        self._add_to_playlist_and_play(song)

    def _on_double_click_fav(self, item):
        song = item.data(Qt.UserRole)
        self._add_to_playlist_and_play(song)

    def _on_double_click_playlist(self, item):
        idx = item.data(Qt.UserRole)
        self.play_index.emit(idx)

    def _add_to_playlist_and_play(self, song):
        self.songs.append(song)
        self._save_playlist_to_config()
        idx = len(self.songs) - 1
        self.playlist_changed.emit(self.songs)
        self._refresh_playlist_widget()
        self.play_index.emit(idx)

    def _select_all_songs(self):
        self.list_all.selectAll()

    def _add_selected_to_playlist(self):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            items = self.list_all.selectedItems()
        else:
            items = self.list_fav.selectedItems()
        existing_paths = {s["path"] for s in self.songs}
        added = 0
        for item in items:
            song = item.data(Qt.UserRole)
            if song and song["path"] not in existing_paths:
                self.songs.append(song)
                existing_paths.add(song["path"])
                added += 1
        if added:
            self._save_playlist_to_config()
            self.playlist_changed.emit(self.songs)
            self._refresh_playlist_widget()

    def _add_selected_to_favorites(self):
        current_tab = self.tabs.currentIndex()
        if current_tab == 0:
            items = self.list_all.selectedItems()
        else:
            items = self.list_fav.selectedItems()
        for item in items:
            song = item.data(Qt.UserRole)
            if song:
                self.favorites.add(song["path"])
        self._save_fav_to_config()
        self._refresh_fav_list()
        self.favorites_changed.emit(list(self.favorites))

    def _show_song_menu(self, pos, source):
        item = self.list_all.itemAt(pos) if source == "all" else self.list_fav.itemAt(pos)
        if not item:
            return
        song = item.data(Qt.UserRole)

        menu = QMenu(self)
        action_play = menu.addAction("▶  播放")
        action_add = menu.addAction("➕  添加到播放列表")
        menu.addSeparator()
        action_fav = menu.addAction("💔  取消喜欢" if song["path"] in self.favorites else "❤️  添加到喜欢")

        action = menu.exec_(QCursor.pos())
        if action is None:
            return
        if action == action_play:
            self._add_to_playlist_and_play(song)
        elif action == action_add:
            if song not in self.songs:
                self.songs.append(song)
                self._save_playlist_to_config()
                self.playlist_changed.emit(self.songs)
                self._refresh_playlist_widget()
        elif action == action_fav:
            if song["path"] in self.favorites:
                self.favorites.discard(song["path"])
            else:
                self.favorites.add(song["path"])
            self._save_fav_to_config()
            self._refresh_fav_list()
            self.favorites_changed.emit(list(self.favorites))

    def _remove_selected(self):
        row = self.playlist_widget.currentRow()
        if row < 0 or row >= len(self.songs):
            return
        self.songs.pop(row)
        if self.current_playing_index == row:
            self.current_playing_index = -1
        elif self.current_playing_index > row:
            self.current_playing_index -= 1
        self._save_playlist_to_config()
        self.playlist_changed.emit(self.songs)
        self._refresh_playlist_widget()

    def _show_playlist_menu(self, pos):
        item = self.playlist_widget.itemAt(pos)
        if not item:
            return
        idx = item.data(Qt.UserRole)
        menu = QMenu(self)
        action_play = menu.addAction("▶  播放此曲")
        action_remove = menu.addAction("❌  从列表移除")
        action = menu.exec_(QCursor.pos())
        if action is None:
            return
        if action == action_play:
            self.play_index.emit(idx)
        elif action == action_remove:
            self.playlist_widget.setCurrentRow(idx)
            self._remove_selected()

    def _clear_playlist(self):
        self.songs.clear()
        self.current_playing_index = -1
        self._save_playlist_to_config()
        self.playlist_changed.emit(self.songs)
        self._refresh_playlist_widget()
        self.lbl_now.setText("未播放")
        self.lbl_song_detail.setText("")
        self.btn_fav_current.setText("♡")

    def _toggle_play(self):
        if self.btn_play.text() == "▶":
            self.resume_signal.emit()
        else:
            self.pause_signal.emit()

    def set_playing_state(self, playing, paused=False, song_name=""):
        if paused:
            self.btn_play.setText("▶")
            self.lbl_now.setText(f"⏸ {song_name}")
        elif playing:
            self.btn_play.setText("⏸")
            self.lbl_now.setText(f"♪ {song_name}")
        else:
            self.btn_play.setText("▶")
            self.lbl_now.setText("未播放" if not song_name else song_name)
        self._update_fav_button()

    def set_current_index(self, idx):
        self.current_playing_index = idx
        self._refresh_playlist_widget()
        self._update_fav_button()
        if 0 <= idx < len(self.songs):
            self.lbl_song_detail.setText(self.songs[idx]["path"])
        else:
            self.lbl_song_detail.setText("")

    def _update_fav_button(self):
        if 0 <= self.current_playing_index < len(self.songs):
            path = self.songs[self.current_playing_index]["path"]
            self.btn_fav_current.setText("❤️" if path in self.favorites else "♡")
        else:
            self.btn_fav_current.setText("♡")

    def _toggle_fav_current(self):
        if 0 <= self.current_playing_index < len(self.songs):
            path = self.songs[self.current_playing_index]["path"]
            if path in self.favorites:
                self.favorites.discard(path)
            else:
                self.favorites.add(path)
            self._save_fav_to_config()
            self._refresh_fav_list()
            self._update_fav_button()
            self.favorites_changed.emit(list(self.favorites))

    def _on_volume(self, val):
        self.lbl_vol.setText(f"{val}%")
        self.volume_changed.emit(val / 100.0)

    def _on_mode_change(self, index):
        mode_id = self.combo_mode.itemData(index)
        self.current_mode = mode_id
        self.mode_changed.emit(mode_id)

    def force_refresh(self):
        self._load_songs_from_config()
        self._refresh_fav_list()
