import io
import os
import pygame
from vne.xor_data import xor_data
from vne.config import key
class ScriptLexer:
    """
    Lee y parsea el script (por ejemplo, startup.kag), uniendo las líneas que
    están indentadas después de un comando de bloque (aquellos que terminan en ":").
    """
    def __init__(self, game_path, engine):
        self.game_path = game_path
        self.engine = engine
        self.commands = []
        self.current = 0
        self.load_scripts()
    
 
    def load_scripts(self):
        base_name = "startup"  # sin extensión
        try:
            # Se construye la ruta del archivo compilado
            compiled_path = base_name + ".kagc"
            # Se carga el contenido del archivo compilado usando get_bytes()
            file_bytes = self.engine.resource_manager.get_bytes(compiled_path)
            # Se descifra el contenido aplicando XOR con la clave
            
            plain_bytes = xor_data(file_bytes, key)
            content = plain_bytes.decode("utf-8", errors="replace")
            self.commands = self.parse_script(content)
        except Exception as e:
            print(f"[Lexer] No se encontró la versión compilada de 'startup': {e}")
            self.commands = []

            
    def parse_script(self, content):
        lines = content.splitlines()
        commands = []
        current_command = None
        # Iterar sobre cada línea del contenido
        for line in lines:
            # Si la línea está vacía o es un comentario, se ignora
            if not line.strip() or line.strip().startswith("#"):
                continue
            # Si no hay un comando en construcción, se inicia uno nuevo.
            if current_command is None:
                current_command = line.rstrip()
            else:
                # Si el comando actual empieza con "@menu:" y la línea actual (después de quitar espacios)
                # NO comienza con "@", la unimos al comando actual.
                if current_command.lstrip().startswith("@menu:") and not line.lstrip().startswith("@"):
                    current_command += "\n" + line.lstrip()
                else:
                    # Si la línea actual empieza con "@", es un nuevo comando.
                    # Se guarda el comando actual y se inicia uno nuevo.
                    commands.append(current_command)
                    current_command = line.rstrip()
        if current_command is not None:
            commands.append(current_command)
        return commands



    
    def get_next_command(self):
        if self.current < len(self.commands):
            cmd = self.commands[self.current]
            self.current += 1
            return cmd
        return None
    
    def load_image(self, relative_path):
        """
        Intenta cargar una imagen usando el ResourceManager para soportar tanto data.pkg como la carpeta data/.
        
        Parámetros:
        - engine: el motor (que tiene el ResourceManager y game_path).
        - relative_path: ruta relativa dentro de la carpeta de datos, por ejemplo:
                "images/sprites/kuro.png" o "images/bg/school.png"
                
        Devuelve:
        - Una superficie de Pygame con la imagen cargada.
        
        Si falla, intenta cargar directamente desde el sistema de archivos.
        """
        try:
            # Intentar cargar usando el ResourceManager (esto soporta data.pkg)
            image_bytes = self.engine.resource_manager.get_bytes(relative_path)
            image_stream = io.BytesIO(image_bytes)
            image = pygame.image.load(image_stream).convert_alpha()
            return image
        except Exception as e:
            # Fallback: carga directamente desde la carpeta data/
            full_path = os.path.join(self.engine.game_path, "data", relative_path)
            if os.path.exists(full_path):
                try:
                    image = pygame.image.load(full_path).convert_alpha()
                    return image
                except Exception as e2:
                    raise Exception(f"Error al cargar la imagen desde '{full_path}': {e2}")
            else:
                raise Exception(f"Error al cargar la imagen en '{relative_path}': {e}")
