import os
import pygame
from vne.config import engine_version

class Renderer:
    def __init__(self, engine):
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        self.engine = engine
        self.screen = pygame.display.set_mode((
            self.engine.config.get("screen_width", 800), 
            self.engine.config.get("screen_height", 600)
        ), flags=pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.HIDDEN)
        self.clock = pygame.time.Clock()
        
        pygame.display.set_caption(f"VNE {engine_version}")
        icon = self.window_icon()
        if icon:
            pygame.display.set_icon(icon)

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
        self.fps_font = pygame.font.SysFont("Arial", 13)
        
        # Sync with global theme
        from vne.visual import global_theme
        global_theme.font = self.font

    def window_icon(self):
        relative_path = os.path.join("ui", "icon", "window_icon.png")
        try:
            image_bytes = self.engine.resource_manager.get_bytes(relative_path)
            if image_bytes:
                import io
                return pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
        except:
            pass
        return None

    def render(self):
        pygame.display.flip()

    def update_set_mode(self, value):
        """Updates the screen mode (window size)."""
        self.screen = pygame.display.set_mode(value, flags=pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.flip()
