# engine/vne/core.py
import os
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
        
        self.resource_manager = ResourceManager(self.game_path)
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
        """
        Método run que mantiene la ventana activa y procesa eventos utilizando el bucle
        que ya te funciona. Aquí se integra el proceso de lectura del script de inicio (startup).
        """
        print("Ejecutando juego. Cierre la ventana para salir.")
        # Intentar cargar el script de inicio. Se buscan en la carpeta raíz o en scenes/
        candidates = [
            "startup.kagc",
            "startup.kag",
            os.path.join("scenes", "startup.kagc"),
            os.path.join("scenes", "startup.kag")
        ]
        content = None
       
        # Buscamos el primer candidato que se encuentre.
        for candidate in candidates:
            try:
                data_bytes = self.resource_manager.get_bytes(candidate)
                if candidate.endswith(".kagc"):
                    # Si es compilado, descifrarlo
                    plain_bytes = xor_data(data_bytes, key)
                    content = plain_bytes.decode("utf-8", errors="replace")
                else:
                    content = data_bytes.decode("utf-8", errors="replace")
                print(f"[VNEngine] Script de inicio cargado: {candidate}")
                break
            except FileNotFoundError:
                continue

        if content is None:
            print("[VNEngine] No se encontró el script de inicio (startup). Saliendo.")
            self.running = False
            return
        # Bucle principal (basado en tu versión que funciona)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # Procesar eventos de gui_manager si se usa (omitido aquí)
            command = self.lexer.get_next_command()
            if command is None:
                pygame.time.wait(2000)
                self.running = False
            else:
                try:
                    # Se procesaría el comando (por ejemplo, con event_manager.handle())
                    self.event_manager.handle(command, self)
                    pass
                except Exception as e:
                    print(e)
                    self.running = False
            time_delta = self.clock.tick(60) / 1000.0
            # Si usas gui_manager y renderer, se actualizarían aquí.
            pygame.display.update()
        pygame.quit()
        print("Juego finalizado.")