import pygame
import io
import os

class Audio(object):
    instances = []
    def __init__(self, filename, type_file="bgm", engine=None):
        super(Audio, self).__init__()
        assert isinstance(filename, str)
        self.bytes_io = None
        self.filename = filename
        self.type_file = type_file
        self.engine = engine
        self.sound = self.load_audio()
        Audio.instances.append(self)
    
    def load_audio(self):
        rel_path = os.path.join("audio", self.type_file, self.filename + ".mp3")
        try:
            audio_bytes = self.engine.resource_manager.get_bytes(rel_path)  
            self.bytes_io = io.BytesIO(audio_bytes)
            self.bytes_io.seek(0)
            return pygame.mixer.Sound(self.bytes_io)
        except Exception as e:
                raise Exception(f"[Audio] Error loading audio from '{rel_path}': {e}")
    
    def get_channel(self):
        if self.type_file == "bgm":
            return pygame.mixer.Channel(0)
        
        # Search for a free channel, or steal one if none are free (except channel 0)
        channel = pygame.mixer.find_channel(True)
        return channel if (channel and channel.get_id() != 0) else pygame.mixer.Channel(1)

    def play(self, loop=0, fade_ms=500):
        channel = self.get_channel()
        
        if self.type_file == "bgm" and channel.get_busy():
            channel.fadeout(fade_ms)
        
        channel.play(self.sound, loops=loop, fade_ms=fade_ms)
        
        if self.engine and hasattr(self.engine, 'config'):
            key = "bgm_volume" if self.type_file == "bgm" else "sfx_volume"
            vol = self.engine.config.get(key, 1.0)
            channel.set_volume(vol)