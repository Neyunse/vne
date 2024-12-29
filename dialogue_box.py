# Copyright 2024 Neyunse
#
# VNengine is licensed under Creative Commons Attribution-NoDerivatives 4.0 International. 
# To view a copy of this license, visit https://creativecommons.org/licenses/by-nd/4.0/
import pygame

class DialogueBox:
    def __init__(self, font_size=30, typing_speed=50, char_index=0):
        self.font_size = font_size
        self.font = pygame.font.Font(None, self.font_size)
        self.namebox_font = pygame.font.Font(None, self.font_size)
        self.typing_speed = typing_speed
        self.last_update_time = pygame.time.get_ticks()
        self.char_index = 0
        self.last_text = "" 

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def typewriter_effect(self, text):
       
        if text != self.last_text:
            self.char_index = 0  
            self.last_text = text 

        current_time = pygame.time.get_ticks()

        if current_time - self.last_update_time >= self.typing_speed and self.char_index < len(text):
            self.char_index += 1
            self.last_update_time = current_time
        
        
        return text[:self.char_index]

    def draw_dialogue_box(self,
                          surface,
                          text, 
                          character_name, 
                          box_color=(0, 0, 0, 128), 
                          text_color=(255, 255, 255),
                          box_height=150,
                          padding=10,
                          position="bottom", 
                          xpos=0.0
                        ):
        window_width, window_height = surface.get_size()

        if position == "bottom":
            box_y = window_height - box_height
            namebox_y = box_y - 30
        elif position == "top":
            box_y = 30
            namebox_y = 0
        elif position == "center":
            box_y = (window_height - box_height) // 2
            namebox_y = box_y - 30
        else:
            raise ValueError("Invalid position: Use 'top', 'bottom' or 'center'.")

        box_rect = pygame.Rect(0, box_y, window_width, box_height)
        box_surface = pygame.Surface((window_width, box_height), pygame.SRCALPHA)
        box_surface.fill(box_color)
        surface.blit(box_surface, (0, box_y))

        name_surface = self.namebox_font.render(character_name, True, text_color)
        namebox_width = max(100, min(name_surface.get_rect().width * padding // (padding - 1), 520))
        namebox_height = 30
        
        namebox_surface = pygame.Surface((namebox_width, namebox_height), pygame.SRCALPHA)
        namebox_surface.fill(box_color)

        if character_name:
            surface.blit(namebox_surface, (0, namebox_y))

        name_x = (namebox_width - name_surface.get_width()) // 2
        if character_name:
            surface.blit(name_surface, (name_x, namebox_y + (namebox_height - name_surface.get_height()) // 2))

        text_area_width = box_rect.width - 2 * padding
        current_text = self.typewriter_effect(text)
        wrapped_lines = self.wrap_text(current_text, self.font, text_area_width)

        text_x_offset = int((box_rect.width - text_area_width) * xpos)

        current_y = box_rect.y + padding
        for line in wrapped_lines:
            text_surface = self.font.render(line, True, text_color)
            surface.blit(text_surface, (box_rect.x + padding + text_x_offset, current_y))
            current_y += self.font.get_height()

            if current_y > box_rect.y + box_rect.height:
                break
        

# USAGE EXAMPLE
# dialogue = DialogueBox(screen, char_index=char_index, typing_speed=typing_speed)
# dialogue.draw_dialogue_box(
    #     text=long_text,
    #     character_name="MIKI",
    # )
