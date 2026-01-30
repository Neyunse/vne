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
from vne.style_manager import StyleManager
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
        # If surface is not a valid pygame Surface, skip rendering
        try:
            if surface is None:
                return
            # quick duck-typing check
            if not hasattr(surface, 'get_width'):
                return
        except Exception:
            return

        for screen in sorted(self.screens, key=lambda e: getattr(e, 'z_index', 0)):
            try:
                screen.render(surface)
            except Exception as e:
                # Prevent a single screen from breaking the whole render loop.
                try:
                    import pygame as _pg
                    if isinstance(e, _pg.error):
                        # Common case: Surface not initialized or video system down
                        continue
                except Exception:
                    pass
                # For other exceptions, log to engine log if possible
                except Exception:
                    pass
        
        # UI Debugging view
        if getattr(self, 'debug_ui', False):
            for screen in self.screens:
                self._render_debug_info(screen, surface)

    def _render_debug_info(self, element, surface):
        abs_x, abs_y = element.get_absolute_position()
        rect = pygame.Rect(abs_x, abs_y, element.width, element.height)
        pygame.draw.rect(surface, (255, 0, 0), rect, 1)
        
        for child in element.children:
            self._render_debug_info(child, surface)

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

        # UI Overhaul Additions
        self.history = [] # FIFO buffer for dialogue
        self.preferences = {
            "music_volume": 0.8,
            "sfx_volume": 1.0,
            "text_speed": 30,
            "auto_forward_mode": False,
            "skip_unread": False
        }
        self.load_settings()
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
        self.style_manager = StyleManager()
        self.renderer = Renderer(self)
        self.clock = pygame.time.Clock()
 
        self.current_choice_buttons = []

        self.current_dialogue = ""
        self.current_character_name = ""
        self.sprite_layers = {}
        # Identificador del script actualmente cargado para soporte de hot-reload avanzado
        self.current_script_id = None
        self.Log(f"Starting the game from {self.game_path}...")

        self.screen_manager = ScreenManager()
        self.theme = None
        self.audio_volume = 1.0
        self.audio_muted = False
        self.force_clear_sprites = False
        # Flag para solicitar un hot-reload seguro fuera de loops bloqueantes (ej: typewriter)
        self.pending_reload = False
        self.awaiting_input = False
        self.current_dialog_panel = None
        self.screen_definitions = {}
        self.debug_ui = False # Toggle with F12
    
    def should_execute_line(self):
        """
        Returns True if all conditions are True, or if there are no active conditions.
        """
        if not self.condition_stack:
            return True
        return all(self.condition_stack)
    
         
    def add_to_history(self, name, text):
        """Adds a line of dialogue to the history buffer."""
        from datetime import datetime
        self.history.append({"name": name, "text": text, "timestamp": datetime.now().isoformat()})
        if len(self.history) > 100:
            self.history.pop(0)

    def load_settings(self):
        """Loads engine preferences from settings.json."""
        import json
        settings_path = os.path.join(self.game_path, "settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as f:
                    self.preferences.update(json.load(f))
            except:
                self.Log("[settings] Failed to load settings.json")

    def save_settings(self):
        """Saves current preferences to settings.json."""
        import json
        settings_path = os.path.join(self.game_path, "settings.json")
        try:
            with open(settings_path, "w") as f:
                json.dump(self.preferences, f, indent=4)
        except:
            self.Log("[settings] Failed to save settings.json")

    def setup_audio_volumes(self):
        """Applies preferences to the audio system."""
        # This will be called when volumes change
        try:
            # Simple volume sync for now
            pygame.mixer.music.set_volume(self.preferences.get("music_volume", 0.8))
        except:
            pass

    def Log(self, log, _=None):
        """
        The function `Log` appends a log message to the log file and prints to console.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {log}\n"
        
        # In devMode we prioritize visibility
        if self.devMode:
            print(log_message, end='')

        log_path = os.path.join(self.game_path, 'log.txt')
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(log_message)
        except Exception:
            pass # Avoid crashing due to log errors
    
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
            
            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F12:
                        self.debug_ui = not self.debug_ui
                        self.Log(f"[dev] Debug UI {'Enabled' if self.debug_ui else 'Disabled'}")
                    
                    # Hot-reload shortcut (Ctrl+R)
                    if event.key == pygame.K_r and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                         self.Log("[dev] Hot-reload requested via Ctrl+R")
                         self.pending_reload = True

                handled_by_ui = self.screen_manager.handle_event(event)
                handled = False
                if self.awaiting_input and self.running:
                    # Dialogue/Input specific handling
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        handled = self.screen_manager.handle_event(event)
                        if not handled:
                            # If no UI screen handled it, check for dialogue advance
                            menu_active = (getattr(self, 'current_menu_panel', None) in self.screen_manager.screens or 
                                           getattr(self, 'quick_menu_panel', None) in self.screen_manager.screens)
                            if not menu_active:
                                if self.current_dialog_panel:
                                    if not self.current_dialog_panel.finished_typewriter:
                                        self.current_dialog_panel.finish_typewriter()
                                        handled = True
                                    else:
                                        self.awaiting_input = False
                                        handled = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z): # Z is common in VN
                            # Check if a menu is blocking dialogue advance
                            menu_active = (getattr(self, 'current_menu_panel', None) in self.screen_manager.screens or 
                                           getattr(self, 'quick_menu_panel', None) in self.screen_manager.screens)
                            if not menu_active:
                                if self.current_dialog_panel:
                                    if not self.current_dialog_panel.finished_typewriter:
                                        self.current_dialog_panel.finish_typewriter()
                                        handled = True
                                    else:
                                        self.awaiting_input = False
                                        handled = True
                
                # General UI event handling (if not already handled by dialogue logic)
                if not handled and self.running:
                    self.screen_manager.handle_event(event)

            # 2. Hot-reload handling
            if getattr(self, 'pending_reload', False):
                try:
                    self.event_manager.handle("@reload", self)
                except Exception as e:
                    self.generate_traceback(e)
                finally:
                    self.pending_reload = False
                continue

            # 3. Command Execution (only if not waiting for input/reload)
            if not self.awaiting_input and self.running:
                command = self.lexer.get_next_command()
                if command is None:
                    # End of script. 
                    # If we have screens active (like a menu), we just wait.
                    # If no screens are active, then we can exit.
                    if not self.screen_manager.screens:
                        pygame.time.wait(1000)
                        self.running = False
                    else:
                        # Stay idle, waiting for UI events
                        self.awaiting_input = True
                else:
                    try:
                        self.event_manager.handle(command, self)
                    except Exception as e:
                        self.generate_traceback(e)
  
          
            # 4. Rendering
            if self.running:
                self.renderer.screen.fill((0,0,0)) # Clear screen
                self.screen_manager.render(self.renderer.screen)
                pygame.display.update()
        pygame.quit()
        self.Log("Game finished.")