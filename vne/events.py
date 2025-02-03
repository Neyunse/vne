# engine/vne/events.py

import os
import pygame

class EventManager:
    def __init__(self):
        self.event_handlers = {}
        self.register_default_events()

    def register_default_events(self):
        self.register_event("inicio", self.handle_inicio)
        self.register_event("say", self.handle_say)
        self.register_event("menu", self.handle_menu)
        self.register_event("bg", self.handle_bg)
        self.register_event("exit", self.handle_exit)

    def register_event(self, event_name, handler):
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)

    def handle(self, command, engine=None):
        if ':' in command:
            event_name, arg = command.split(":", 1)
            self.dispatch(event_name.strip(), arg.strip(), engine)
        else:
            # Si no se especifica evento, se asume diálogo (say)
            self.dispatch("say", command.strip(), engine)

    def dispatch(self, event_name, arg, engine=None):
        handlers = self.event_handlers.get(event_name, [])
        if not handlers:
            print(f"[WARNING] No hay manejadores para el evento '{event_name}'.")
        for handler in handlers:
            handler(arg, engine)

    # Manejadores de eventos:

    def handle_inicio(self, arg, engine):
        print("Evento 'inicio':", arg)
        engine.current_dialogue = arg
        engine.wait_for_keypress()  # Espera a que el jugador presione una tecla
        engine.current_dialogue = ""

    def handle_say(self, arg, engine):
        # Se espera el formato "Personaje, diálogo" o solo diálogo.
        if ',' in arg:
            character, dialogue = arg.split(',', 1)
            full_text = f"{character.strip()}: {dialogue.strip()}"
        else:
            full_text = arg
        engine.current_dialogue = full_text
        engine.wait_for_keypress()
        engine.current_dialogue = ""

    def handle_menu(self, arg, engine):
        # Las opciones se separan con "|"
        options = [opt.strip() for opt in arg.split('|')]
        engine.current_menu = options
        engine.renderer.render()  # Dibuja el menú en pantalla
        selection = engine.wait_for_menu_selection()
        engine.current_menu = None
        if selection is not None and selection < len(options):
            print(f"Menú seleccionado: {selection + 1} - {options[selection]}")
        else:
            print("No se seleccionó opción válida.")

    def handle_bg(self, arg, engine):
        # Se espera que 'arg' sea el nombre (o ruta relativa) de la imagen de fondo.
        # Se buscará en: <game_path>/data/images/bg/
        bg_path = os.path.join(engine.game_path, "data", "images", "bg", arg)
        if os.path.exists(bg_path):
            try:
                image = pygame.image.load(bg_path)
                # Escalar la imagen al tamaño de la pantalla
                image = pygame.transform.scale(image, (engine.renderer.screen.get_width(),
                                                         engine.renderer.screen.get_height()))
                engine.current_bg = image
            except Exception as e:
                print("Error al cargar la imagen de fondo:", e)
        else:
            print("Imagen de fondo no encontrada:", bg_path)

    def handle_exit(self, arg, engine):
        print("Evento 'exit':", arg)
        engine.running = False
