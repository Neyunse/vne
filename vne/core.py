# engine/vne/core.py

import pygame
from vne.lexer import ScriptLexer
from vne.renderer import Renderer
from vne.events import EventManager
from vne.config import CONFIG

class VNEngine:
    def __init__(self, game_path):
        self.game_path = game_path
        self.running = True
        # Estados del juego
        self.current_bg = None
        self.current_dialogue = ""
        self.current_menu = None
        # Diccionarios para archivos cargados, personajes y escenas
        self.loaded_files = {}
        self.characters = {}
        self.scenes = {}   # Aquí se almacenarán las definiciones de escenas

        print(f"Iniciando el juego desde {self.game_path}...")
        self.load_game_resources()
        self.lexer = ScriptLexer(self.game_path)
        self.event_manager = EventManager()
        self.renderer = Renderer(self)
        self.clock = pygame.time.Clock()

    def load_game_resources(self):
        print("Cargando recursos del juego...")

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

    def wait_for_menu_selection(self):
        selection = None
        while selection is None and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                if event.type == pygame.KEYDOWN:
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        num = event.key - pygame.K_0
                        if num <= len(self.current_menu):
                            selection = num - 1
            self.renderer.render()
            self.clock.tick(30)
        return selection

    def run(self):
        print("Ejecutando juego. Cierre la ventana para salir.")
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            command = self.lexer.get_next_command()
            if command is None:
                pygame.time.wait(2000)
                self.running = False
            else:
                # Procesa el comando (ya sea con @ o con formato tradicional)
                self.event_manager.handle(command, self)
            self.renderer.render()
            self.clock.tick(30)
        pygame.quit()
        print("Juego finalizado.")

 