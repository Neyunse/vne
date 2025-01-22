import pygame

class Config:
    """
    Contains global configuration settings for the Visual Novel Engine.
    """

    def __init__(self):
        # Display settings
        self.SCREEN_SIZE = (1280, 720)
        self.FPS = 60
        self.PYGAME_FLAGS = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
        self.WINDOW_TITLE = "Visual Novel Engine"

        # Path settings
        self.base_game = ""
        self.TRACEBACK_FILE = "traceback.txt"  # File for error traceback

        self.WINDOW_ICON = "images/ui/window_icon.png"  # Icon for the game window



        # Debugging options
        self.DEBUG_MODE = True  # Enable or disable debug logs
        self.DEBUG_CONSOLE_OUTPUT = True  # Print logs to the console

        # Localization settings
        self.DEFAULT_LANGUAGE = "en"  # Default language for localization
        self.LOCALE_FOLDER = "data/i18n"  # Folder for localization files

    def log(self, message):
        """
        Logs a message to the log file and optionally to the console.
        """
        with open(self.LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"{message}\n")

        if self.DEBUG_CONSOLE_OUTPUT:
            print(message)
