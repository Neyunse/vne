import os
import pygame

class Renderer:
    def __init__(self, engine):
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        self.engine = engine
        # Usar engine.config para obtener los valores actualizados de ancho y alto.
        self.screen = pygame.display.set_mode((
            self.engine.config.get("screen_width", 800), 
            self.engine.config.get("screen_height", 600)
        ))
        self.clock = pygame.time.Clock()
        self.fps = 0

        pygame.display.set_caption("Visual Novel Engine")
 
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
    
    def wrap_text(self, text, font, max_width):
        """
        Divides the text into lines, so that each line does not exceed max_width pixels,
        using the font size.
        """
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines
        

    def draw_background(self):
        if self.engine.current_bg:
            self.screen.blit(self.engine.current_bg, (0, 0))
        else:
            self.screen.fill(self.engine.config.get("bg_color", (0, 0, 0)))
    
    def draw_dialogue(self):
        if self.engine.current_dialogue:
            rect_cfg = self.engine.config.get("dialogue_rect", {
                "x": 0,
                "y": self.engine.config.get("screen_height", 600) - 150,
                "width": self.engine.config.get("screen_width", 800) - 100,
                "height": 100,
                "bg_color": (50, 50, 50),
                "border_color": (255, 255, 255)
            })
            dialogue_rect = pygame.Rect(rect_cfg["x"], rect_cfg["y"], rect_cfg["width"], rect_cfg["height"])
            pygame.draw.rect(self.screen, rect_cfg["bg_color"], dialogue_rect)
             
            
            margin = 10
            max_text_width = dialogue_rect.width - 2 * margin
            lines = self.wrap_text(self.engine.current_dialogue, self.font, max_text_width)
           
            y_offset = dialogue_rect.y + margin
            for line in lines:
                text_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (dialogue_rect.x + margin, y_offset))
                y_offset += self.font.get_height() + 2

    def draw_character_name(self):
        if self.engine.current_character_name:
            namebox_cfg = self.engine.config.get("namebox_rect", {
                "x": 50,
                "y": self.engine.config.get("screen_height", 600) - 210,
                "width": 200,
                "height": 40,
                "bg_color": (50, 50, 50),
                "border_color": (255, 255, 255)
            })
            namebox_rect = pygame.Rect(namebox_cfg["x"], namebox_cfg["y"], namebox_cfg["width"], namebox_cfg["height"])
            pygame.draw.rect(self.screen, namebox_cfg["bg_color"], namebox_rect)
            name_surface = self.name_font.render(self.engine.current_character_name, True, (255, 255, 255))
            self.screen.blit(name_surface, (namebox_rect.x + 10, namebox_rect.y + 10))
    
    def draw_sprites(self):
        if hasattr(self.engine, "sprites"):
            screen_width = self.engine.config.get("screen_width", 800)
            screen_height = self.engine.config.get("screen_height", 600)
            
           
            base_low = 800
            base_high = 1280
            default_scale = self.engine.config.get("sprite_scale", 0.5)
            high_scale = self.engine.config.get("sprite_scale_high", 0.40)
            if screen_width <= base_low:
                sprite_scale = default_scale
            elif screen_width >= base_high:
                sprite_scale = high_scale
            else:
                t = (screen_width - base_low) / (base_high - base_low)
                sprite_scale = default_scale + t * (high_scale - default_scale)
            
            for alias, sprite_data in self.engine.sprites.items():
                image = sprite_data["image"]
                position = sprite_data.get("position", "center")
                
                desired_width = int(screen_width * sprite_scale)
                scale_factor = desired_width / image.get_width()
                new_width = desired_width
                new_height = int(image.get_height() * scale_factor)
                zoom_factor = new_width / image.get_width()
                scaled_image = pygame.transform.rotozoom(image, 0, zoom_factor)
                
                if position.lower() == "left":
                    x = 3
                elif position.lower() == "right":
                    x = screen_width - new_width - 3
                else:
                    x = (screen_width - new_width) // 2

       
                y = sprite_data.get("y", (screen_height - new_height) // 2)
                
                self.screen.blit(scaled_image, (x, y))

    
    def render(self):
        self.draw_background()
        self.draw_sprites()
        self.draw_character_name()
        self.draw_dialogue()
        self.clock.tick(30)
        self.fps = int(self.clock.get_fps())

        if self.engine.devMode:
            counter_surface = self.fps_font.render(f"{self.fps}", True, (0, 0, 0))
            self.screen.blit(counter_surface, (2, 2))
        
        pygame.display.flip()
