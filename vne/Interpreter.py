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
        self.characters = {}
        self.command_table = {
            "@bg": self.set_background,
            "@show": self.show_sprite,
            "@char": self.define_character,
            "@process_scene": self.process_scene,
            "@Load": self.load_file,
            "@scene": self.define_scene,
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
        else:
            raise ValueError(f"Unknown command: {parsed_command['command']}")

        self.lexer.advance()
        print(f"Advanced to index {self.lexer.current_line_index}")  # Debugging
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
        """Displays a line of dialogue."""
        dialogue_text = parsed_command["arguments"]
        print(f"Dialogue: {dialogue_text}")  # Debugging

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
            self.characters[key.strip()] = name.strip('"')
        else:
            key = parsed_command["arguments"].strip()
            self.characters[key] = key
        print(f"Character defined: {key} -> {self.characters[key]}")  # Debugging
