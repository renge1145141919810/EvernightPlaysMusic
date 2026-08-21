import random
import pygame


class MusicPlayer:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        self.playlist = []
        self.current_index = -1
        self.volume = 0.5
        self.play_mode = "sequential"
        self._playing = False
        self._paused = False
        self._on_finish = None
        self._repeat_one = False

    def set_on_finish(self, callback):
        self._on_finish = callback

    def set_playlist(self, songs):
        self.playlist = list(songs)
        self.current_index = 0 if self.playlist else -1

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        pygame.mixer.music.set_volume(self.volume)

    def get_volume(self):
        return self.volume

    def set_play_mode(self, mode):
        self.play_mode = mode

    def get_current_song(self):
        if 0 <= self.current_index < len(self.playlist):
            return self.playlist[self.current_index]
        return None

    def play(self, index=None):
        if not self.playlist:
            return False
        if index is not None and 0 <= index < len(self.playlist):
            self.current_index = index
        if self.current_index < 0 or self.current_index >= len(self.playlist):
            self.current_index = 0
        song = self.playlist[self.current_index]
        try:
            pygame.mixer.music.load(song["path"])
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self._playing = True
            self._paused = False
            return True
        except Exception:
            return False

    def pause(self):
        if self._playing and not self._paused:
            pygame.mixer.music.pause()
            self._paused = True

    def resume(self):
        if self._playing and self._paused:
            pygame.mixer.music.unpause()
            self._paused = False

    def stop(self):
        pygame.mixer.music.stop()
        self._playing = False
        self._paused = False

    def next_song(self):
        if not self.playlist:
            return False
        if self.play_mode == "random":
            if len(self.playlist) > 1:
                new_idx = self.current_index
                while new_idx == self.current_index:
                    new_idx = random.randint(0, len(self.playlist) - 1)
                self.current_index = new_idx
            else:
                self.current_index = 0
        elif self.play_mode == "single":
            pass
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        return self.play()

    def prev_song(self):
        if not self.playlist:
            return False
        if self.play_mode == "random":
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        return self.play()

    def is_playing(self):
        return self._playing and not self._paused

    def is_paused(self):
        return self._paused

    def is_finished(self):
        if not self._playing:
            return False
        return not pygame.mixer.music.get_busy() and not self._paused

    def tick(self):
        if self._playing and not self._paused:
            if not pygame.mixer.music.get_busy():
                if self._on_finish:
                    self._on_finish()

    def get_position_ms(self):
        return pygame.mixer.music.get_pos()

    def destroy(self):
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        try:
            pygame.mixer.quit()
        except pygame.error:
            pass
