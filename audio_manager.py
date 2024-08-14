import pyglet

class AudioManager:
    def __init__(self, window, framerate):
        self.window = window
        self.framerate = framerate
        self.player = pyglet.media.Player()
        
    def open_audio_file(self, audio_file):
        if len(audio_file) > 0:
            self.audio_file = audio_file
            music = pyglet.media.load(self.audio_file, streaming=False)
            self.player.queue(music)
            self.window.set_update_audio_flag(True)
        
    def play(self):
        if self.player.source is None:
            return
        self.player.play()
        
    def pause(self):
        if self.player.source is None:
            return
        self.player.pause()
        
    def reset(self):
        if self.player.source is None:
            return
        self.player.pause()
        self.player.seek(0)
        self.window.set_update_audio_flag(True)
        
    def update(self, frame, update_flag):
        if self.player.source is None:
            return
        
        if update_flag is True:
            frame_time = frame/self.framerate
            self.player.seek(frame_time)