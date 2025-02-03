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
        # Estados del juego:
        self.current_bg = None          # Imagen de fondo (Surface de Pygame)
        self.current_dialogue = ""      # Texto a mostrar en el recuadro de diálogo
        self.current_menu = None        # Lista de opciones (cuando se activa un menú)
        
        print(f"Iniciando el juego desde {self.game_path}...")
        self.load_game_resources()

        self.lexer = ScriptLexer(self.game_path)
        self.event_manager = EventManager()
        self.renderer = Renderer(self)
        self.clock = pygame.time.Clock()

    def load_game_resources(self):
        # Aquí podrías cargar sonidos, música u otros recursos globales
        print("Cargando recursos del juego...")

    def wait_for_keypress(self):
        """
        Pausa la ejecución hasta que el usuario presione una tecla.
        """
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
        """
        Espera a que el usuario presione una tecla numérica (1-9) correspondiente a una opción.
        Retorna el índice (0 basado) de la opción seleccionada.
        """
        selection = None
        while selection is None and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                if event.type == pygame.KEYDOWN:
                    # Se asume que las teclas numéricas del 1 al 9 se usan para seleccionar
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
            # Procesa eventos de Pygame (por ejemplo, cierre de ventana)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Obtiene el siguiente comando del script
            command = self.lexer.get_next_command()
            if command is None:
                # Si se han procesado todos los comandos, esperar unos segundos y salir
                pygame.time.wait(2000)
                self.running = False
            else:
                # Procesa el comando (se invocan los handlers correspondientes)
                self.event_manager.handle(command, self)
            
            self.renderer.render()
            self.clock.tick(30)
        pygame.quit()
        print("Juego finalizado.")