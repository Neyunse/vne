import os
import pygame
from vne.config import engine_version

class Renderer:
    def __init__(self, engine):
        os.environ["SDL_VIDEO_CENTERED"] = "1"

        self.engine = engine
        # Usar engine.config para obtener los valores actualizados de ancho y alto.
        self.screen = pygame.display.set_mode((
            self.engine.config.get("screen_width", 800), 
            self.engine.config.get("screen_height", 600)
        ), flags=pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.HIDDEN)
        self.clock = pygame.time.Clock()
        self.fps = 0

        pygame.display.set_caption(f"VNE {engine_version}")

        if self.window_icon():
            pygame.display.set_icon(self.window_icon())
            self.engine.Log("[window] game icon was loaded")
 
        self.font = None
        self.name_font = None
        self.fps_font = None
    
    def initialize(self):
        pygame.init()

        self.font = pygame.font.SysFont(
            self.engine.config.get("font_name", "Arial"), 
            self.engine.config.get("font_size", 24)
        )
        
        self.name_font = pygame.font.SysFont(
            self.engine.config.get("name_font", "Arial"), 
            self.engine.config.get("name_font_size", 20)
        )

        self.fps_font = pygame.font.SysFont(
            self.engine.config.get("name_font", "Arial"), 13
        )

    @classmethod
    def update_set_mode(cls, value):
        cls.screen = pygame.display.set_mode(value, flags=pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.flip()
    
    def window_icon(self):
        """
        Loads and stores a sprite image with a specified alias and position.
        """
        load_image = self.engine.lexer.load_image
        relative_path = os.path.join("ui", "icon", "window_icon" + ".png")
        try:
            image_bytes = self.engine.resource_manager.get_bytes(relative_path)

            if image_bytes:
                icon = load_image(relative_path)

                return icon
             
            return None
        except Exception as e:
            pass
 
