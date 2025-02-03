# engine/vne/lexer.py

class ScriptLexer:
    """
    Lee y parsea el script del juego.
    """
    def __init__(self, game_path):
        self.game_path = game_path
        self.commands = []
        self.current = 0
        self.load_scripts()

    def load_scripts(self):
        # Se asume que el script de inicio está en <game_path>/data/startup.kag
        script_path = f"{self.game_path}/data/startup.kag"
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.commands = self.parse_script(content)
        except Exception as e:
            print("Error al cargar el script:", e)

    def parse_script(self, content):
        lines = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)
        return lines

    def get_next_command(self):
        if self.current < len(self.commands):
            cmd = self.commands[self.current]
            self.current += 1
            return cmd
        return None
