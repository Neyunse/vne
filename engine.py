import os
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from datetime import datetime

import platform
# This class `VNEngine` is used for initializing a visual novel engine with specified script and
# configuration paths, as well as optional game and base folders.

version = "0.0.0-alpha.3"
version_name = "N/a"

class VNEngine:
    
    def __init__(self, 
                 script_path: str, 
                 config_path: str = None, 
                  
                 game_folder: str = None,
                 base_folder: str = None
                 ):
        """
        This Python function initializes an object with specified script, config, game, and base folder
        paths.
        
        :param script_path: The `script_path` parameter is a required argument that specifies the path
        to a script file. This parameter should be a string representing the file path where the script
        is located

        :type script_path: str

        :param config_path: The `config_path` parameter is a string that represents the path to a
        configuration file. This parameter is optional, as indicated by the default value of `None`. If
        a `config_path` is provided when initializing an instance of the class, it would be used to
        locate and load a configuration file
        
        :type config_path: str
        
        :param game_folder: The `game_folder` parameter in the `__init__` method is a string that
        represents the path to the folder where the game files are located. This parameter is optional
        and can be provided when initializing an instance of the class. If not provided, it will default
        to `None`
        
        :type game_folder: str
        
        :param base_folder: The `base_folder` parameter in the `__init__` method is used to specify the
        base folder path for the game or script. This parameter is optional and can be provided if
        needed. It allows you to set a specific base folder for your game or script, which can be useful
        for organizing
        
        :type base_folder: str
        """

        # LOAD PYGAME
        pygame.init()
 
        self.screen_size = (1280, 720)
        self.screen = pygame.display.set_mode(self.screen_size, pygame.HIDDEN)   
        pygame.display.set_caption(f"VNEngine - {version}")
        if os.path.exists(os.path.join(base_folder, 'icon.png')):
            pygame.display.set_icon(pygame.image.load(os.path.join(base_folder, 'icon.png')))
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

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
    
    
 

        self.game_folder = game_folder
        self.base_folder = base_folder


        # TODO FOR PYGAME
        self.current_background = None
        self.current_sprites = []
        self.dialogue_queue = []
        self.running = True
        self.dialogue_text_color = (255, 255, 255)
        self.character_name_color = (255, 255, 255)

        self.dialog_box_color = (0,0,0, 128)
 
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
        'label', 
        'change_scene', 
        'return',  
        'endScene',
        'conditional',
        'setCondtion',
        'renameChar',
        'if',
        'endif',
        'setVar',
        'game_size',
        'game_title',
        'game_icon',
        'game_dialogue_color',
        'game_character_color',
        'game_textbox_background_color',
        'game_version'
    ]
  
    RESERVED_VARIABLES = [
        ('engine.version', f"VNE v{version}"),
        ('engine.version_only', f"v{version}"),
        ('engine.version_name', f"{version_name}"),
        ('engine.current_plataform', f"{platform.system()}")
    ]

 
    def load_script(self):
        """
        The function `load_script` loads a script file, removes empty lines and comments, and raises an
        error if the file is not found.
        """
        
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"Script file not found: {self.script_path}")

        with open(self.script_path, 'r', encoding='utf-8') as f:
            self.script = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith(self.COMMENT_PREFIX)]
            Log(f"Script loaded...")

 
    def parse_line(self, line: str):
        """
        The function `parse_line` in Python parses a line of text to determine if it is a command,
        dialogue, or invalid syntax.
        
        :param line: The `parse_line` method takes a single parameter `line`, which is expected to be a
        string representing a line of a script. The method then checks the content of the line to
        determine whether it is a command, a dialogue, or an invalid syntax based on certain prefixes
        defined in the class `VNEngine`. 
        :type line: str
        """
         
        if line.startswith(self.COMMAND_PREFIX):  # Command
            self.execute_command(line[1:])
        elif self.DIALOGUE_PREFIX in line:  # Dialogue
            self.display_dialogue(line)
            
        else:
            raise ValueError(f"Invalid script syntax: {line}")

    def execute_command(self, command: str):
        """
        The function `execute_command` in Python processes different commands for a game script,
        handling tasks like changing screen settings, defining characters, displaying images, and
        managing conditional statements.
        
        :param command: The `execute_command` method you provided seems to be a part of a larger script
        or program that handles various commands related to a game or interactive fiction
        :type command: str
        """
         
        parts = command.split()
        cmd = parts[0]

        if cmd not in self.COMMAND_LIST:
            raise ValueError(f"Invalid command: {cmd}")

        match cmd:
            # Command to change the screen width @screen_width <width>
            case "game_size":
                w, h = self.parse_variables(parts, 2)
                if w is None or h is None:
                    raise ValueError(f"Error: Missing screen size values. Usage: @screen_size <width> <height>")
                
                width = int(w) * 1
                height = int(h) * 1
            
                self.screen_size = (width, height) 
                
                self.screen = pygame.display.set_mode(self.screen_size)
            
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
            
            case "game_dialogue_color":
                rgb = self.parse_rbg_color(parts)
                self.dialogue_text_color = rgb
            
            case "game_character_color":
                rgb = self.parse_rbg_color(parts)
                self.character_name_color = rgb
            
            case "game_textbox_background_color":
                rgb = self.parse_rbg_color(parts)
                
                self.dialog_box_color = rgb
                
            
            # Variable definition @var <key> = <value>
          
            case "var":
                key, value = self.parse_variables(parts, 3)
                
                check = self.check_reserved_variables(key)
                
                if check:
                    self.variables[key] = self.parse_value(value)
                else:
                    raise ValueError(f"Error: The variable '{key}' is reserved by the engine.")

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
                self.images[key] = path

            # Sprite definition @sprite <key> = <path>
            case "sprite":
                key, path = self.parse_variables(parts, 3)
                self.sprites[key] = path

            # Set variable @setVar <var> = <value>
            case "setVar":
                key, value = self.parse_variables(parts, 3)
                self.variables[key] = self.parse_value(value)

            # show sprite image @show_sprite <key>
            case "show_sprite":
                sprite = parts[1]
                pos_x, pos_y, sprite_scaled, zoom_image = self.parse_sprite_position(parts[2:], sprite)
                position = (pos_x, pos_y)
                self.display_sprite(sprite,sprite_scaled, position, zoom_image)
            
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

            # End of Label @endScene
            case "endScene":
                self.current_line = len(self.script)  # End the script
            
            case _:
                raise ValueError(f"Error: Unknown command ({cmd})")
    
    def check_reserved_variables(self, key):
        
        r = [t for t in self.RESERVED_VARIABLES if t[0] == key]

        if r: return True
        
        return False
    
    def parse_rbg_color(self, parts):
        """
        This Python function parses an RGB color represented as a list of parts, extracting the red,
        green, blue, and optional alpha values.
        
        :param parts: It looks like the `parse_rbg_color` function is designed to parse RGB color values
        from a list of parts. The function assumes that the RGB values are stored in the `parts` list
        starting from index 1
        :return: The `parse_rbg_color` function is returning a tuple of integers representing the RGB
        values of a color. If the input `parts` contains 4 elements (representing RGBA values), it
        returns a tuple of four integers (r, g, b, alpha). If the input `parts` contains 3 elements
        (representing RGB values), it returns a tuple of three integers (r,
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
        
    def parse_sprite_position(self, parts, sprite_key):
        """
        The function `parse_sprite_position` parses sprite position and properties, loads the sprite
        image, applies scaling and zoom, centers the sprite, and returns the position, scaled image, and
        zoom factor.
        
        :param parts: The `parts` parameter in the `parse_sprite_position` method is a list of strings
        that contain information about the position and size of a sprite. Each string in the list
        represents a specific part of the sprite's configuration, such as its x and y position, width,
        height, and zoom factor
        :param sprite_key: The `sprite_key` parameter in the `parse_sprite_position` method is used to
        identify a specific sprite image from a dictionary of sprites stored in `self.sprites`. This key
        is used to retrieve the filename of the sprite image that will be loaded and processed in the
        method
        :return: The function `parse_sprite_position` returns the position x, position y, scaled image,
        and zoom factor after processing the input parts and sprite key.
        """
         
        pos_x = 0  # Default position x
        pos_y = 20  # Default position y
        width = None
        height = None
        scale_factor = 1.0  # Default scale factor
        zoom_factor = 0.7  # Default zoom factor

        sprite = self.sprites[sprite_key].replace('=', '').strip().replace('"', '')

        character_image = os.path.join(self.game_folder, 'assets','sprites', sprite)

        if not os.path.exists(character_image):
            raise FileNotFoundError(f"Error: Character image not found in {character_image}")

        sprite_image = pygame.image.load(character_image)
        sprite_width, sprite_height = sprite_image.get_size()

        for part in parts:
            if part.startswith('x='):
                pos_x = int(part[2:])  # Extract x value
            elif part.startswith('y='):
                pos_y = int(part[2:])  # Extract y value
            elif part.startswith('width='):
                width = int(part[6:])  # Extract width value
            elif part.startswith('height='):
                height = int(part[7:])  # Extract height value
            elif part.startswith('zoom='):
                zoom_factor = float(part[6:])  # Extract zoom value

        # Get default size if no width/height provided
        width = width or sprite_width
        height = height or sprite_height

        # Apply scaling and zoom
        width = int(width  * zoom_factor)
        height = int(height * zoom_factor)

        # Center the sprite by default
        screen_width, screen_height = self.screen.get_size()
        if pos_x == 0:  # Center horizontally
            pos_x = (screen_width - width) // 2
        if pos_y == 0:  # Center vertically
            pos_y = (screen_height - height) // 2

        # Smoothscale the image to avoid pixelation
        scaled_image = pygame.transform.smoothscale(sprite_image, (width, height))
        return pos_x, pos_y, scaled_image, zoom_factor

 
    def return_from_jump(self):
        """
        The function `return_from_jump` sets the current line to the last jump line if available,
        otherwise raises a ValueError.
        """
        
        if hasattr(self, 'last_jump_line'):
            self.current_line = self.last_jump_line
        else:
            raise ValueError("Error: Not previous scene point detected.")

    def jump_to_label(self, label: str):
        """
        The function `jump_to_label` searches for a specific scene label in a script and updates the
        current line accordingly, raising an error if the label is not found.
        
        :param label: The `label` parameter in the `jump_to_label` method is a string that represents
        the scene label to which you want to jump in the script. The method searches for a line in the
        script that matches the format `@scene {label}` and updates the current line index accordingly.
        If the
        :type label: str
        :return: The `jump_to_label` method returns the line number where the specified scene label is
        found in the script.
        """
        
        for idx, line in enumerate(self.script):
            if line == f"@scene {label}":
                self.last_jump_line = self.current_line
                self.current_line = idx
                return
        raise ValueError(f"Error: The scene '{label}' was not found, and the @change_scene cannot be executed.")

    def display_scene(self, image_key: str):
        """
        This function displays a background image for a scene in a game, handling errors if the image is
        not found or not defined.
        
        :param image_key: The `image_key` parameter in the `display_scene` method is a string that
        represents the key of the image to be displayed. This key is used to retrieve the image file
        path from the `self.images` dictionary. If the key is found in the dictionary, the corresponding
        image file is loaded
        :type image_key: str
        """
         
        if image_key in self.images:
            scene = self.images[image_key].replace('=', '').strip().replace('"', '')

            background = os.path.join(self.game_folder, 'assets','bg', scene)

            Log(f"Background '{scene}' displayed.")


            if os.path.exists(background):
                self.current_background = pygame.image.load(background)
                self.current_background = pygame.transform.scale(self.current_background, self.screen_size)
                self.needs_update = True
            else:
                raise FileNotFoundError(f"Error: Background image not found in: {background}")
        else:
            raise ValueError(f"Error: Background image not defined: {image_key}")

    def display_sprite(self, sprite_key: str,sprite_image:str, position: tuple, zoom_factor: float):
        """
        This function displays a sprite image at a specified position with a given zoom factor, checking
        if the sprite key is defined in the sprites dictionary.
        
        :param sprite_key: The `sprite_key` parameter is a string that represents the key or identifier
        of the sprite you want to display. It is used to look up the sprite in the `self.sprites`
        dictionary to check if it is defined
        :type sprite_key: str
        :param sprite_image: The `sprite_image` parameter in the `display_sprite` method is a string
        that represents the image file path or name of the sprite that you want to display on the
        screen. This parameter is used to specify which image should be displayed for the given sprite
        key
        :type sprite_image: str
        :param position: The `position` parameter in the `display_sprite` method is a tuple that
        represents the position where the sprite will be displayed on the screen. It typically consists
        of two values, the x-coordinate and the y-coordinate, specifying the location of the sprite
        within the game or application window
        :type position: tuple
        :param zoom_factor: The `zoom_factor` parameter in the `display_sprite` method is a float value
        that determines the scaling factor by which the sprite image will be zoomed in or out when
        displayed on the screen. A `zoom_factor` of 1.0 represents the original size of the sprite
        image, while
        :type zoom_factor: float
        """
         
        if not sprite_key in self.sprites:
            raise ValueError(f"Error: Sprite not defined: {sprite_key}")
       
        self.current_sprites.append((sprite_key, sprite_image, position, zoom_factor))
        self.needs_update = True
        Log(f"Sprite '{sprite_key}' displayed.")
    
    def wrap_text(self, text, font, max_width):
        """
        The `wrap_text` function takes a text string, a font, and a maximum width as input, and wraps
        the text to fit within the specified width by breaking it into lines.
        
        :param text: The `wrap_text` function you provided is designed to wrap text to fit within a
        specified maximum width when rendered using a given font. It splits the input text into words
        and then constructs lines of text that do not exceed the maximum width
        :param font: The `font` parameter in the `wrap_text` function is the font object that will be
        used to render the text. This font object is typically created using a font file and the desired
        font size. It is used to render the text onto a surface with the specified font style and size
        :param max_width: The `max_width` parameter in the `wrap_text` function represents the maximum
        width in pixels that a line of text can occupy before it needs to be wrapped to the next line.
        This parameter is used to determine when a line of text exceeds the specified width and needs to
        be split into multiple lines
        :return: The function `wrap_text` returns a list of strings, where each string represents a line
        of text that has been wrapped to fit within the specified `max_width` using the provided `font`.
        """
         
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
        
            line_surface = font.render(' '.join(current_line), True, self.dialogue_text_color)
            if line_surface.get_width() > max_width:
               
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines


    def display_dialogue(self, line: str):
        """
        The function `display_dialogue` parses a line of dialogue, extracts the character and dialogue
        text, replaces variables in the dialogue, and appends the character and dialogue to a queue.
        
        :param line: The `display_dialogue` method takes in a string `line` as a parameter. This string
        is expected to contain a character name followed by a colon and then the dialogue spoken by that
        character. The method then processes this line by splitting it into the character name and
        dialogue, stripping any extra whitespace
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
        The function `replace_variables` replaces variables in a given text string with their
        corresponding values from a dictionary.
        
        :param text: The `replace_variables` method takes a string `text` as input. This method replaces
        variables in the `text` string with their corresponding values from the `self.variables`
        dictionary. It iterates over the key-value pairs in `self.variables` and replaces occurrences of
        `{key}` in the `
        :type text: str
        :return: The `replace_variables` method returns the input `text` with variables replaced by
        their corresponding values from the `self.variables` dictionary.
        """
         
        for key, value in self.variables.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text

    def parse_variables(self, parts, index):
        """
        The function `parse_variables` extracts a key and value from a list of parts starting from a
        specified index.
        
        :param parts: The `parts` parameter seems to be a list or array containing the input that needs
        to be parsed. In the provided code snippet, it is being used to extract the key and value from
        specific indices within this list
        :param index: The `index` parameter in the `parse_variables` function is used to specify the
        starting index in the `parts` list from where the values should be joined together to form the
        `value` variable
        :return: The `parse_variables` function is returning a tuple containing the `key` and `value`
        extracted from the input `parts` list.
        """
        key, value = parts[1], ' '.join(parts[index:])
        return key, value 

    def parse_value(self, value: str):
        """
        The function `parse_value` takes a string input and returns the value as an integer, float, or
        stripped string based on certain conditions.
        
        :param value: The `parse_value` method takes a string `value` as input and performs the
        following operations:
        :type value: str
        :return: The `parse_value` method will return the parsed value based on the input `value`. If
        the input `value` is enclosed in double quotes, it will return the value without the quotes. If
        the input `value` can be converted to a float, it will return the float value. If the input
        `value` can be converted to an integer, it will return the integer value. If
        """
         
        if value.startswith('"') and value.endswith('"'):
            return value.strip('"')
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def evaluate_condition(self, condition: str) -> bool:
        """
        The function evaluates a given condition string by replacing variables and flags with their
        values and then using Python's eval function to determine the boolean result.
        
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
        The function `skip_to_endif` iterates through lines of a script to skip to the next "endif"
        command while handling nested "if" statements.
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

    def render(self):
        """
        This function renders the current background, sprites, and dialogue queue onto the screen in a
        game using Pygame.
        """

        if not self.needs_update:
                return
            
        self.screen.fill((0, 0, 0))


        if self.current_background:
            self.screen.blit(self.current_background, (0, 0))

        for _ ,sprite, position, _ in self.current_sprites:
            self.screen.blit(sprite, position)

            
        if self.dialogue_queue:
            character, dialogue = self.dialogue_queue[0]
            character_surface = self.font.render(character, True, self.character_name_color)
            
            character_rect = character_surface.get_rect()
            character_rect.y = 510
            character_rect.x = 50

            line_height = self.font.get_height()
            char_padding = 6
              
            ch_w = character_rect.width+char_padding
            ch_h = character_rect.height+char_padding
            
            name_box = self.Box((ch_w, ch_h), self.dialog_box_color)
            
            if character:
                self.screen.blit(name_box, (character_rect.x, character_rect.y))

            character_pos = (character_rect.x + 2, character_rect.y + 3)

            self.screen.blit(character_surface, character_pos)
            
            wrapped_lines = self.wrap_text(dialogue, self.font, self.screen_size[0] - 100)

            for i, line in enumerate(wrapped_lines):
                dialogue_surface = self.font.render(line, True, self.dialogue_text_color)

                dialogue_rect = dialogue_surface.get_rect()
                dialogue_rect.x = 50
                dialogue_rect.y = 550

                 
                dialogue_rect.width = self.screen_size[0] - 100
                dialogue_rect.height = self.screen_size[1] - 100

                dialog_padding = 5

                tb_w = dialogue_rect.width+dialog_padding
                tb_h = dialogue_rect.height+dialog_padding

                dialogue_box = self.Box((tb_w, tb_h), self.dialog_box_color)
                
                dialog_pos = (dialogue_rect.x + 2 * dialog_padding, dialogue_rect.y + 3 * dialog_padding + i * line_height)


                
                self.screen.blit(dialogue_box, (dialogue_rect.x, dialogue_rect.y))
                self.screen.blit(dialogue_surface, dialog_pos)

            
            self.needs_update = False
            pygame.display.flip()
        
        if not self.show_window:
            self.screen = pygame.display.set_mode(self.screen_size, pygame.SHOWN)
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            self.show_window = True

        
    def Box(self, size, color):
        bx = pygame.Surface(size, pygame.SRCALPHA)
        bx.fill(color)
        return bx

    
    def handle_events(self):
        """
        The function `handle_events` processes various pygame events, such as quitting the game or
        handling mouse clicks.
        """
         
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                
                if self.dialogue_queue:
                    self.dialogue_queue.pop(0)
                elif self.current_line >= len(self.script):
                
                    self.running = False
 
    
    def run(self):
        """
        The function runs a script line by line, handling events and rendering while checking for
        errors.
        :return: The `run` method is returning None.
        """
         

        # set internal variables or reserved variables

        for vars in self.RESERVED_VARIABLES:
            key, value = vars
            self.variables[key] = value
        
        # set default version for the game
        self.variables["game_version"] = self.game_version
            
        self.load_script()
     

        if not self.script:
            print("No script to execute. Please check the script path.")
            return
        
        try:
            
            while self.running:
                self.handle_events()
                if self.needs_update:
                    self.render()

                if self.current_line < len(self.script):
                    if not self.dialogue_queue:
                        line = self.script[self.current_line]
                        self.parse_line(line)
                        self.current_line +=1
                else:
                    if not self.dialogue_queue:  
                        self.running = False

                
                self.clock.tick(30)
        except Exception as e:
            raise ValueError(f"{e}")
        finally:
            pygame.quit()

    
    def run_for_console(self):
        """Run the visual novel script."""
        self.load_script()
        while self.current_line < len(self.script):
            line = self.script[self.current_line]
            self.parse_line(line)
            self.current_line += 1


def Log(message):
    with open('log.txt', 'a') as f:
        f.write(f"-----------------[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]-----------------\n")
        f.write(f"{message}\n")
        f.close()

def generate_files():
    Log("Generating game files...")
    os.makedirs('game', exist_ok=True)
    os.makedirs(os.path.join('game', 'assets', 'bg'), exist_ok=True)
    os.makedirs(os.path.join('game', 'assets', 'sprites'), exist_ok=True)
    with open('game/script.kag', 'w') as f:
        f.write("""# This is a sample script file.

# Settings
@game_title "Sample Visual Novel"

# Define characters
@char Sayuri

# Define background images
# use @background <key> = <image name>

# Define sprite images
# use @sprite <key> = <image name>
        
@scene start
    Sayuri: Hello, World!
    Sayuri: This is a sample visual novel script.
    Sayuri: You can customize it to create your own story.
    Sayuri: Enjoy the journey!
    
    @endScene # finish the scene or close the game
        """)
        f.close()
        Log("Game files generated successfully.")

if __name__ == "__main__":
    
    root = None
    if sys.executable.endswith('engine.py'):
        # TODO For debuging
        root = __file__
    
    elif sys.executable.endswith('engine.exe'):
        root = sys.executable
    else:
        root = sys.argv[0]
    
    dirname = os.path.dirname(root)
    base_folder = os.path.join(dirname)
    game_folder = os.path.join(base_folder, 'game')

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
        
    
        traceback_template = '''
Fail while game code was running:
  File: "%(filename)s"
  %(message)s\n

  %(plataform)s
  VNE v%(engineVersion)s
  '''

        Log(f"Script was failed. Check the error.txt file for more information.")

        traceback_details = {
                         'filename': os.path.join(game_folder, "script.kag"),
                         'message' : e,
                         'plataform': f"{platform.system()}-{platform.version()}",
                         'engineVersion': version
                        }
        
        print(traceback_template % traceback_details)

        with open('traceback-error.txt', 'w') as f:
            f.write(traceback_template % traceback_details)
            f.close()
        
        
