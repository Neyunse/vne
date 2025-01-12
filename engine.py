# Copyright 2024 Neyunse
#
# VNengine is licensed under Creative Commons Attribution-NoDerivatives 4.0 International. 
# To view a copy of this license, visit https://creativecommons.org/licenses/by-nd/4.0/
import os
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from datetime import datetime
from dialogue_box import DialogueBox as TextBox
import platform

version = "0.0.0"
prefix_version = "-alpha.10"
version_name = "N/a"
builded_file_name = "vne"
product_name = "VNEngine"
copyright = "Neyunse"
sdk_icon_name = "sdk_icon"

class VNEngine:
    
    def __init__(self, 
                 script_path: str, 
                 config_path: str = None, 
                  
                 game_folder: str = None,
                 base_folder: str = None
                 ):

        self.pygame_flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        self.screen_size = (1280, 720)
        self.default_screen_size = (1280, 720)
        self.monitor_size = ()
        self.screen = None  
        self.fullscreen = False
        
        self.font = None
        self.clock = None

        self.script_path = script_path
        self.script = []
        self.current_line = 0
        self.variables = {}
        self.characters = {}
        self.images = {}
        self.sprites = {}
        self.labels = []
        self.flags = {}
        self.game_version = "1.0.0"
        self.needs_update = True
        self.show_window = False
        self.scale_factor = 1.0
        self.display_info = None
        self.typing_speed=50
        self.char_index = 0 

        self.game_folder = game_folder
        self.base_folder = base_folder

        self.current_background = None
        self.current_sprites = []
        self.dialogue_queue = []
        self.current_menu = None
        self.running = True
        self.dialogue_box_text_color = (255, 255, 255)

        self.dialog_box_color = (0,0,0, 128)
 
        self.chars_displayed = 0
        self.dialogue_start_time = None
        self.scene_boundaries = {}
         
 
    COMMAND_PREFIX = '@'
    COMMENT_PREFIX = '#'
    DIALOGUE_PREFIX = ':'
    COMMAND_LIST = [
        'var', 
        'char', 
        'background',
        'bg', 
        'sprite', 
        'scene', 
        'show_sprite',
        'remove_sprite',
        'change_scene', 
        'return',  
        'endScene',
        'conditional',
        'setCondtion',
        'renameChar',
        'if',
        'endif',
        'setVar',
        'game_title',
        'game_icon',
        'game_textbox_font_color',
        'game_textbox_background_color',
        'game_version',
        'pass',
        'import'
        #"menu"
    ]
  
    RESERVED_VARIABLES = [
        ('engine.version', f"VNE v{version}{prefix_version}"),
        ('engine.version_only', f"v{version}{prefix_version}"),
        ('engine.version_name', f"{version_name}"),
        ('engine.current_plataform', f"{platform.system()}")
    ]

    def load_script(self):
        """
        Load the script file, excluding preloaded resources and comments.
        """
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"Script file not found: {self.script_path}")

        with open(self.script_path, 'r', encoding='utf-8') as f:
            main_script = [
                line.strip() for line in f.readlines()
                if line.strip() and not line.strip().startswith(self.COMMENT_PREFIX)
                and not any(line.strip().startswith(f"{self.COMMAND_PREFIX}{cmd}") for cmd in ["background", "sprite", "var"])
            ]

        self.script = self.process_imports(main_script)
        Log("Script loaded...")
    
    def preprocess_script(self):
        """
        Preprocess the script to load resources and map scene boundaries.
        """
        scene_boundaries = {}
        current_scene = None
        start_line = None
        for idx, line in enumerate(self.script):
            if line.startswith(f"{self.COMMAND_PREFIX}background"):
                # Load background resource
                parts = line.split(maxsplit=2)
                if len(parts) == 3 and "=" in parts[2]:
                    key, path = parts[1], parts[2].split("=", 1)[1].strip()
                    self.images[key] = self.load_background(key, path)
                else:
                    raise ValueError(f"Invalid background syntax at line {idx + 1}: {line}")
            elif line.startswith(f"{self.COMMAND_PREFIX}sprite"):
                # Load sprite resource
                parts = line.split(maxsplit=2)
                if len(parts) == 3 and "=" in parts[2]:
                    key, path = parts[1], parts[2].split("=", 1)[1].strip()
                    self.sprites[key] = self.load_sprite(key, path)
                else:
                    raise ValueError(f"Invalid sprite syntax at line {idx + 1}: {line}")
            elif line.startswith(f"{self.COMMAND_PREFIX}var"):
                # Initialize variables
                parts = line.split(maxsplit=2)
                if len(parts) == 3 and "=" in parts[2]:
                    key, value = parts[1], parts[2].split("=", 1)[1].strip()
                    self.variables[key] = self.parse_value(value)
                else:
                    raise ValueError(f"Invalid variable syntax at line {idx + 1}: {line}")
            elif line.startswith(f"{self.COMMAND_PREFIX}scene"):
                # Start of a new scene
                if current_scene:
                    # Save the previous scene's end line
                    scene_boundaries[current_scene]["end"] = idx - 1
                current_scene = line.split()[1]
                start_line = idx
                scene_boundaries[current_scene] = {"start": start_line}
                print(scene_boundaries)

            elif line.startswith(f"{self.COMMAND_PREFIX}endScene"):
                # End of the current scene
                if current_scene:
                    scene_boundaries[current_scene]["end"] = idx
                    current_scene = None

        self.scene_boundaries = scene_boundaries
    
    def process_imports(self, script_lines):
        """
        The function `process_imports` processes script lines by recursively importing and processing
        other script files based on specified import syntax.
        
        :param script_lines: The `process_imports` method you provided takes a list of `script_lines` as
        input and processes them to handle imports in a custom scripting language
        :return: The `process_imports` method returns a list of processed script lines after handling
        imports recursively.
        """
        processed_lines = []

        for line in script_lines:
            if line.startswith(f"{self.COMMAND_PREFIX}import"):
                parts = line.split()
                if len(parts) != 2:
                    raise ValueError(f"Invalid @import syntax: {line}")
                
                import_path_debug = os.path.join(self.game_folder, f"{parts[1]}.kag.debug")
                import_path_def = os.path.join(self.game_folder, f"{parts[1]}.kag")

                import_path = None
                
                if os.path.exists(import_path_debug):
                    import_path = import_path_debug
                elif os.path.exists(import_path_def):
                    import_path = import_path_def
                else:
                    raise FileNotFoundError(f"The '{parts[1]}' script was not found and could not be imported.")

                with open(import_path, 'r', encoding='utf-8') as f:
                    imported_lines = [
                        l.strip() for l in f.readlines() 
                        if l.strip() and not l.strip().startswith(self.COMMENT_PREFIX)
                    ]

                processed_lines.extend(self.process_imports(imported_lines))
            else:
                processed_lines.append(line)

        return processed_lines

    def parse_line(self, line: str):
        """
        The function `parse_line` in Python parses a line of text based on prefixes and executes
        commands or parses dialogues accordingly.
        
        :param line: The `line` parameter in the `parse_line` method represents a single line of a
        script that needs to be parsed. The method checks the content of the line to determine whether
        it is a command, a dialogue, or if it does not match the expected syntax
        :type line: str
        """
 
        if line.startswith(self.COMMAND_PREFIX):  # Command
            self.execute_command(line[1:])
        elif self.DIALOGUE_PREFIX in line:  # Dialogue
            self.parse_dialogue(line)
            
        else:
            raise ValueError(f"Invalid script syntax: {line}")

    def execute_command(self, command: str):
        """
        The `execute_command` function in Python parses and executes different commands based on the
        input provided.
        
        :param command: The `execute_command` method takes a command as a string input and then
        processes it based on the command type. The method splits the command string into parts and
        extracts the command keyword. It then checks if the command is valid and executes the
        corresponding logic based on the command type
        :type command: str
        """

        parts = command.split()
        cmd = parts[0]

        if cmd not in self.COMMAND_LIST:
            raise ValueError(f"Invalid command: {cmd}")

        match cmd:
            # Command to change the window title @game_title <title>
            case "game_title":
                _, title = self.parse_variables(parts, 1)
                pygame.display.set_caption(title.replace('"', ''))
            
            case "game_icon":
                _, icon = self.parse_variables(parts, 1)
                if icon.endswith('.png'):
                    raise ValueError(f"Error: The icon file not need extension .png")
                
                icon_path = os.path.join(self.base_folder, f"{icon}.png")

                if os.path.exists(icon_path):
                    icon_surface = pygame.image.load(icon_path)
                    pygame.display.set_icon(icon_surface)
                else:
                    raise FileNotFoundError(f"Error: The Icon file not found in {icon_path}")
            
            case "game_version":
                _, v = self.parse_variables(parts, 1)
                if v.isdigit():
                    raise ValueError("Error: The game version must be of type float")
                self.variables["game_version"] = self.parse_value(v)
            
            case "game_textbox_font_color":
                rgb = self.parse_rbg_color(parts)
                self.dialogue_box_text_color = rgb
            
            case "game_textbox_background_color":
                rgb = self.parse_rbg_color(parts)
                
                self.dialog_box_color = rgb

            case "import":
                raise ValueError("@import commands should be resolved during script loading.")
                
            
            # Variable definition @var <key> = <value>
          
            case "var":
                key, value = self.parse_variables(parts, 3)
                
                check = self.check_reserved_variables(key)
                
                if check:
                    raise ValueError(f"Error: The variable '{key}' is reserved by the engine.")
                else:
                    self.variables[key] = self.parse_value(value)

            # Character definition @char <char> or @char <char> = <value>
            case "char":
                key, value = self.parse_variables(parts, 3)
                if value == "":  # if value is not defined use the variable name as the value
                    if parts[1] not in self.characters:
                        self.characters[parts[1]] = parts[1]
                    else:
                        raise ValueError(f"Error: The character {parts[1]} is duplicated.")
                else:  # if value is defined use the value as the character name
                    if parts[1] not in self.characters:
                        self.characters[key] = self.parse_value(value)
                    else:
                        raise ValueError(f"Error: The character {parts[1]} is duplicated.")

            # Rename defined character @renameChar <char> = <value>
            case "renameChar":
                key, value = self.parse_variables(parts, 3)

                if key in self.characters:
                    self.characters[key] = self.parse_value(value)
                else:
                    raise ValueError(f"Error: The Character '{key}' cannot be renamed because it is not defined.")

            # Background image definition @background <key> = <path>
            case "background":
                key, path = self.parse_variables(parts, 3)
                image = self.load_background(key, path)
                self.images[key] = image

            # Sprite definition @sprite <key> = <path>
            case "sprite":
                key, image_name = self.parse_variables(parts, 3)
                image = self.load_sprite(key, image_name)
                

                self.sprites[key] = image

            # Set variable @setVar <var> = <value>
            case "setVar":
                key, value = self.parse_variables(parts, 3)

                check = self.check_reserved_variables(key)
                
                if check:
                    raise ValueError(f"Error: The variable '{key}' is reserved by the engine.")
                else:
                    self.variables[key] = self.parse_value(value)
                

            # show sprite image @show_sprite <key>
            case "show_sprite":
                sprite_key = parts[1]
                prefixes = ['pos=']
                default_values = {
                    'pos=': 'center'
                }
                modifiers = self.parse_modifiers(parts, prefixes, default_values)
                self.display_sprite(sprite_key, modifiers)
            
            # remove the sprite @ remove_sprite <key>
            case "remove_sprite":
                sprite = parts[1]
                remove = [t for t in self.current_sprites if t[0] != sprite]
                
                self.current_sprites = remove
                
            # Scene definition @bg <key>
            case "bg":
                image = parts[1]
                self.display_scene(image)

            # Label definition @scene <key>
            case "scene":
                if parts[1] not in self.labels:
                    self.labels.append(parts[1])
                else:
                    raise ValueError(f"Error: The Scene '{parts[1]}' is Duplicated.")

            # Jump to a label @change_scene <label>
            case "change_scene":
                self.jump_to_label(parts[1])

            # Return to previous jump point @return
            case "return":
                self.return_from_jump()

            # Flag definition @conditional <flag>
            case "conditional":
                self.flags[parts[1]] = None  # Initialize a flag as None

            # Set a condition boolean value @setCondtion <flag> = <value> (True or False)
            case "setCondtion":
                flag, value = self.parse_variables(parts, 3)

                if value not in ['True', 'False']:
                    raise ValueError(f"Error: The conditional value is invalid, must be True or False.")

                if flag in self.flags:
                    self.flags[flag] = value
                else:
                    raise ValueError(f"Error: The '{flag}' conditional not defined")

            # Conditional block @if <condition> | <flag>
            case "if":
                condition = ' '.join(parts[1:])
                if not self.evaluate_condition(condition):
                    self.skip_to_endif()
            
            # End of conditional block @endif
            case "endif":
                pass  # End of conditional block

            case "pass": # do nothing
                pass

            # End of Label @endScene
            case "endScene":
                self.current_line = len(self.script)  # End the script
                # reset current data
                self.current_background = None
                self.current_sprites = []
                self.dialogue_queue = []
            
            case "menu":
                menu = parts[1]
                self.current_menu = menu

            case _:
                raise ValueError(f"Error: Unknown command ({cmd})")
    
    def parse_modifiers(self, parts, prefixes = [], default_values={}):
        """
        The function `parse_modifiers` takes a list of parts, a list of prefixes, and a dictionary of
        default values, and returns a dictionary of matching values for each prefix.
        
        :param parts: The `parts` parameter in the `parse_modifiers` method is expected to be a list of
        strings. These strings are used to extract values based on the prefixes provided and the default
        values specified
        :param prefixes: The `prefixes` parameter in the `parse_modifiers` method is a list of strings
        that represent the prefixes used to identify the modifiers in the `parts` list. These prefixes
        are used to extract specific values from the `parts` list based on the prefix provided
        :param default_values: The `default_values` parameter in the `parse_modifiers` method is a
        dictionary that contains default values for the prefixes that are being parsed. If a prefix is
        not found in the `parts` list or does not have a value specified after the `=` sign, the default
        value for that prefix
        :return: The `parse_modifiers` function returns a dictionary `matching_values` where the keys
        are the prefixes provided in the `prefixes` list, and the values are obtained by extracting the
        values associated with each prefix from the `parts` list. If a value is not found for a prefix,
        it will default to the corresponding value from the `default_values` dictionary.
        """
        
        matching_values = {prefix: (next((item.split('=')[1] for item in parts if item.startswith(prefix)), default_values.get(prefix))) 
                   for prefix in prefixes}
        return matching_values
            
    def check_reserved_variables(self, key):
        """
        The function `check_reserved_variables` checks if a given key is in a list of reserved
        variables.
        
        :param key: The `key` parameter in the `check_reserved_variables` function is used to specify
        the variable name that you want to check against the list of reserved variables
        :return: The function is checking if the input key matches any of the reserved variables in the
        list self.RESERVED_VARIABLES. If a match is found, the function returns True, indicating that
        the key is a reserved variable. If no match is found, the function returns False, indicating
        that the key is not a reserved variable.
        """
 
        r = [t for t in self.RESERVED_VARIABLES if t[0] == key]

        if r: return True
        
        return False
    
    def parse_rbg_color(self, parts):
        """
        This Python function parses an RGB color represented as a list of parts and returns the
        individual color components along with an optional alpha value.
        
        :param parts: The `parse_rbg_color` function takes a list of parts as input, where the first
        element is not included in the RGB values. The function extracts the RGB values from the parts
        list and returns them as integers. If there is an alpha value present, it is also extracted and
        returned as either
        :return: either a tuple of integers representing the RGB color values (r, g, b) or a tuple of
        integers representing the RGB color values along with the alpha value (r, g, b, alpha).
        """
 
        rgb = parts[1:]

        if len(rgb) > 3:
            r,g,b,a = rgb

            alpha = 0

            if a.isdigit():
                alpha = int(a)
            else:
                alpha = float(a)


            return int(r), int(g), int(b), alpha
        r, g, b = rgb
        return int(r), int(g), int(b)
    
    def load_sprite(self, key, image):
        """
        The function `load_sprite` loads a sprite image file, performs validation checks, and returns
        the key and sprite image.
        
        :param key: The `key` parameter in the `load_sprite` method is used to identify the sprite being
        loaded. It is a unique identifier for the sprite within the game
        :param image: The `image` parameter in the `load_sprite` method is a string that represents the
        key or name of the sprite image file to be loaded. It is used to identify and load the specific
        sprite image file from the game's assets folder
        :return: a tuple containing the key and the loaded sprite image.
        """
        if image.endswith('.png'):
            raise ValueError(f"Error: The sprite '{key}' not need extension .png")


        character_image = os.path.join(self.game_folder, 'assets','sprites', f"{image}.png")

        if not os.path.exists(character_image):
            raise FileNotFoundError(f"Error: Character image not found in {character_image}")

        sprite_image = pygame.image.load(character_image).convert_alpha()
        sprite_width, sprite_height = sprite_image.get_size()

        if not sprite_width == 740 and not sprite_height == 1080:
            raise ValueError("Error: The sprite size must be 740x1080")
        
        Log(f"The sprite '{key}' was loaded")

        return key, sprite_image
    
    def load_background(self, key, image):
        """
        The function `load_background` loads a background image for a game using Pygame and raises an
        error if the image file is not found.
        
        :param key: The `key` parameter in the `load_background` function is used to identify the
        background image that is being loaded. It is a unique identifier for the background image within
        the game
        :param image: The `image` parameter in the `load_background` function represents the filename of
        the background image that you want to load for your game. It is used to locate the image file
        within the specified directory structure and load it into the game using Pygame
        :return: a tuple containing the key and the loaded background image.
        """

        background_image = os.path.join(self.game_folder, 'assets','bg', image)

        if not os.path.exists(background_image):
            raise FileNotFoundError(f"Error: Background image not found in {background_image}")
        
        image = pygame.image.load(background_image).convert_alpha()

        Log(f"The background '{key}' was loaded")
 
        return key, image

    def return_from_jump(self):        
        """
        The function `return_from_jump` sets the current line to the last jump line if it exists,
        otherwise raises a ValueError.
        """
        if hasattr(self, 'last_jump_line'):
            self.current_line = self.last_jump_line
        else:
            raise ValueError("Error: Not previous scene point detected.")

    def jump_to_label(self, label: str):

        if label not in self.scene_boundaries:
            
            raise ValueError(f"Error: The scene '{label}' was not found, and the @change_scene cannot be executed.")
        
        self.current_line = self.scene_boundaries[label]["start"]
    
    def calculate_positions(self, size):
        """
        The function calculates the positions of elements based on the given size, with options for
        left, center, and right alignments.
        
        :param size: The `size` parameter is a tuple containing the width and height of a container or a
        bounding box
        :return: A dictionary containing the positions for "left", "center", and "right" keys with
        corresponding coordinate values.
        """
        width, height = size
      
        return {
            "left": (0, 0),
            "center": (width * 0.5, 0),
            "right": (width, 0),
        }

    def display_scene(self, image_key: str):
        """
        This function displays a background image in a scene and logs the action.
        
        :param image_key: The `image_key` parameter is a string that represents the key used to retrieve
        a specific image from a dictionary of images stored in the `self.images` attribute
        :type image_key: str
        """

        if not image_key in self.images:
            raise ValueError(f"Error: Background not defined: {image_key}")
        
        background_surface = self.images[image_key][1]
        
        self.current_background = background_surface
        self.needs_update = True
        Log(f"Background '{image_key}' displayed.")

    def display_sprite(self, sprite_key, modifiers):
        """
        This function displays a sprite on the screen with a specified zoom factor and position.
        
        :param sprite_key: The `sprite_key` parameter is used to identify which sprite to display. It is
        a unique identifier for a specific sprite in the game
        :param modifiers: Modifiers is a dictionary containing additional information for displaying the
        sprite. In this context, it seems to contain a key "pos" which specifies the position where the
        sprite should be displayed. The value associated with the "pos" key in the modifiers dictionary
        is used to determine the position of the sprite on the
        """

        if not self.sprites[sprite_key]:
            raise ValueError(f"Error: Sprite not defined: {sprite_key}")
        
        sprite_surface = self.sprites[sprite_key][1]
        sprite_width, sprite_height = sprite_surface.get_size()

        zoom_factor = 0.7 # for the moment 0.7

        self.current_sprites.append((sprite_key, sprite_surface, (sprite_width, sprite_height), modifiers["pos="], zoom_factor))
        self.needs_update = True
        Log(f"Sprite '{sprite_key}' displayed.")
    
    def display_dialogue(self, virtual_work, textbox):
        """
        The function `display_dialogue` displays dialogue in a dialogue box on a virtual workspace using
        the provided textbox.
        
        :param virtual_work: Virtual_work is the area or canvas where the dialogue box will be
        displayed. It could be a virtual screen or workspace where the dialogue will appear
        :param textbox: The `textbox` parameter in the `display_dialogue` method is likely an object
        that provides functionality for drawing a dialogue box on the screen. It seems to have a method
        called `draw_dialogue_box` that takes several arguments including the `virtual_work`,
        `dialogue`, `character`, `
        """

        if self.dialogue_queue:
            character, dialogue = self.dialogue_queue[0]
             
            textbox.draw_dialogue_box(
                virtual_work,
                dialogue,
                character,
                self.dialog_box_color,
                self.dialogue_box_text_color
            )

    def parse_dialogue(self, line: str):
        """
        The `parse_dialogue` function parses a line of dialogue, extracts the character and dialogue
        text, replaces variables in the dialogue, and adds the parsed dialogue to a queue for further
        processing.
        
        :param line: The `parse_dialogue` method takes a single parameter `line`, which is expected to
        be a string representing a line of dialogue. This method parses the line to extract the
        character speaking and the actual dialogue spoken by that character. The character and dialogue
        are then processed and added to a dialogue queue for
        :type line: str
        """
        
        character, dialogue = line.split(':', 1)
        character = character.strip()
        character = self.characters.get(character, character)
        dialogue = self.replace_variables(dialogue.strip())

        self.dialogue_queue.append((character, dialogue))
        self.needs_update = True

    def replace_variables(self, text: str) -> str:
        """
        The function `replace_variables` replaces variables in a text string with their corresponding
        values.
        
        :param text: The `text` parameter in the `replace_variables` method is a string that may contain
        placeholders in the format `{key}` that need to be replaced with corresponding values from the
        `self.variables` dictionary
        :type text: str
        :return: The `replace_variables` method returns a string where any variables in the format
        `{key}` are replaced with their corresponding values from the `self.variables` dictionary.
        """

        for key, value in self.variables.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text

    def parse_variables(self, parts, index):
        """
        The function `parse_variables` extracts a key and value from a list of parts starting from a
        specified index.
        
        :param parts: The `parts` parameter seems to be a list of strings. In the provided code snippet,
        it is being used to extract the `key` and `value` from specific indices within this list
        :param index: The `index` parameter in the `parse_variables` function represents the starting
        index in the `parts` list from where the value should be extracted and joined together
        :return: The `parse_variables` function is returning a tuple containing the `key` and `value`.
        The `key` is extracted from the second element of the `parts` list (at index 1), and the `value`
        is created by joining the elements of the `parts` list starting from the `index` provided.
        """

        key, value = parts[1], ' '.join(parts[index:])
        return key, value 

    def parse_value(self, value: str):
        """
        The function `parse_value` takes a string input and returns the value without leading or
        trailing double quotes if present.
        
        :param value: The `parse_value` method you provided seems to be checking if the input `value` is
        enclosed in double quotes. If it is, it strips the quotes and returns the value. If the value
        contains a dot ('.'), it returns the value as is. Otherwise, it returns the value unchanged
        :type value: str
        :return: The function will return the input value if it does not start with a double quote and
        end with a double quote, and if it does not contain a period. If the input value does start and
        end with double quotes, it will return the value with the quotes stripped.
        """

        if value.startswith('"') and value.endswith('"'):
            return value.strip('"')
        try:
            if '.' in value:
                return value
            return value
        except Exception as e:
            raise Exception(f"{e}")
            
    def evaluate_condition(self, condition: str) -> bool:
        """
        The function `evaluate_condition` takes a string representing a condition, replaces variables
        and flags with their values, and evaluates the condition using Python's `eval` function,
        returning a boolean result.
        
        :param condition: The `evaluate_condition` method takes a string `condition` as input, which
        represents a logical condition that needs to be evaluated. The method processes the condition by
        replacing variables with their values and flags with their boolean values, and then evaluates
        the resulting expression using the `eval` function
        :type condition: str
        :return: The `evaluate_condition` method returns a boolean value after evaluating the given
        condition string.
        """
         
        try:
            tokens = condition.split()
            for i, token in enumerate(tokens):
                if token in self.variables:
                    value = self.variables[token]
                    if isinstance(value, str):
                        tokens[i] = f'"{value}"'
                    else:
                        tokens[i] = str(value)
                elif token in self.flags:
                    tokens[i] = str(self.flags[token])  # Replace flag with its boolean value
            condition = ' '.join(tokens)
            return eval(condition, {}, {})
        except Exception as e:
            raise ValueError(f"Invalid condition: {condition}") from e
    
    def skip_to_endif(self):
        """
        The function `skip_to_endif` in Python skips to the next "endif" statement while handling nested
        "if" statements.
        """

        nested_ifs = 0
        while self.current_line < len(self.script):
            self.current_line += 1
            line = self.script[self.current_line].strip()
            if line.startswith(self.COMMAND_PREFIX):
                cmd = line[1:].split()[0]
                if cmd == "if":
                    nested_ifs += 1
                elif cmd == "endif":
                    if nested_ifs == 0:
                        break
                    else:
                        nested_ifs -= 1

    def in_game_render(self,virtual_work, window_size, textbox = None):
        """
        The function `in_game_render` renders background, sprites, and textbox onto a virtual work
        surface before displaying it on the screen.
        
        :param virtual_work: Virtual work is a surface where all the rendering is done before blitting
        it to the actual screen. It acts as a buffer for rendering images and text before displaying
        them on the screen
        :param window_size: The `window_size` parameter in the `in_game_render` method represents the
        size of the window or screen where the game is being rendered. It is used to scale the
        background and sprites to fit the window properly. The `window_size` parameter is typically a
        tuple containing the width and height of
        :param textbox: The `textbox` parameter in the `in_game_render` method is used to display text
        or dialogue on the game screen. It is an optional parameter that allows you to pass a textbox
        object to the method for rendering text content during the game. If the `textbox` parameter is
        not provided (i
        :return: The `in_game_render` method returns an exception if any error occurs during its
        execution. If there are no errors and the conditions are not met, it returns early without any
        specific value.
        """
        try:
            
            if not self.needs_update:
                return
            
            if textbox is None:
                return
            
            if self.current_background:
                bg_scaled = pygame.transform.smoothscale(self.current_background, window_size)
                
                virtual_work.blit(bg_scaled, (0, 0))

            for _, sprite_surface, sprite_size, sprite_position_string, zoom in self.current_sprites:

                scaled_size = (
                    sprite_size[0] * virtual_work.get_width() / self.screen_size[0],
                    sprite_size[1] * virtual_work.get_height() / self.screen_size[1]
                )

                sprite_position = self.calculate_positions(scaled_size)
                sprite = None
                if zoom:
                    sprite_scaled = pygame.transform.smoothscale(sprite_surface, scaled_size)
                    sprite = pygame.transform.rotozoom(sprite_scaled, 0, zoom)
                else:
                    sprite = pygame.transform.smoothscale(sprite_surface, scaled_size)
                
                virtual_work.blit(sprite, sprite_position[sprite_position_string])

       
            # pass the textbox to display_dialogue
            self.display_dialogue(virtual_work, textbox)
            

            self.screen.blit(virtual_work, (0,0)) 

         
        except Exception as e:
            return e
    
    def render(self, textbox = None):
        """
        This Python function renders the game process onto a virtual surface and then blits it onto the
        screen for display.
        
        :param textbox: The `textbox` parameter in the `render` method is used to pass a textbox object
        that can be rendered on the screen. This textbox object may contain text or other information
        that needs to be displayed to the user during the rendering process. If the `textbox` parameter
        is not provided (i.e
        """
        window_size = pygame.display.get_window_size()
        virtual_work = pygame.Surface(window_size)
        virtual_work = virtual_work.convert_alpha()

        # render the game process
        self.in_game_render(virtual_work, window_size, textbox)

        self.screen.blit(virtual_work, (0,0)) 
        # we need update in everymoment...
        pygame.display.update()

    def new_screen_context(self, size, flags):
        """
        This function creates a new screen context in Pygame with the specified size and flags.
        
        :param size: The `size` parameter in the `new_screen_context` method is used to specify the
        dimensions of the screen or display window that will be created using `pygame.display.set_mode`.
        It typically takes a tuple `(width, height)` representing the width and height of the screen in
        pixels. For example,
        :param flags: The `flags` parameter in the `new_screen_context` function is used to specify
        various display options when creating a new Pygame display surface. These flags can include
        options such as fullscreen mode, resizable window, double buffering, and more. By passing
        different flag values, you can customize the behavior and
        """
        self.screen = pygame.display.set_mode(size, flags, 32, vsync=1)
        self.needs_update = True
    
    def handle_events(self):
        """
        The `handle_events` function in Python processes various pygame events such as quitting the
        game, handling mouse clicks, window resizing, toggling fullscreen mode, and exiting the game.
        """
     
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
            
                if self.dialogue_queue:
                    self.dialogue_queue.pop(0)
                elif self.current_line >= len(self.script):
                    self.running = False

            if event.type == pygame.WINDOWRESIZED:
                self.needs_update = True
            if event.type == pygame.WINDOWRESTORED:
                self.needs_update = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                if pygame.display.get_driver() =='x11':
                    pygame.display.toggle_fullscreen()
                else:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.new_screen_context(self.monitor_size, self.pygame_flags | pygame.FULLSCREEN)
                    else:
                        self.new_screen_context(self.default_screen_size, self.pygame_flags)
                    
                self.needs_update = True
            if event.type == pygame.VIDEORESIZE:
                self.new_screen_context((event.w, event.h), self.pygame_flags | pygame.RESIZABLE)
                

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def run(self):
        """
        Main game loop with script preprocessing.
        """
        self.load_script()
        if not self.script:
            print("No script to execute. Please check the script path.")
            return

        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        
        self.font = pygame.font.Font(None, 33)
        self.clock = pygame.time.Clock()
        self.display_info = pygame.display.Info()

        self.monitor_size = (self.display_info.current_w, self.display_info.current_h)

        Log(f'desktop size: {self.monitor_size}')

        if not self.show_window:
            self.new_screen_context(self.default_screen_size, self.pygame_flags)

            pygame.display.set_caption(f"VNEngine - {version}{prefix_version}")
            if os.path.exists(os.path.join(self.base_folder, 'icon.png')):
                pygame.display.set_icon(pygame.image.load(os.path.join(self.base_folder, 'icon.png')))
                Log("game icon was loaded")

            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            self.show_window = True

        Log(f'video mode size: ({pygame.display.Info().current_w},{pygame.display.Info().current_h})')

        # Preprocess the script here, and avoid
        
        self.preprocess_script()

        try:
            textbox = TextBox(30, self.typing_speed, self.char_index)

            while self.running:
                self.handle_events()
                self.render(textbox)

                if self.current_line < len(self.script):
                    if not self.dialogue_queue:
                        line = self.script[self.current_line]
                        self.parse_line(line)
                        self.current_line += 1
                else:
                    if not self.dialogue_queue:
                        self.running = False

                self.clock.tick(30)
        except Exception as e:
            raise ValueError(f"{e}")
    
    def run_for_console(self):
        """Run the visual novel script."""
        self.load_script()
        while self.current_line < len(self.script):
            line = self.script[self.current_line]
            self.parse_line(line)
            self.current_line += 1

