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
prefix_version = "-alpha.9"
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
        #"menu"
    ]
  
    RESERVED_VARIABLES = [
        ('engine.version', f"VNE v{version}{prefix_version}"),
        ('engine.version_only', f"v{version}{prefix_version}"),
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
            
            case "game_textbox_font_color":
                rgb = self.parse_rbg_color(parts)
                self.dialogue_box_text_color = rgb
            
            case "game_textbox_background_color":
                rgb = self.parse_rbg_color(parts)
                
                self.dialog_box_color = rgb
                
            
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
        
        matching_values = {prefix: (next((item.split('=')[1] for item in parts if item.startswith(prefix)), default_values.get(prefix))) 
                   for prefix in prefixes}
        return matching_values
            
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

        background_image = os.path.join(self.game_folder, 'assets','bg', image)

        if not os.path.exists(background_image):
            raise FileNotFoundError(f"Error: Background image not found in {background_image}")
        
        image = pygame.image.load(background_image).convert_alpha()

        Log(f"The background '{key}' was loaded")
 
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
    
    def calculate_positions(self, size):
        width, height = size
      
        return {
            "left": (0, 0),
            "center": (width * 0.5, 0),
            "right": (width, 0),
        }

    def display_scene(self, image_key: str):

        if not image_key in self.images:
            raise ValueError(f"Error: Background not defined: {image_key}")
        
        background_surface = self.images[image_key][1]
        
        self.current_background = background_surface
        self.needs_update = True
        Log(f"Background '{image_key}' displayed.")

    def display_sprite(self, sprite_key, modifiers):

        if not self.sprites[sprite_key]:
            raise ValueError(f"Error: Sprite not defined: {sprite_key}")
        
        sprite_surface = self.sprites[sprite_key][1]
        sprite_width, sprite_height = sprite_surface.get_size()

        zoom_factor = 0.7 # for the moment 0.7

        self.current_sprites.append((sprite_key, sprite_surface, (sprite_width, sprite_height), modifiers["pos="], zoom_factor))
        self.needs_update = True
        Log(f"Sprite '{sprite_key}' displayed.")
    
    def display_dialogue(self, virtual_work, textbox):

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
                return value
            return value
        except Exception as e:
            raise Exception(f"{e}")
            
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

    def in_game_render(self,virtual_work, window_size, textbox = None):
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
        window_size = pygame.display.get_window_size()
        virtual_work = pygame.Surface(window_size)
        virtual_work = virtual_work.convert_alpha()

        # render the game process
        self.in_game_render(virtual_work, window_size, textbox)

        self.screen.blit(virtual_work, (0,0)) 
        # we need update in everymoment...
        pygame.display.update()

    def new_screen_context(self, size, flags):
        self.screen = pygame.display.set_mode(size, flags, 32, vsync=1)
        self.needs_update = True
    
    def handle_events(self):
     
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
        self.display_info = pygame.display.Info()

        self.monitor_size = (self.display_info.current_w, self.display_info.current_h)

        Log(f'desktop size: {self.monitor_size}')
 
        if not self.show_window:
            self.new_screen_context(self.default_screen_size, self.pygame_flags)

            pygame.display.set_caption(f"VNEngine - {version}{prefix_version}")
            if os.path.exists(os.path.join(base_folder, 'icon.png')):
                pygame.display.set_icon(pygame.image.load(os.path.join(base_folder, 'icon.png')))
                Log("game icon was loaded")

       
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            self.show_window = True
        
        Log(f'video mode size: ({pygame.display.Info().current_w},{pygame.display.Info().current_h})')
  
        try:
            # Initialice the textbox here, because in the loop has bugs!
            textbox = TextBox(30, self.typing_speed, self.char_index)
            
            while self.running:
                self.handle_events()
                self.render(textbox)

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
    
    def run_for_console(self):
        """Run the visual novel script."""
        self.load_script()
        while self.current_line < len(self.script):
            line = self.script[self.current_line]
            self.parse_line(line)
            self.current_line += 1

def Log(log):
    
    with open('log.txt', 'a+') as f:
        f.write("\n")
        f.write(log)
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
        
        
