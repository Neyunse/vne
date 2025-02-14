import pygame
from vne.lexer import ScriptLexer
from vne.renderer import Renderer
from vne.events import EventManager
from vne.config import CONFIG
from vne.config import key
from vne.rm import ResourceManager
from vne.xor_data import xor_data
from datetime import datetime
import os
import platform
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
        self.typewriter_index = 0
        
        
        self.resource_manager = ResourceManager(self.game_path, self.Log)
        self.lexer = ScriptLexer(self.game_path, self)
        self.event_manager = EventManager()
        self.renderer = Renderer(self)
        self.clock = pygame.time.Clock()

        self.current_dialogue = ""
        self.current_character_name = ""

        self.Log(f"Starting the game from {self.game_path}...")
    
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
    
    def run(self):
        """
        This Python function runs a game by loading a script, handling events, and updating the display
        until the game is exited.
        :return: If the script reaches the end of the `run` method without encountering any errors, it
        will return `None`.
        """
     
        self.Log("Running game. Close the window to exit.") 

        init_log_template = """created at: %(createdAt)s
Plataform: %(plataform)s
"""
        init_log_template_data = {
            'createdAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'plataform': f"{platform.system()}-{platform.version()}",
         
        }

        log_path = os.path.join(self.game_path, 'log.txt')

        with open(log_path, 'w') as f:
            f.write(init_log_template % init_log_template_data)
            pass

        candidates = [
            "startup.kagc",
            "startup.kag"
        ]
        content = None

        self.vars["continue"] = "false"
        
 
        for candidate in candidates:
            try:
                data_bytes = self.resource_manager.get_bytes(candidate)
                if candidate.endswith(".kagc"):
                    plain_bytes = xor_data(data_bytes, key)
                    content = plain_bytes.decode("utf-8", errors="replace")
                else:
                    content = data_bytes.decode("utf-8", errors="replace")
                self.Log(f"[VNEngine] Startup script loaded: {candidate}")
                break
            except FileNotFoundError:
                continue

        if content is None:
            self.Log("[VNEngine] Startup script not found. Exiting.")
            self.running = False
            return
        pygame.mixer.init()
        
        while self.running:
            delta_time = self.clock.tick(30) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.typewriter_index += int(delta_time * 20)
            command = self.lexer.get_next_command()
            if command is None:
                pygame.time.wait(2000)
                self.running = False
            else:
                try:
                    self.event_manager.handle(command, self)
                    pass
                except Exception as e:
                    self.running = False
                    traceback_template = '''Exception error:
  %(message)s\n

  %(plataform)s
  '''
                    self.Log(f"[Exception] Script was failed. Check the traceback.txt file for more information.")
                    
                    traceback_details = {
                        'message' : e,
                        'plataform': f"{platform.system()}-{platform.version()}"
                    }
                    
                    print(traceback_template % traceback_details)

                    trace_path = os.path.join(self.game_path, 'traceback.txt')


                    with open(trace_path, 'w') as f:
                        f.write(traceback_template % traceback_details)
                        f.close()
  
          
            pygame.display.update()
        pygame.quit()
        self.Log("Game finished.")
