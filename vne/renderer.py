import pygame

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)  # Fuente predeterminada

    def draw_text(self, text, pos, color=(255, 255, 255)):
        """Render text on the screen."""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, pos)

    def draw_dialogue_box(self, text):
        """Draw a basic dialogue box with text."""
        pygame.draw.rect(self.screen, (0, 0, 0), (50, 500, 1180, 180))  # Box background
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 500, 1180, 180), 2)  # Box border
        self.draw_text(text, (70, 520))  # Draw text inside the box
