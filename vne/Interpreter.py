import os
import re

class Interpreter:
    """
    Handles the interpretation of commands from the Lexer.
    """

    def __init__(self, lexer, renderer, config):
        self.lexer = lexer
        self.renderer = renderer
        self.config = config
        self.characters = {}  # Nombres de personajes
        self.variables = {}   # Variables generales
        self.command_table = {
            "@bg": self.set_background,
            "@show": self.show_sprite,
            "@char": self.define_character,
            "@process_scene": self.process_scene,
            "@Load": self.load_file,
            "@scene": self.define_scene,
            "@var": self.define_variable,  # Manejar variables
            "dialogue": self.show_dialogue,
        }

    def execute_next_command(self):
        """Executes the next command in the script."""
        command = self.lexer.get_current_state()

        if not command:
            print("No more commands to execute.")  # Debugging
            return False

        print(f"Executing command at index {self.lexer.current_line_index}: {command}")  # Debugging

        parsed_command = self.parse_command(command)
        print(f"Parsed command: {parsed_command}")  # Debugging

        if parsed_command["command"] in self.command_table:
            print(f"Executing: {parsed_command['command']}")  # Debugging
            self.command_table[parsed_command["command"]](parsed_command)
            # Avanzar solo si no es diálogo (requiere interacción del jugador)
            if parsed_command["command"] != "dialogue":
                self.lexer.advance()
        else:
            raise ValueError(f"Unknown command: {parsed_command['command']}")

        return True



    def parse_command(self, command_line):
        """Parses a command line into a dictionary with command and arguments."""
        if command_line.startswith('@'):
            match = re.match(r'(@\w+)\((.*?)\)', command_line)
            if match:
                command = match.group(1)
                arguments = match.group(2).strip()
                return {"command": command, "arguments": arguments}
            parts = command_line.split(maxsplit=1)
            command = parts[0]
            arguments = parts[1] if len(parts) > 1 else ""
            return {"command": command, "arguments": arguments}
        return {"command": "dialogue", "arguments": command_line}
    
    def define_variable(self, parsed_command):
        """Defines a variable."""
        if "=" not in parsed_command["arguments"]:
            raise ValueError(f"Invalid variable definition: {parsed_command['arguments']}")

        key, value = parsed_command["arguments"].split("=", 1)
        key = key.strip()
        value = value.strip().strip('"')

        # Procesa valores numéricos o booleanos
        if value.isdigit():
            value = int(value)
        elif value.lower() in ["true", "false"]:
            value = value.lower() == "true"

        self.variables[key] = value
        print(f"Variable defined: {key} -> {value}")  # Debugging


    def define_scene(self, parsed_command):
        """Defines a scene and registers it in the assets."""
        args = parsed_command["arguments"].split("=")
        if len(args) != 2:
            raise ValueError(f"Invalid scene definition: {parsed_command['arguments']}")

        scene_key = args[0].strip()
        scene_file = args[1].strip().strip('"')
        scene_path = os.path.normpath(f"scenes/{scene_file}.kag")
        self.lexer.assets["scenes"][scene_key] = scene_path
        print(f"Scene defined: {scene_key} -> {scene_path}")  # Debugging

    def process_scene(self, parsed_command):
        """Processes and loads a new scene."""
        scene_key = parsed_command["arguments"].strip()
        print(f"Processing scene: {scene_key}")  # Debugging

        scene_path = self.lexer.assets["scenes"].get(scene_key)
        if not scene_path:
            raise ValueError(f"Scene '{scene_key}' not defined in assets.")

        full_scene_path = os.path.normpath(os.path.join(self.config.base_game, "data", scene_path))
        print(f"Loading scene file: {full_scene_path}")  # Debugging
        self.lexer.load(full_scene_path)

    def load_file(self, parsed_command):
        """Handles the @Load command to load additional scripts."""
        file_path = parsed_command["arguments"].strip('"')
        if not file_path:
            raise ValueError("The @Load command requires a valid file path.")

        full_path = os.path.normpath(os.path.join(self.config.base_game, "data", file_path))
        print(f"Attempting to load additional script: {full_path}")  # Debugging
        self.lexer.load_additional(full_path)

    def show_dialogue(self, parsed_command):
        """Displays a line of dialogue with proper variable and character name resolution."""
        dialogue_text = parsed_command["arguments"]

        # Depuración: mostrar el contenido actual de personajes y variables
        print(f"Characters: {self.characters}")  # Debugging
        print(f"Variables: {self.variables}")  # Debugging

        # Verifica si el diálogo pertenece a un personaje
        if ":" in dialogue_text:
            character_key, dialogue = dialogue_text.split(":", 1)
            character_key = character_key.strip()
            dialogue = dialogue.strip()

            # Depuración: mostrar el personaje identificado
            print(f"Character key: {character_key}")  # Debugging

            # Resuelve el alias del personaje o usa la clave si no hay alias
            character_name = self.characters.get(character_key, character_key)

            # Depuración: mostrar el nombre del personaje resuelto
            print(f"Resolved character name: {character_name}")  # Debugging

            # Reemplaza variables en el texto del diálogo
            for key, value in {**self.characters, **self.variables}.items():
                dialogue = dialogue.replace(f"{{{key}}}", str(value))

            # Reconstruye el texto del diálogo con el alias del personaje
            dialogue_text = f"{character_name}: {dialogue}"
        else:
            # Si no hay personaje, reemplaza variables en el diálogo general
            for key, value in {**self.characters, **self.variables}.items():
                dialogue_text = dialogue_text.replace(f"{{{key}}}", str(value))

        # Depuración: mostrar el diálogo final procesado
        print(f"Final dialogue text: {dialogue_text}")  # Debugging

        # Renderiza el cuadro de diálogo
        self.renderer.draw_dialogue_box(dialogue_text)


    def set_background(self, parsed_command):
        """Sets the background."""
        background_key = parsed_command["arguments"].strip()
        background_path = self.lexer.assets["backgrounds"].get(background_key)
        if not background_path:
            raise ValueError(f"Background '{background_key}' not defined in assets.kag")
        print(f"Set background: {background_path}")

    def show_sprite(self, parsed_command):
        """Shows a sprite on the screen."""
        sprite_key = parsed_command["arguments"].strip()
        sprite_path = self.lexer.assets["sprites"].get(sprite_key)
        if not sprite_path:
            raise ValueError(f"Sprite '{sprite_key}' not defined in assets.kag")
        print(f"Show sprite: {sprite_path}")

    def define_character(self, parsed_command):
        """Defines a character."""
        if " as " in parsed_command["arguments"]:
            key, name = parsed_command["arguments"].split(" as ", 1)
            key = key.strip()
            name = name.strip('"').strip()
            self.characters[key] = name
        else:
            key = parsed_command["arguments"].strip()
            self.characters[key] = key  # Usa la clave como nombre por defecto
        print(f"Character defined: {key} -> {self.characters[key]}")  # Debugging