def Log(log):
    """
    The function `Log` appends a log message to a file named 'log.txt'.
    
    :param log: The `Log` function takes a parameter `log`, which is a string representing the log
    message that you want to write to a file named `log.txt`. The function appends the log message to
    the file
    """
    
    with open('log.txt', 'a+') as f:
        f.write("\n")
        f.write(log)
        f.close()

def write_file_in_game_folder(file, content):
    """
    The function `write_file_in_game_folder` writes content to a file located in the "game" folder and
    logs a success message.
    
    :param file: The `file` parameter is a string that represents the name of the file that will be
    created in the "game" folder
    :param content: The `content` parameter in the `write_file_in_game_folder` function refers to the
    data that you want to write to the file specified by the `file` parameter. This data can be text,
    numbers, or any other information that you want to store in the file
    """
    with open(f'game/{file}', 'w') as f:
        f.write(content)
        f.close()

        Log(f"{file} generated successfully.")

def generate_files():
    """
    The function `generate_files` creates necessary game files and directories for a sample visual novel
    game.
    """
    Log("Generating game files...")
    os.makedirs('game', exist_ok=True)
    os.makedirs(os.path.join('game', 'assets', 'bg'), exist_ok=True)
    os.makedirs(os.path.join('game', 'assets', 'sprites'), exist_ok=True)
    write_file_in_game_folder("assets.kag", """# Define background images
# @background <key> = <image name>

# Define sprite images
# @sprite <key> = <image name>
        """)
    write_file_in_game_folder("config.kag", """# Settings
@game_title "Sample Visual Novel"
        """)
    write_file_in_game_folder("script.kag", """# This is a sample script file.

@import config
@import assets
                                                    
# Define characters
@char Sayuri

@scene start
    Sayuri: Hello, World!
    Sayuri: This is a sample visual novel script.
    Sayuri: You can customize it to create your own story.
    Sayuri: Enjoy the journey!
@endScene # finish the scene or close the game
        """)
    
    Log(f"Game files generated successfully.")
    
    

