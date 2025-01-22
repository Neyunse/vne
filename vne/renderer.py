import pygame

class Renderer:
    """
    Handles rendering of backgrounds, sprites, and dialogue for the Visual Novel Engine.
    """

    def __init__(self):
        self.background = None
        self.sprites = []

    def render(self, screen, current_state):
        """Render the current frame."""
        screen.fill((0, 0, 0))  # Black background

        # Render the background
        if self.background:
            screen.blit(self.background, (0, 0))

        # Render sprites
        for sprite, x, y in self.sprites:
            screen.blit(sprite, (x, y))

        # Render current state as text (basic for now)
        if current_state:
            font = pygame.font.Font(None, 36)
            text_surface = font.render(current_state, True, (255, 255, 255))
            screen.blit(text_surface, (50, 50))
