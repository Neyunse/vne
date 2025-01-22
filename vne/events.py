import pygame

class EventManager:
    """
    Handles events such as user input for the Visual Novel Engine.
    """

    def __init__(self):
        self.events = []

    def process_events(self):
        """Processes Pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            self.events.append(event)
