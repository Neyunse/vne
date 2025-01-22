import os
import pygame
from .config import Config
from .lexer import Lexer
from .events import EventManager
from .renderer import Renderer
from .Interpreter import Interpreter

class VNEngine:
    """
    Core class for the Visual Novel Engine.
    Handles game initialization, script execution, and interaction coordination.
    """

    def __init__(self):
        self.config = Config()
        self.running = True
        self.screen = None
        self.clock = None
        self.event_manager = EventManager()
        self.renderer = Renderer()
        self.lexer = Lexer(self.config)
        self.interpreter = Interpreter(self.lexer, self.renderer, self.config)

    def initialize(self):
        """Initialize the engine and set up pygame."""
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode(
            self.config.SCREEN_SIZE, self.config.PYGAME_FLAGS
        )
        pygame.display.set_caption(self.config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()

    def run(self, project_folder):
        """Main game loop."""
        self.config.base_game = os.path.abspath(project_folder)
        print(f"Base game path set to: {self.config.base_game}")  # Debug

        startup_script = os.path.join(self.config.base_game, "data", "startup.kag")

        # Verify if the startup.kag file exists
        if not os.path.exists(startup_script):
            raise FileNotFoundError(f"startup.kag not found in {startup_script}")

        self.initialize()

        # Load the initial script
        self.lexer.load(startup_script)

        while self.running:
            self.event_manager.process_events()

            # Delegate command execution to the interpreter
            if not self.interpreter.execute_next_command():
                self.running = False

            pygame.display.flip()
            self.clock.tick(self.config.FPS)