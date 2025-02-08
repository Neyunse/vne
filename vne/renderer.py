# engine/vne/renderer.py
import pygame
from vne.config import CONFIG

class Renderer:
    def __init__(self, engine):
        pygame.init()
        self.engine = engine
        self.screen = pygame.display.set_mode((CONFIG.get("screen_width", 800), CONFIG.get("screen_height", 600)))
        self.clock = pygame.time.Clock()
        self.fps = 0

        pygame.display.set_caption("Visual Novel Engine")
        # Fuente para el diálogo
        self.font = pygame.font.SysFont(CONFIG.get("font_name", "Arial"), CONFIG.get("font_size", 24))
        # Fuente para el nombre del personaje
        self.name_font = pygame.font.SysFont(CONFIG.get("name_font", "Arial"), CONFIG.get("name_font_size", 20))
    
    def draw_background(self):
        if self.engine.current_bg:
            self.screen.blit(self.engine.current_bg, (0, 0))
        else:
            self.screen.fill(CONFIG.get("bg_color", (0, 0, 0)))
    
    def draw_dialogue(self):
        if self.engine.current_dialogue:
            # Configuración de la caja de diálogo (usa CONFIG o valores por defecto)
            rect_cfg = CONFIG.get("dialogue_rect", {
                "x": 50,
                "y": CONFIG.get("screen_height", 600) - 150,
                "width": CONFIG.get("screen_width", 800) - 100,
                "height": 100,
 
               
            })
            dialogue_rect = pygame.Rect(rect_cfg["x"], rect_cfg["y"], rect_cfg["width"], rect_cfg["height"])
            pygame.draw.rect(self.screen, rect_cfg["bg_color"], dialogue_rect)
            #pygame.draw.rect(self.screen, rect_cfg["border_color"], dialogue_rect, 2)
            # Renderizar el texto del diálogo (se puede mejorar para que haga word wrap)
            text_surface = self.font.render(self.engine.current_dialogue, True, (255, 255, 255))
            self.screen.blit(text_surface, (dialogue_rect.x + 10, dialogue_rect.y + 10))
    
    def draw_character_name(self):
        if self.engine.current_character_name:
            # Configuración de la caja del nombre (usa CONFIG o valores por defecto)
            namebox_cfg = CONFIG.get("namebox_rect", {
                "x": 50,
                "y": CONFIG.get("screen_height", 600) - 210,  # Por encima de la caja de diálogo
                "width": 200,
                "height": 40
            })
            namebox_rect = pygame.Rect(namebox_cfg["x"], namebox_cfg["y"], namebox_cfg["width"], namebox_cfg["height"])
            pygame.draw.rect(self.screen, namebox_cfg["bg_color"], namebox_rect)
       
            # Renderizar el nombre del personaje
            name_surface = self.name_font.render(self.engine.current_character_name, True, (255, 255, 255))
            self.screen.blit(name_surface, (namebox_rect.x + 10, namebox_rect.y + 10))
    
    def draw_menu(self):
        # El menú se dibuja a través del gui_manager de pygame_gui u otro método.
        pass
    
    def render(self):
        self.draw_background()
        self.draw_character_name()
        self.draw_dialogue()
        self.clock.tick()
        self.fps = int(self.clock.get_fps())
        counter_surface = self.font.render(f"{self.fps}", True, (0, 0, 0))
        self.screen.blit(counter_surface, (0, 0))
        
        pygame.display.flip()
    
    def refresh(self):
        self.draw_background()
        self.draw_character_name()
        self.draw_dialogue()
        pygame.display.update()
        print("Refrescado...")
        