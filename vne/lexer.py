# engine/vne/lexer.py
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
            from vne.xor_data import xor_data
            from vne.config import key
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
