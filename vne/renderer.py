# engine/vne/renderer.py

import pygame
from vne.config import CONFIG

class Renderer:
    def __init__(self, engine):
        pygame.init()
        self.engine = engine
        self.screen = pygame.display.set_mode(
            (CONFIG["screen_width"], CONFIG["screen_height"]))
        pygame.display.set_caption("Visual Novel Engine")
        self.font = pygame.font.SysFont(CONFIG.get("font_name", "Arial"),
                                        CONFIG.get("font_size", 24))

    def draw_background(self):
        if self.engine.current_bg:
            self.screen.blit(self.engine.current_bg, (0, 0))
        else:
            self.screen.fill(CONFIG.get("bg_color", (0, 0, 0)))

    def draw_dialogue(self):
        if self.engine.current_dialogue:
            rect_cfg = CONFIG["dialogue_rect"]
            dialogue_rect = pygame.Rect(rect_cfg["x"], rect_cfg["y"],
                                        rect_cfg["width"], rect_cfg["height"])
            pygame.draw.rect(self.screen, rect_cfg["bg_color"], dialogue_rect)
            pygame.draw.rect(self.screen, rect_cfg["border_color"], dialogue_rect, 2)
            text_surface = self.font.render(self.engine.current_dialogue, True, (255, 255, 255))
            self.screen.blit(text_surface, (dialogue_rect.x + 10, dialogue_rect.y + 10))

    def draw_menu(self):
        if self.engine.current_menu:
            menu_options = self.engine.current_menu
            menu_rect = pygame.Rect(100, 100, CONFIG["screen_width"] - 200, CONFIG["screen_height"] - 200)
            s = pygame.Surface((menu_rect.width, menu_rect.height), pygame.SRCALPHA)
            s.fill((80, 80, 80, 200))
            self.screen.blit(s, (menu_rect.x, menu_rect.y))
            pygame.draw.rect(self.screen, (255, 255, 255), menu_rect, 2)
            y = menu_rect.y + 20
            for idx, option in enumerate(menu_options):
                option_text = f"{idx + 1}. {option}"
                text_surface = self.font.render(option_text, True, (255, 255, 255))
                self.screen.blit(text_surface, (menu_rect.x + 20, y))
                y += 40

    def render(self):
        self.draw_background()
        self.draw_dialogue()
        self.draw_menu()
        pygame.display.flip()
