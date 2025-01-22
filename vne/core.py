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
        self.renderer = None
        self.lexer = None
        self.interpreter = None

    def initialize(self):
        """Initialize the engine and set up pygame."""
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode(
            self.config.SCREEN_SIZE, self.config.PYGAME_FLAGS
        )
        pygame.display.set_caption(self.config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.lexer = Lexer(self.config)
        self.interpreter = Interpreter(self.lexer, self.renderer, self.config)

    def run(self, project_folder):
        """Main game loop with dialogue interaction."""
        self.config.base_game = os.path.abspath(project_folder)
        print(f"Base game path set to: {self.config.base_game}")

        startup_script = os.path.join(self.config.base_game, "data", "startup.kag")
        if not os.path.exists(startup_script):
            raise FileNotFoundError(f"startup.kag not found in {startup_script}")

        self.initialize()
        self.lexer.load(startup_script)

        dialogue_active = False
        dialogue_text = ""

        while self.running:
            self.screen.fill((0, 0, 0))  # Clear screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and dialogue_active:
                        dialogue_active = False  # Ready for the next command

            if not dialogue_active:
                # Execute the next command
                if not self.interpreter.execute_next_command():
                    self.running = False
                else:
                    command = self.lexer.get_current_state()
                    if command and command.startswith("dialogue"):
                        dialogue_active = True
                        dialogue_text = command.split("dialogue ", 1)[-1]

            # Render dialogue if active
            if dialogue_active:
                self.renderer.draw_dialogue_box(dialogue_text)

            pygame.display.flip()
            self.clock.tick(self.config.FPS)

        pygame.quit()

