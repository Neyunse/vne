import pygame
import pygame_gui
from vne.lexer import ScriptLexer
from vne.renderer import Renderer
from vne.events import EventManager
from vne.config import CONFIG
from vne.config import key
from vne.rm import ResourceManager
from vne.xor_data import xor_data

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
        
        
        self.resource_manager = ResourceManager(self.game_path)
        self.lexer = ScriptLexer(self.game_path, self)
        self.event_manager = EventManager()
        self.renderer = Renderer(self)
        self.clock = pygame.time.Clock()

        self.current_dialogue = ""
        self.current_character_name = ""
        
        self.gui_manager = pygame_gui.UIManager((CONFIG["screen_width"], CONFIG["screen_height"]))


        print(f"Starting the game from {self.game_path}...")
    
    def wait_for_keypress(self):
        """
        The `wait_for_keypress` function in Python uses Pygame to wait for a keypress or mouse click
        while rendering and updating the display.
        :return: If the event type is pygame.QUIT, the method will set self.running to False and return.
        Otherwise, if the event type is pygame.MOUSEBUTTONDOWN, the method will set waiting to False. No
        explicit return value is provided in this code snippet.
        """
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                               
            self.renderer.render()
         
            
    
    def run(self):
        """
        This Python function runs a game by loading a script, handling events, and updating the display
        until the game is exited.
        :return: If the script reaches the end of the `run` method without encountering any errors, it
        will return `None`.
        """
     
        print("Running game. Close the window to exit.") 

        candidates = [
            "startup.kagc",
            "startup.kag"
        ]
        content = None
 
        for candidate in candidates:
            try:
                data_bytes = self.resource_manager.get_bytes(candidate)
                if candidate.endswith(".kagc"):
                    plain_bytes = xor_data(data_bytes, key)
                    content = plain_bytes.decode("utf-8", errors="replace")
                else:
                    content = data_bytes.decode("utf-8", errors="replace")
                print(f"[VNEngine] Startup script loaded: {candidate}")
                break
            except FileNotFoundError:
                continue

        if content is None:
            print("[VNEngine] Startup script not found. Exiting.")
            self.running = False
            return
 
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
               
            command = self.lexer.get_next_command()
            if command is None:
                pygame.time.wait(2000)
                self.running = False
            else:
                try:
                    self.event_manager.handle(command, self)
                    pass
                except Exception as e:
                    print(e)
                    self.running = False
  
          
            pygame.display.update()
        pygame.quit()
        print("Game finished.")
