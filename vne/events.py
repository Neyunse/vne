import os
import pygame
import re

class EventManager:
    def __init__(self):
        self.event_handlers = {}
        self.register_default_events()

    def register_default_events(self):
        # Eventos “clásicos”
        self.register_event("inicio", self.handle_inicio)
        self.register_event("say", self.handle_say)
        self.register_event("menu", self.handle_menu)
        self.register_event("bg", self.handle_bg)
        self.register_event("exit", self.handle_exit)
        # Nuevos comandos especiales (prefijados con @)
        self.register_event("Load", self.handle_Load)
        self.register_event("process_scene", self.handle_process_scene)
        self.register_event("char", self.handle_char)
        # Nuevo: definición de escenas (desde system/scenes.kag)
        self.register_event("scene", self.handle_scene)

    def register_event(self, event_name, handler):
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)

    def handle(self, command, engine=None):
        command = command.strip()
        # Si comienza con @, es un comando especial
        if command.startswith("@"):
            stripped = command[1:].strip()
            match = re.match(r"(\w+)(.*)", stripped)
            if match:
                event_name = match.group(1)
                arg = match.group(2).strip()
            else:
                event_name = stripped
                arg = ""
            self.dispatch(event_name, arg, engine)
        elif ':' in command:
            event_name, arg = command.split(":", 1)
            self.dispatch(event_name.strip(), arg.strip(), engine)
        else:
            # Por defecto, se asume un diálogo
            self.dispatch("say", command.strip(), engine)

    def dispatch(self, event_name, arg, engine=None):
        handlers = self.event_handlers.get(event_name, [])
        if not handlers:
            print(f"[WARNING] No hay manejadores para el evento '{event_name}'.")
        for handler in handlers:
            handler(arg, engine)

    # ---------- Manejadores “clásicos” ----------

    def handle_inicio(self, arg, engine):
        print("Evento 'inicio':", arg)
        engine.current_dialogue = arg
        engine.wait_for_keypress()
        engine.current_dialogue = ""

    def handle_say(self, arg, engine):
        if ',' in arg:
            character, dialogue = arg.split(',', 1)
            full_text = f"{character.strip()}: {dialogue.strip()}"
        else:
            full_text = arg
        engine.current_dialogue = full_text
        engine.wait_for_keypress()
        engine.current_dialogue = ""

    def handle_menu(self, arg, engine):
        options = [opt.strip() for opt in arg.split('|')]
        engine.current_menu = options
        engine.renderer.render()
        selection = engine.wait_for_menu_selection()
        engine.current_menu = None
        if selection is not None and selection < len(options):
            print(f"Menú seleccionado: {selection + 1} - {options[selection]}")
        else:
            print("No se seleccionó opción válida.")

    def handle_bg(self, arg, engine):
        bg_path = os.path.join(engine.game_path, "data", "images", "bg", arg)
        if os.path.exists(bg_path):
            try:
                image = pygame.image.load(bg_path)
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

    # ---------- Nuevos manejadores para comandos especiales ----------

    def handle_Load(self, arg, engine):
        """
        Carga un archivo dado en formato: @Load("ruta/al/archivo.kag")
        Se almacena el contenido en engine.loaded_files.
        Además, si se carga 'system/scenes.kag', se procesa para definir escenas.
        """
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        arg = arg.strip(' "\'')
        file_path = os.path.join(engine.game_path, "data", arg)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            engine.loaded_files[arg] = content
            print(f"[Load] Archivo cargado: {file_path}")
            # Si se trata de system/scenes.kag, procesamos sus líneas para definir escenas.
            if arg.lower() == "system/scenes.kag":
                for line in content.splitlines():
                    line = line.strip()
                    print("[DEBUG] Línea de escenas:", line)  # Línea de depuración
                    if line.startswith("@scene"):
                        # Se remueve el prefijo "@scene" y se procesa el resto.
                        scene_def = line[len("@scene"):].strip()
                        # Llamamos al manejador correspondiente (por ejemplo, pasando el comando "@scene first = "first"")
                        self.handle("@" + "scene " + scene_def, engine)
        except Exception as e:
            print(f"[Load] Error al cargar {file_path}: {e}")

    def handle_scene(self, arg, engine):
        """
        Procesa la definición de una escena.
        Se espera el formato: <alias> = "archivo"
        Ejemplo:
            @scene first = "first"
        Lo que significa que el alias 'first' corresponde al archivo "first.kag" (ubicado en data/scenes/).
        Se almacena en engine.scenes.
        """
        parts = arg.split("=")
        if len(parts) == 2:
            alias = parts[0].strip()
            filename = parts[1].strip().strip('"')
            engine.scenes[alias] = filename
            print(f"[scene] Escena definida: alias '{alias}', archivo '{filename}'")
        else:
            print("[scene] Formato inválido. Se esperaba: @scene alias = \"archivo\"")

    def handle_process_scene(self, arg, engine):
        """
        Procesa la escena de inicio.
        En este modo simple se espera que se pase el alias de la escena (por ejemplo: first).
        Se busca en engine.scenes la definición correspondiente y se carga el archivo:
            <game_path>/data/scenes/<archivo>.kag
        que se procesa línea por línea.
        """
        parts = [p.strip() for p in arg.split("|") if p.strip()]
        if len(parts) == 1:
            scene_alias = parts[0]
            if scene_alias in engine.scenes:
                scene_file_name = engine.scenes[scene_alias]  # p.ej. "first"
                scene_file_path = os.path.join(engine.game_path, "data", "scenes", f"{scene_file_name}.kag")
                print(f"[process_scene] Procesando escena '{scene_alias}' desde: {scene_file_path}")
                try:
                    with open(scene_file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    scene_commands = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
                    for cmd in scene_commands:
                        print(f"[process_scene] Comando de escena: {cmd}")
                        engine.event_manager.handle(cmd, engine)
                    engine.wait_for_keypress()
                except Exception as e:
                    print(f"[process_scene] Error al cargar la escena '{scene_alias}': {e}")
            else:
                print(f"[process_scene] Escena '{scene_alias}' no está definida en system/scenes.kag.")
        else:
            # Caso extendido (no utilizado en este ejemplo, pero se deja para ampliación)
            scene_alias = parts[0]
            print(f"[process_scene] Procesando escena (extendido): {scene_alias}")
            for token in parts[1:]:
                token = token.strip()
                if token.endswith(":"):
                    token = token[:-1].strip()
                    self.handle_Load('("' + token + '")', engine)
                elif token.startswith("@scene"):
                    new_command = token[len("@scene"):].strip()
                    print(f"[process_scene] Ejecutando comando de escena: {new_command}")
                    engine.event_manager.handle("@" + new_command, engine)
            engine.wait_for_keypress()

    def handle_char(self, arg, engine):
        """
        Define un personaje. Se espera el formato:
            alias as "Nombre"
        Ejemplo:
            @char K as "Kuro"
        """
        parts = arg.split(" as ")
        if len(parts) == 2:
            alias = parts[0].strip()
            display_name = parts[1].strip().strip('"')
            engine.characters[alias] = display_name
            print(f"[char] Definido personaje: alias '{alias}', nombre '{display_name}'")
        else:
            print("[char] Formato inválido. Se esperaba: @char alias as \"nombre\"")
