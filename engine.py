import os
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from datetime import datetime

import platform
# This class `VNEngine` is used for initializing a visual novel engine with specified script and
# configuration paths, as well as optional game and base folders.

version = "0.0.0-alpha.5"
version_name = "N/a"
builded_file_name = "vne"

class VNEngine:
    
    def __init__(self, 
                 script_path: str, 
                 config_path: str = None, 
                  
                 game_folder: str = None,
                 base_folder: str = None
                 ):

        self.pygame_flags = pygame.SCALED | pygame.HWSURFACE | pygame.DOUBLEBUF
        self.screen_size = (1280, 720)
        self.screen = None  
       
        
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
 

        self.chars_displayed = 0
        self.dialogue_start_time = None
 
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
        #'game_size',
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
 
        
        if not os.path.exists(self.script_path):
            raise FileNotFoundError(f"Script file not found: {self.script_path}")

        with open(self.script_path, 'r', encoding='utf-8') as f:
            self.script = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith(self.COMMENT_PREFIX)]
            Log(f"Script loaded...")

 
    def parse_line(self, line: str):
 
        if line.startswith(self.COMMAND_PREFIX):  # Command
            self.execute_command(line[1:])
        elif self.DIALOGUE_PREFIX in line:  # Dialogue
            self.parse_dialogue(line)
            
        else:
            raise ValueError(f"Invalid script syntax: {line}")

    def execute_command(self, command: str):
 
         
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
                self.variables[key] = self.parse_value(value)

            # show sprite image @show_sprite <key>
            case "show_sprite":
                sprite_key = parts[1]
                #position = self.parse_sprite_position(parts)
                self.display_sprite(sprite_key)
            
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
    
    def reset_screen(self):
 

        if self.display_info is None:
            self.display_info = pygame.display.Info()

        self.scale_factor = 1.0
        
        self.screen_size = (800, 600)

        self.screen = None
    
    def virtual_screen(self, size):
        pass
    
    def check_reserved_variables(self, key):
 
        r = [t for t in self.RESERVED_VARIABLES if t[0] == key]

        if r: return True
        
        return False
    
    def parse_rbg_color(self, parts):
 
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


        character_image = os.path.join(self.game_folder, 'assets','sprites', image)

        if not os.path.exists(character_image):
            raise FileNotFoundError(f"Error: Character image not found in {character_image}")

        sprite_image = pygame.image.load(character_image).convert_alpha()
        sprite_width, sprite_height = sprite_image.get_size()

        if not sprite_width == 740 and not sprite_height == 1080:
            raise ValueError("Error: The sprite size must be 740x1080")

        return key, sprite_image
    
    def load_background(self, key, image):

        background_image = os.path.join(self.game_folder, 'assets','bg', image)

        if not os.path.exists(background_image):
            raise FileNotFoundError(f"Error: Background image not found in {background_image}")
        
        image = pygame.image.load(background_image).convert_alpha()
 
        return key, image

 
    def return_from_jump(self):        
        if hasattr(self, 'last_jump_line'):
            self.current_line = self.last_jump_line
        else:
            raise ValueError("Error: Not previous scene point detected.")

    def jump_to_label(self, label: str):

        for idx, line in enumerate(self.script):
            if line == f"@scene {label}":
                self.last_jump_line = self.current_line
                self.current_line = idx
                return
        raise ValueError(f"Error: The scene '{label}' was not found, and the @change_scene cannot be executed.")

    def display_scene(self, image_key: str):

        if not image_key in self.images:
            raise ValueError(f"Error: Background not defined: {image_key}")
        
        background_surface = self.images[image_key][1]

        bg_width, bg_height = background_surface.get_size()
        screen_width, screen_height = pygame.display.get_window_size()

        zoom_factor = 1
 

        width =  screen_width % bg_width
        height =  screen_height % bg_height

        width = int(width  * zoom_factor)
        height = int(height * zoom_factor)
    
        self.current_background = (background_surface, (width, height))
        self.needs_update = True

    def display_sprite(self, sprite_key):

        if not sprite_key in self.sprites:
            raise ValueError(f"Error: Sprite not defined: {sprite_key}")
        
        sprite_surface = self.sprites[sprite_key][1]
        sprite_width, sprite_height = sprite_surface.get_size()
        screen_width, screen_height = pygame.display.get_window_size()
     
        pos_x = 0 
        pos_y = 20  
        width =  screen_width % sprite_width  
        height =  screen_height % sprite_height 

        zoom_factor = 1

        # Apply scaling and zoom
        width = int(width  * zoom_factor)
        height = int(height * zoom_factor)

        # Center the sprite by default
        
        if pos_x == 0:  # Center horizontally
            pos_x = (screen_width - width) // 2
        if pos_y == 0:  # Center vertically
            pos_y = (screen_height - height) // 2

        
        self.current_sprites.append((sprite_surface, (width, height),(pos_x, pos_y)))
        self.needs_update = True
        Log(f"Sprite '{sprite_key}' displayed.")
    
    def display_dialogue(self, virtual_work):

        xpos = 74 # in pixels

        if self.dialogue_queue and self.screen_size:
            character, dialogue = self.dialogue_queue[0]
            character_surface = self.font.render(character, True, self.character_name_color).convert_alpha()
            
            character_rect = character_surface.get_rect()
            character_rect.y = 542
            character_rect.x = xpos

            line_height = self.font.get_height()
            char_padding = 6
              
            ch_w = character_rect.width+char_padding
            ch_h = character_rect.height+char_padding
            
            name_box = self.Box((ch_w, ch_h), self.dialog_box_color)
            
            if character:
               virtual_work.blit(name_box, (character_rect.x, character_rect.y))

            character_pos = (character_rect.x + 2, character_rect.y + 3)

            virtual_work.blit(character_surface, character_pos)

            ## for dialogue

            w = 1116
            
            wrapped_lines = self.wrap_text(dialogue, self.font, w)

            if wrapped_lines:
                line_height = self.font.get_height()
                total_height = len(wrapped_lines) * line_height + 10 
                dialogue_rect = pygame.Rect(0, 421, w, total_height)
                dialogue_rect.width = w
                dialogue_rect.height = 150
                

                dialogue_box = self.Box((pygame.display.get_window_size()[0], dialogue_rect.height), self.dialog_box_color)
                
                virtual_work.blit(dialogue_box, dialogue_rect.bottomleft)

                text_padding = 5
                
                
                for i, line in enumerate(wrapped_lines):

                
                    dialogue_surface = self.font.render(line, True, self.dialogue_text_color)
 
                    x, y = dialogue_rect.bottomleft 

                    virtual_work.blit(dialogue_surface, (x + text_padding + xpos, y + text_padding +  6  + i * line_height))

        

    
    def wrap_text(self, text, font, max_width):
 
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


    def parse_dialogue(self, line: str):
        
        character, dialogue = line.split(':', 1)
        character = character.strip()
        character = self.characters.get(character, character)
        dialogue = self.replace_variables(dialogue.strip())

        self.dialogue_queue.append((character, dialogue))
        self.needs_update = True

    def replace_variables(self, text: str) -> str:

        for key, value in self.variables.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text

    def parse_variables(self, parts, index):

        key, value = parts[1], ' '.join(parts[index:])
        return key, value 

    def parse_value(self, value: str):

        if value.startswith('"') and value.endswith('"'):
            return value.strip('"')
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def evaluate_condition(self, condition: str) -> bool:
         
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

        window_size = pygame.display.get_window_size()

        if not self.needs_update:
            return
        
        virtual_work = pygame.Surface(window_size)
        virtual_work = virtual_work.convert_alpha()
     
        if self.current_background:
            surface, size = self.current_background

            bg_scaled = pygame.transform.smoothscale(surface, size)
            
            virtual_work.blit(bg_scaled, (0, 0))

            
        for sprite_surface,  sprite_size, sprite_pos in self.current_sprites:
            sprite_scaled = pygame.transform.smoothscale(sprite_surface, sprite_size)
            
            virtual_work.blit(sprite_scaled, sprite_pos)
        
        
        self.display_dialogue(virtual_work)

        self.screen.blit(virtual_work,(0,0))

        if self.needs_update:
            pygame.display.flip()
            self.needs_update = False
         
    def Box(self, size, color):

        bx = pygame.Surface(size, pygame.SRCALPHA)
        bx.fill(color)
        return bx
    
    def handle_events(self):
     
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                
                if self.dialogue_queue:
                    self.dialogue_queue.pop(0)
                elif self.current_line >= len(self.script):
                
                    self.running = False
     
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
                self.screen_size = pygame.display.get_window_size()
                self.needs_update = True

    def run(self):
 
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
        
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        # LOAD PYGAME
        pygame.init()

        self.font = pygame.font.Font(None, 33)
        self.clock = pygame.time.Clock()

        if not self.show_window:
            self.screen = pygame.display.set_mode(self.screen_size, self.pygame_flags, 0)
          
            pygame.display.set_caption(f"VNEngine - {version}")
            if os.path.exists(os.path.join(base_folder, 'icon.png')):
                pygame.display.set_icon(pygame.image.load(os.path.join(base_folder, 'icon.png')))

       
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            self.show_window = True
        
   
        
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
# @background <key> = <image name>

# Define sprite images
# @sprite <key> = <image name>
        
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
    
    elif sys.executable.endswith(f"{builded_file_name}.exe"):
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
        
        
