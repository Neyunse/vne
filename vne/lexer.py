import os
from .config import Config
class Lexer:
    """
    Handles the loading and processing of script files.
    Provides commands to the interpreter sequentially.
    """

    def __init__(self, config):
        self.script_lines = []
        self.current_line_index = 0
        self.config = config
        self.assets = {
            "backgrounds": {},
            "sprites": {},
            "scenes": {},
        }

    def load(self, file_path):
        """Loads a script file into memory."""
        full_path = os.path.normpath(os.path.join(self.config.base_game, file_path))
        print(f"Loading script from: {full_path}")  # Debugging
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                self.script_lines = [line.strip() for line in file if line.strip() and not line.startswith('#')]
            self.current_line_index = 0
            print(f"Script loaded with {len(self.script_lines)} lines.")  # Debugging
        except FileNotFoundError:
            raise FileNotFoundError(f"Script file not found: {full_path}")

    def get_current_state(self):
        """Returns the current command or None if at the end of the script."""
        if self.current_line_index < len(self.script_lines):
            return self.script_lines[self.current_line_index]
        return None

    def advance(self):
        """Moves to the next line in the script."""
        if self.current_line_index < len(self.script_lines):
            self.current_line_index += 1

    def load_additional(self, file_path):
        """Loads an additional script and appends it to the current script."""
        full_path = os.path.normpath(file_path)
        print(f"Loading additional script from: {full_path}")  # Debugging

        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                additional_lines = [line.strip() for line in file if line.strip() and not line.startswith('#')]

            insertion_index = self.current_line_index + 1
            self.script_lines = (
                self.script_lines[:insertion_index] +
                additional_lines +
                self.script_lines[insertion_index:]
            )

            print(f"Added {len(additional_lines)} lines at index {insertion_index}")  # Debugging
            print(f"Updated script_lines: {self.script_lines}")  # Debugging
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")