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
 
        self.font = pygame.font.SysFont(CONFIG.get("font_name", "Arial"), CONFIG.get("font_size", 24))
        
        self.name_font = pygame.font.SysFont(CONFIG.get("name_font", "Arial"), CONFIG.get("name_font_size", 20))

        self.fps_font = pygame.font.SysFont(CONFIG.get("name_font", "Arial"), 13)
    
    def draw_background(self):
        """
        The function `draw_background` in Python checks if there is a current background image and
        displays it on the screen, otherwise it fills the screen with a specified background color.
        """
        if self.engine.current_bg:
            self.screen.blit(self.engine.current_bg, (0, 0))
        else:
            self.screen.fill(CONFIG.get("bg_color", (0, 0, 0)))
    
    def draw_dialogue(self):
        """
        The function `draw_dialogue` in Python draws a dialogue box on the screen with text rendered
        inside it.
        """
        if self.engine.current_dialogue:
        
            rect_cfg = CONFIG.get("dialogue_rect", {
                "x": 50,
                "y": CONFIG.get("screen_height", 600) - 150,
                "width": CONFIG.get("screen_width", 800) - 100,
                "height": 100,
 
               
            })
            dialogue_rect = pygame.Rect(rect_cfg["x"], rect_cfg["y"], rect_cfg["width"], rect_cfg["height"])
            pygame.draw.rect(self.screen, rect_cfg["bg_color"], dialogue_rect)

            text_surface = self.font.render(self.engine.current_dialogue, True, (255, 255, 255))
            self.screen.blit(text_surface, (dialogue_rect.x + 10, dialogue_rect.y + 10))
    
    def draw_character_name(self):
        """
        This function draws the current character's name on the screen within a specified rectangular
        box.
        """
        if self.engine.current_character_name:

            namebox_cfg = CONFIG.get("namebox_rect", {
                "x": 50,
                "y": CONFIG.get("screen_height", 600) - 210,  
                "width": 200,
                "height": 40
            })
            namebox_rect = pygame.Rect(namebox_cfg["x"], namebox_cfg["y"], namebox_cfg["width"], namebox_cfg["height"])
            pygame.draw.rect(self.screen, namebox_cfg["bg_color"], namebox_rect)
       
            name_surface = self.name_font.render(self.engine.current_character_name, True, (255, 255, 255))
            self.screen.blit(name_surface, (namebox_rect.x + 10, namebox_rect.y + 10))
    
    def draw_sprites(self):
        """
        This function draws scaled sprites on the screen based on their position.
        """
        if hasattr(self.engine, "sprites"):
            for alias, sprite_data in self.engine.sprites.items():
                image = sprite_data["image"]
                position = sprite_data["position"]

                sprite_scale = CONFIG.get("sprite_scale", 0.5)
                desired_width = int(CONFIG["screen_width"] * sprite_scale)
           
                scale_factor = desired_width / image.get_width()
                new_width = desired_width
                new_height = int(image.get_height() * scale_factor)
                scaled_image = pygame.transform.smoothscale(image, (new_width, new_height))
            
                if position == "left":
                    x = 3
                elif position == "right":
                    x = CONFIG["screen_width"] - new_width - 3
                else: 
                    x = (CONFIG["screen_width"] - new_width) // 2
             
                y = (CONFIG["screen_height"] - new_height) // 2
                
                self.screen.blit(scaled_image, (x, y))
    
    def render(self):
        """
        The `render` function in Python renders various elements of a game screen and displays the
        frames per second if in developer mode.
        """
        self.draw_background()
        self.draw_sprites()
        self.draw_character_name()
        self.draw_dialogue()
        self.clock.tick()
        self.fps = int(self.clock.get_fps())

        if self.engine.devMode:
            counter_surface = self.fps_font.render(f"{self.fps}", True, (0, 0, 0))
            self.screen.blit(counter_surface, (2, 2))
        
        pygame.display.flip()
 