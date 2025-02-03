# engine/vne/renderer.py
import pygame
from vne.config import CONFIG

class Renderer:
    def __init__(self, engine):
        pygame.init()
        self.engine = engine
        self.screen = pygame.display.set_mode((CONFIG["screen_width"], CONFIG["screen_height"]))
        pygame.display.set_caption("Visual Novel Engine")
        self.font = pygame.font.SysFont(CONFIG.get("font_name", "Arial"), CONFIG.get("font_size", 24))
    
    def draw_background(self):
        if self.engine.current_bg:
            self.screen.blit(self.engine.current_bg, (0, 0))
        else:
            self.screen.fill(CONFIG.get("bg_color", (0, 0, 0)))
    
    def draw_dialogue(self):
        if self.engine.current_dialogue:
            rect_cfg = CONFIG["dialogue_rect"]
            dialogue_rect = pygame.Rect(rect_cfg["x"], rect_cfg["y"], rect_cfg["width"], rect_cfg["height"])
            pygame.draw.rect(self.screen, rect_cfg["bg_color"], dialogue_rect)
            pygame.draw.rect(self.screen, rect_cfg["border_color"], dialogue_rect, 2)
            text_surface = self.font.render(self.engine.current_dialogue, True, (255, 255, 255))
            self.screen.blit(text_surface, (dialogue_rect.x + 10, dialogue_rect.y + 10))
    
    def draw_menu(self):
        # El menú se dibuja a través del gui_manager de pygame_gui.
        pass
    
    def render(self):
        self.draw_background()
        self.draw_dialogue()
        pygame.display.flip()
