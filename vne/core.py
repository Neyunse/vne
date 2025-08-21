import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import platform
from datetime import datetime
from vne.lexer import ScriptLexer
from vne.renderer import Renderer
from vne.events import EventManager
from vne.config import CONFIG
from vne.config import key, engine_version, file_extension, aes_extension, init_file
from vne.rm import ResourceManager
from vne.aes import AES, SaveCorruptError, SCRIPT_AAD
from vne.visual import VisualElement, MenuPanel, Button, VerticalLayout

class ScreenManager:
    def __init__(self, modal=False):
        self.screens = []
        self.modal = modal
        self.z_index = 0
    def show(self, screen, force_top=True):
        if screen in self.screens:
            self.screens.remove(screen)
  
        if force_top:
            self.screens.append(screen)
        else:
            self.screens.insert(0, screen)
    def hide(self, screen):
        if screen in self.screens:
            self.screens.remove(screen) 
    def hide_all(self):
        """
        Hides and removes all screens from the manager.
        """
        for screen in self.screens[:]: 
            self.hide(screen)
            
    def render(self, surface):
        for screen in sorted(self.screens, key=lambda e: getattr(e, 'z_index', 0)):
            screen.render(surface)
    def handle_event(self, event):
        for screen in reversed(self.screens):
            handled = screen.handle_event(event)
            if handled:
                # Si la pantalla es modal, no dejar pasar el evento a otras pantallas
                if getattr(screen, 'modal', False):
                    return True
                # Si la pantalla no es modal pero manejó el evento, puede dejar pasar o no según necesidad
                return True
            # Si la pantalla es modal pero no manejó el evento, igualmente bloqueamos el evento para otras pantallas
            if getattr(screen, 'modal', False):
                # Modal que no manejó evento, bloqueamos para pantallas debajo
                return True
        return False

class VNEngine:
    def __init__(self, game_path, devMode=False):
        self.game_path = game_path
        self.running = True
        self.current_bg = None
        self.sprites = {}
        self.current_dialogue = ""
        self.current_menu = None
        self.menu_selection = 0
        self.loaded_files = {}
        self.characters = {}
        self.scenes = {}
        self.vars = {}
        self.config = CONFIG
        self.devMode = devMode
        self.checkpoints = {}
        self.condition_stack = []
        self.current_menu_buttons = []
        self.quick_menu_buttons = []
        self.current_bgm = None
        self.current_bg_filename = None
        self.current_bgm_filename = None
        self.quick_menu_panel = None
        self.current_bg_visual = None
        self.bg_layer = None
        self.resource_manager = ResourceManager(self.game_path, self.Log)
        self.lexer = ScriptLexer(self.game_path, self)
        self.event_manager = EventManager()
        self.renderer = Renderer(self)
        self.clock = pygame.time.Clock()
 
        self.current_choice_buttons = []

        self.current_dialogue = ""
        self.current_character_name = ""
        self.sprite_layers = {}

        self.Log(f"Starting the game from {self.game_path}...")
    
        self.screen_manager = ScreenManager()
        self.theme = None
        self.audio_volume = 1.0
        self.audio_muted = False
        self.force_clear_sprites = False
    
    def should_execute_line(self):
        """
        Returns True if all conditions are True, or if there are no active conditions.
        """
        if not self.condition_stack:
            return True
        return all(self.condition_stack)
    
         
    def Log(self, log, _=None):
        """
        The function `Log` appends a log message to a file named 'log.txt'.
        
        :param log: The `Log` function takes a parameter `log`, which is a string representing the log
        message that you want to write to a file named `log.txt`. The function appends the log message to
        the file
        """
        log_path = os.path.join(self.game_path, 'log.txt')
        
        with open(log_path, 'a+') as f:
            f.write("\n")
            f.write(log)
            f.close()
    
    def set_theme(self, theme):
        self.theme = theme
    def set_audio_volume(self, volume):
        self.audio_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.audio_volume)
    def mute_audio(self):
        self.audio_muted = True
        pygame.mixer.music.set_volume(0.0)
    def unmute_audio(self):
        self.audio_muted = False
        pygame.mixer.music.set_volume(self.audio_volume)
    def fade_audio(self, to_volume, duration=1000):
        pygame.mixer.music.fadeout(duration)
        self.audio_volume = to_volume
        pygame.mixer.music.set_volume(self.audio_volume)
    
    def window_icon(self):
        """
        Loads and stores a sprite image with a specified alias and position.
        """
        load_image = self.lexer.load_image
        relative_path = os.path.join("ui", "icon", "window_icon" + ".png")
        try:
            image_bytes = self.resource_manager.get_bytes(relative_path)

            if image_bytes:
                icon = load_image(relative_path)

                return icon
             
            return None
        except Exception as e:
            pass
    def generate_traceback(self, e):
        self.running = False # Crash the game 
        traceback_template = '''Exception error:
  %(message)s\n
  
  created %(createdAt)s
  %(plataform)s
  VNE %(engineVersion)s
  '''
        self.Log(f"[Exception] Script was failed. Check the traceback.txt file for more information.")
        
        traceback_details = {
            'plataform': f"{platform.system()}-{platform.version()}",
            'engineVersion': engine_version,
            'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            
            'message' : e,
        }
        
        print(traceback_template % traceback_details)

        trace_path = os.path.join(self.game_path, 'traceback.txt')


        with open(trace_path, 'w') as f:
            f.write(traceback_template % traceback_details)
            f.close()
    def run(self):
        """
        This Python function runs a game by loading a script, handling events, and updating the display
        until the game is exited.
        :return: If the script reaches the end of the `run` method without encountering any errors, it
        will return `None`.
        """

        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        
     
        self.Log("Running game. Close the window to exit.") 

        init_log_template = """created at: %(createdAt)s
Plataform: %(plataform)s
VNE %(engineVersion)s
"""
        init_log_template_data = {
            'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'plataform': f"{platform.system()}-{platform.version()}",
            'engineVersion': engine_version 
        }

        log_path = os.path.join(self.game_path, 'log.txt')

        with open(log_path, 'w') as f:
            f.write(init_log_template % init_log_template_data)
            pass

        candidates = [
            f"{init_file}{aes_extension}",
            f"{init_file}{file_extension}"
        ]
        content = None

        self.vars["continue"] = "false"
        
 
        for candidate in candidates:
            data_bytes = self.resource_manager.get_bytes(candidate)
            
            if candidate.endswith(aes_extension):
                try:
                    # Si usas hex/base64, pasa encoded='hex' o 'base64'
                    content = AES(key).decrypt(data_bytes, aad=SCRIPT_AAD).decode("utf-8", errors="replace")
                except SaveCorruptError:
                    raise Exception(f"[VNEngine] Corrupted script or invalid key: {candidate}")
            else:
                content = data_bytes

        if content is None:
            self.Log("[VNEngine] Startup script not found. Exiting.")
            self.running = False
            return
        
        self.renderer.initialize()
 
        while self.running:
            delta_time = self.clock.tick(30) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.screen_manager.handle_event(event)
            command = self.lexer.get_next_command()
            if command is None:
                pygame.time.wait(2000)
                self.running = False
            else:
                try:
                    self.event_manager.handle(command, self)
                except Exception as e:
                    
                    self.generate_traceback(e)
  
          
            # Render overlays and stacking
            self.screen_manager.render(self.renderer.screen)
            pygame.display.update()
        pygame.quit()
        self.Log("Game finished.")
