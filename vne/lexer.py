import io
import os
import pygame
from vne.xor_data import xor_data
from vne.config import key
import numpy as np

class ScriptLexer:
 
    def __init__(self, game_path, engine):
        self.game_path = game_path
        self.engine = engine
        self.commands = []
        self.original_commands = []
        self.current = 0
        self.load_scripts()
    
    def load_scripts(self):
        """
        The function `load_scripts` loads and parses a script file after decoding it using XOR
        encryption.
        """
        base_name = "startup"   
        try:
            compiled_path = base_name + ".kagc"
            file_bytes = self.engine.resource_manager.get_bytes(compiled_path)
            plain_bytes = xor_data(file_bytes, key)
            content = plain_bytes.decode("utf-8", errors="replace")
            self.commands = self.parse_script(content)
            self.original_commands = list(self.commands)
        except Exception as e:
            print(f"[Lexer] Compiled version of 'startup' not found: {e}")
            self.commands = []
            self.original_commands = []
            
    def parse_script(self, content):
        """
        The function `parse_script` takes in a string of content, splits it into lines, removes leading
        and trailing whitespace, filters out empty lines and lines starting with `#`, and returns a list
        of commands.
        
        :param content: The `parse_script` method takes a string `content` as input and splits it into
        lines. It then iterates over each line, strips any leading or trailing whitespace, and checks if
        the line is not empty and does not start with a `#` (comment). If these conditions are met
        :return: The `parse_script` method returns a list of commands extracted from the input `content`
        after removing empty lines and lines starting with `#`.
        """
        lines = content.splitlines()
        commands = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith("#"):
                commands.append(stripped_line)
        return commands

    def get_next_command(self):
        """
        The function `get_next_command` returns the next command in a list of commands if available.
        :return: The `get_next_command` method returns the next command in the list of commands if there
        are more commands available. If there are no more commands left to return, it returns `None`.
        """
        if self.current < len(self.commands):
            cmd = self.commands[self.current]
            self.current += 1
            print(f"[get-next-command] {cmd} | current = {self.current}")
            return cmd
        return None
    
    def load_image(self, relative_path):
        """
        The function `load_image` loads an image from a relative path using Pygame, handling exceptions
        and ensuring full opacity.
        
        :param relative_path: The `load_image` method you provided seems to be a part of a class that
        loads images for a game engine. The `relative_path` parameter is used to specify the path to the
        image file relative to the game's data directory
        :return: The `load_image` method returns the loaded image after processing it with full opacity.
        """
        try:
            image_bytes = self.engine.resource_manager.get_bytes(relative_path)
            image_stream = io.BytesIO(image_bytes)
            image = pygame.image.load(image_stream).convert_alpha()
 
            return image
        except Exception as e:
            full_path = os.path.join(self.engine.game_path, "data", relative_path)
            if os.path.exists(full_path):
                try:
                    image = pygame.image.load(full_path)
 
                    return image
                except Exception as e2:
                    raise Exception(f"Error loading image from '{full_path}': {e2}")
            else:
                raise Exception(f"Error loading image at '{relative_path}': {e}")
    
    def force_full_opacity(self, surface):
        """
        This Python function converts a surface to use alpha transparency and sets all alpha values to
        full opacity.
        
        :param surface: The `surface` parameter in the `force_full_opacity` function is a surface object
        representing an image or a portion of the screen in Pygame. The function converts the surface to
        use alpha transparency, sets all alpha values to 255 (full opacity), and then returns the
        modified surface
        :return: the surface with full opacity, where the alpha values of all pixels in the surface have
        been set to 255 (fully opaque).
        """
        surface = surface.convert_alpha()
        alpha_array = pygame.surfarray.pixels_alpha(surface)
        alpha_array[:] = 255  
        del alpha_array  
    
