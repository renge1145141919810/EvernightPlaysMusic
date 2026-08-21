import sys
import os
import atexit

if getattr(sys, 'frozen', False):
    _RESOURCE_DIR = sys._MEIPASS
else:
    _RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QPixmap

from config_manager import load_config, save_config
from music_player import MusicPlayer
from pet_widget import DesktopPet
from player_window import MusicPlayerWindow


class MoonPetApp(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.config = load_config()
        atexit.register(save_config, self.config)
        self.player = MusicPlayer()
        self.player.set_volume(self.config.get("volume", 50) / 100.0)
        self.player.set_play_mode(self.config.get("play_mode", "sequential"))

        gif_path = os.path.join(_RESOURCE_DIR, "moon.gif")
        self._gif_path = gif_path

        screen = self.app.primaryScreen().geometry()
        pet_size = self.config.get("pet_size", 180)
        margin = 30

        x = self.config.get("pet_x", -1)
        y = self.config.get("pet_y", -1)

        if x < 0 or y < 0 or x > screen.width() - 50 or y > screen.height() - 50:
            x = screen.width() - pet_size - margin
            y = screen.height() - pet_size - margin - 40

        self.pet = DesktopPet(gif_path, x=x, y=y, size=pet_size)

        self.player_window = MusicPlayerWindow(self.config)
        self.player_window.hide()

        self._setup_tray()
        self._connect_signals()
        self._start_tick()

        if self.config.get("auto_play", True) and self.player_window.songs:
            idx = self.config.get("last_play_index", 0)
            idx = max(0, min(idx, len(self.player_window.songs) - 1))
            self.player.set_playlist(self.player_window.songs)
            self.player.play(idx)
            self._sync_ui()

        print("MoonPet started! Look for the moon character on your desktop.")
        print("Right-click it for menu, or use the tray icon.")

    def _setup_tray(self):
        tray_icon = QIcon(self._gif_path)
        self.tray = QSystemTrayIcon(tray_icon, self.app)
        self.tray.setToolTip("MoonPet Player")

        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b3d;
                color: #e0e0e0;
                border: 1px solid #555;
                padding: 4px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #6c5ce7;
            }
        """)

        action_show_pet = tray_menu.addAction("Show Pet")
        action_show_pet.triggered.connect(self._bring_pet_front)

        action_open = tray_menu.addAction("Open Player")
        action_open.triggered.connect(self._show_player)

        tray_menu.addSeparator()

        action_play = tray_menu.addAction("Play / Pause")
        action_play.triggered.connect(self._toggle_play)

        action_next = tray_menu.addAction("Next Track")
        action_next.triggered.connect(self._next)

        action_prev = tray_menu.addAction("Previous Track")
        action_prev.triggered.connect(self._prev)

        tray_menu.addSeparator()

        action_quit = tray_menu.addAction("Quit")
        action_quit.triggered.connect(self._quit)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_player()

    def _bring_pet_front(self):
        self.pet.show()
        self.pet.raise_()
        self.pet.activateWindow()

    def _connect_signals(self):
        self.pet.open_player.connect(self._show_player)
        self.pet.toggle_play.connect(self._toggle_play)
        self.pet.next_track.connect(self._next)
        self.pet.prev_track.connect(self._prev)
        self.pet.quit_app.connect(self._quit)

        self.player_window.play_index.connect(self._play_at)
        self.player_window.pause_signal.connect(self._pause)
        self.player_window.resume_signal.connect(self._resume)
        self.player_window.next_signal.connect(self._next)
        self.player_window.prev_signal.connect(self._prev)
        self.player_window.volume_changed.connect(self._set_volume)
        self.player_window.mode_changed.connect(self._set_mode)
        self.player_window.favorites_changed.connect(self._save_favorites)

    def _start_tick(self):
        self.tick_timer = QTimer()
        self.tick_timer.timeout.connect(self._tick)
        self.tick_timer.start(500)

    def _tick(self):
        self.player.tick()
        is_paused = self.player.is_paused()
        song = self.player.get_current_song()
        name = song["name"] if song else ""

        self.player_window.set_playing_state(
            self.player.is_playing(), is_paused, name
        )

        if self.player.is_finished():
            self._on_song_finished()

    def _on_song_finished(self):
        mode = self.player.play_mode
        if mode == "single":
            self.player.play()
        elif mode == "loop":
            self.player.next_song()
        elif mode == "random":
            self.player.next_song()
        else:
            idx = self.player.current_index
            if idx < len(self.player.playlist) - 1:
                self.player.next_song()
            else:
                self.player.stop()
        self._sync_ui()

    def _sync_ui(self):
        song = self.player.get_current_song()
        name = song["name"] if song else ""
        self.player_window.set_playing_state(
            self.player.is_playing(), self.player.is_paused(), name
        )
        self.player_window.set_current_index(self.player.current_index)
        if self.player.current_index >= 0:
            self.config["last_play_index"] = self.player.current_index

    def _show_player(self):
        self.player_window.show()
        self.player_window.raise_()
        self.player_window.activateWindow()

    def _toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
        elif self.player.is_paused():
            self.player.resume()
        elif self.player.playlist:
            self.player.play()
        else:
            if self.player_window.songs:
                self.player.set_playlist(self.player_window.songs)
                self.player.play()
        self._sync_ui()

    def _pause(self):
        self.player.pause()
        self._sync_ui()

    def _resume(self):
        if self.player.is_paused():
            self.player.resume()
        elif self.player.playlist:
            self.player.play()
        self._sync_ui()

    def _next(self):
        if self.player_window.songs and not self.player.playlist:
            self.player.set_playlist(self.player_window.songs)
        self.player.next_song()
        self._sync_ui()

    def _prev(self):
        if self.player_window.songs and not self.player.playlist:
            self.player.set_playlist(self.player_window.songs)
        self.player.prev_song()
        self._sync_ui()

    def _play_at(self, index):
        if self.player_window.songs:
            self.player.set_playlist(self.player_window.songs)
            self.player.play(index)
            self._sync_ui()

    def _set_volume(self, vol):
        self.player.set_volume(vol)
        self.config["volume"] = int(vol * 100)

    def _set_mode(self, mode):
        self.player.set_play_mode(mode)
        self.config["play_mode"] = mode

    def _save_favorites(self, favs):
        self.config["favorite_songs"] = favs
        save_config(self.config)

    def _quit(self):
        self.player_window._save_playlist_to_config()
        self.config["pet_x"] = self.pet.x()
        self.config["pet_y"] = self.pet.y()
        save_config(self.config)
        self.player.destroy()
        self.app.quit()

    def run(self):
        ret = self.app.exec_()
        self.player_window._save_playlist_to_config()
        self.config["pet_x"] = self.pet.x()
        self.config["pet_y"] = self.pet.y()
        save_config(self.config)
        self.player.destroy()
        return ret


if __name__ == "__main__":
    app = MoonPetApp()
    sys.exit(app.run())
