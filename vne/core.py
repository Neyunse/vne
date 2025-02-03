# engine/vne/core.py
import os
import pygame
import pygame_gui
from vne.lexer import ScriptLexer
from vne.renderer import Renderer
from vne.events import EventManager
from vne.config import CONFIG
from vne.rm import ResourceManager

class VNEngine:
    def __init__(self, game_path):
        self.game_path = game_path
        self.running = True
        self.current_bg = None
        self.current_dialogue = ""
        self.current_menu = None
        self.menu_selection = 0
        self.loaded_files = {}
        self.characters = {}
        self.scenes = {}
        self.vars = {}
        self.config = CONFIG
        
        print(f"Iniciando el juego desde {self.game_path}...")
        self.load_game_resources()
        
        self.resource_manager = ResourceManager(data_folder=os.path.join(self.game_path, "data"), pkg_path="data.pkg")
        self.lexer = ScriptLexer(self.game_path, self)
        self.event_manager = EventManager()
        self.renderer = Renderer(self)
        self.clock = pygame.time.Clock()
        
        # Inicializar el UI Manager de pygame_gui.
        self.gui_manager = pygame_gui.UIManager((CONFIG["screen_width"], CONFIG["screen_height"]))
    
    def load_game_resources(self):
        print("Cargando recursos del juego...")
        # Aquí se pueden cargar otros recursos globales si se desea.
    
    def wait_for_keypress(self):
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    waiting = False
            self.renderer.render()
            self.clock.tick(30)
    
    def run(self):
        print("Ejecutando juego. Cierre la ventana para salir.")
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.gui_manager.process_events(event)
            command = self.lexer.get_next_command()
            if command is None:
                pygame.time.wait(2000)
                self.running = False
            else:
                try:
                    self.event_manager.handle(command, self)
                except Exception as e:
                    print(e)
                    self.running = False
            time_delta = self.clock.tick(60) / 1000.0
            self.gui_manager.update(time_delta)
            self.renderer.render()
            self.gui_manager.draw_ui(self.renderer.screen)
            pygame.display.update()
        pygame.quit()
        print("Juego finalizado.")