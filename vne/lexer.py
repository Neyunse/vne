import io
import os
import pygame
from vne.aes import AES
from vne.aes import SCRIPT_AAD, SaveCorruptError
from vne.config import key, aes_extension, init_file

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
        Carga y descifra el script compilado usando AES-GCM.
        """
        base_name = init_file
        try:
            compiled_path = base_name + aes_extension
            # 1. Leer datos cifrados desde resource_manager
            file_bytes = self.engine.resource_manager.get_bytes(compiled_path)

            # 2. Si guardaste en hex o base64, decodificar primero
            #    Aquí asumo binario puro; si es texto, agrega decode según corresponda
            #    Ej: file_bytes = file_bytes.decode("utf-8") si el archivo es hex/base64
            #    y luego pasarlo a aes.decrypt(..., encoded='hex')

            # 3. Desencriptar con AES-GCM y AAD
            try:
                plain_bytes = AES(key).decrypt(file_bytes, aad=SCRIPT_AAD)  # encoded='hex' si corresponde
            except SaveCorruptError:
                raise Exception(f"[Lexer] Script corrupto o clave inválida: {compiled_path}")

            # 4. Convertir a texto y parsear
            content = plain_bytes.decode("utf-8", errors="replace")
            self.commands = self.parse_script(content)
            self.original_commands = list(self.commands)

        except Exception as e:
            self.commands = []
            self.original_commands = []
            raise Exception(f"[Lexer] Compiled version of '{init_file}' not found: {e}")
            
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
            if cmd.startswith("@"):
                self.engine.Log(f"[get-next-command] {cmd}")
            return cmd
        return None
    
    def load_image(self, relative_path):
        """
        Loads an image. If the path is not found directly, it tries to search in
        common directories (images/bg, images/sprites) and tries common extensions.
        """
        search_paths = [
            relative_path,
            os.path.join("images", "bg", relative_path),
            os.path.join("images", "sprites", relative_path)
        ]
        
        # Add variations with common extensions if no extension is present
        exts = [".png", ".jpg", ".jpeg", ".webp"]
        final_to_try = []
        for p in search_paths:
            final_to_try.append(p)
            # If path doesn't have an extension, add common ones
            if not os.path.splitext(p)[1]:
                for ext in exts:
                    final_to_try.append(p + ext)

        last_err = None
        for path in final_to_try:
            try:
                image_bytes = self.engine.resource_manager.get_bytes(path)
                image_stream = io.BytesIO(image_bytes)
                return pygame.image.load(image_stream).convert_alpha()
            except Exception as e:
                last_err = e
                continue
        
        raise Exception(f"Error loading image at '{relative_path}': {last_err}")
    
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
    
