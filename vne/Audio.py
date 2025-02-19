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
                raise Exception(f"[bgm] Error loading background music from '{rel_path}': {e}")
    
    def get_channel(self):

        if self.type_file == "bgm":
            return pygame.mixer.Channel(0)

        return pygame.mixer.Channel(1)

    def play(self, channel_id=0, loop=0, fade_ms=1000):
        """
        The function `play` plays the audio on the specified channel.
        :param channel: The `play` method takes an integer `channel` as input, which specifies the audio channel to play the sound on.
        """
        channel = self.get_channel()
        
        if channel.get_busy():
            channel.fadeout(500)
            pygame.time.delay(700)

        channel.play(self.sound, loops=loop, fade_ms=fade_ms)