if __name__ == "__main__":
    
    root = None
    if sys.executable.endswith('engine.py'):
        # TODO For debuging
        root = __file__
    
    elif sys.executable.endswith(f"{builded_file_name}.exe"):
        root = sys.executable
    else:
        root = sys.argv[0]
    
    dirname = os.path.dirname(root)
    base_folder = os.path.join(dirname)
    game_folder = os.path.join(base_folder, 'game')

    init_log_template = """created at: %(createdAt)s
Plataform: %(plataform)s
VNE v%(engineVersion)s
"""
    init_log_template_data = {
        'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'plataform': f"{platform.system()}-{platform.version()}",
        'engineVersion': f"{version}{prefix_version}",
    }

    with open('log.txt', 'w') as f:
        f.write(init_log_template % init_log_template_data)
        pass

    try:
        script_file = None
        if os.path.exists(game_folder):

            kagFile = os.path.join(game_folder, 'script.kag')
            kagDebugFile = os.path.join(game_folder, 'script.kag.debug')

            if os.path.exists(kagFile):
                script_file = os.path.join(game_folder, 'script.kag')
            elif os.path.exists(kagDebugFile):
                script_file = os.path.join(game_folder, 'script.kag.debug')
            else:
                raise FileNotFoundError("Error: No valid script file found in the game folder.")
            
        else:
            generate_files()
            script_file = os.path.join(game_folder, 'script.kag')
        engine = VNEngine(
            script_file, 
        
            game_folder=game_folder,
            base_folder=base_folder
        )
        engine.run()

    
    except Exception as e:
        traceback_template = '''Exception error:
  %(message)s\n

  %(plataform)s
  VNE v%(engineVersion)s
  '''

        traceback_details = {
            'message' : e,
            'plataform': f"{platform.system()}-{platform.version()}",
            'engineVersion': version+prefix_version
        }    

        Log(f"Script was failed. Check the traceback-error.txt file for more information.")
        
        print(traceback_template % traceback_details)

        with open('traceback-error.txt', 'w') as f:
            f.write(traceback_template % traceback_details)
            f.close()
        
        
