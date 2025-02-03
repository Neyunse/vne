import os
import pygame
import re

class EventManager:
    def __init__(self):
        self.event_handlers = {}
        self.register_default_events()

    def register_default_events(self):
        # Registro de comandos clásicos y especiales
        self.register_event("say", self.handle_say)
        # self.register_event("menu", self.handle_menu)  # Puedes descomentar si lo necesitas
        self.register_event("bg", self.handle_bg)
        self.register_event("exit", self.handle_exit)
        # Comandos especiales definidos con @
        self.register_event("Load", self.handle_Load)
        self.register_event("process_scene", self.handle_process_scene)
        self.register_event("char", self.handle_char)
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
            # Separamos por ":" y obtenemos el token de la izquierda.
            event_name, arg = command.split(":", 1)
            event_name = event_name.strip()
            arg = arg.strip()
            # Si el token a la izquierda corresponde a un comando registrado,
            # se procesa normalmente; de lo contrario se trata como diálogo.
            if event_name in self.event_handlers:
                self.dispatch(event_name, arg, engine)
            else:
                # Se trata la línea completa como diálogo.
                self.handle_say(command, engine)
        else:
            self.dispatch("say", command.strip(), engine)

    def dispatch(self, event_name, arg, engine=None):
        handlers = self.event_handlers.get(event_name, [])
        if not handlers:
            print(f"[WARNING] No hay manejadores para el evento '{event_name}'.")
        for handler in handlers:
            handler(arg, engine)

    def handle_say(self, arg, engine):
        """
        Procesa un diálogo. Se espera la sintaxis:
        <speaker>: <dialogue text>
        Además, si el texto contiene marcadores del tipo {alias}, se reemplazan
        por el nombre definido para ese personaje.
        También, si el speaker coincide con un alias definido, se sustituye por su display name.
        """
        import re
        if ':' in arg:
            speaker, dialogue = arg.split(":", 1)
            speaker = speaker.strip()
            dialogue = dialogue.strip()
            # Reemplazar el speaker por su display name si está definido
            if speaker in engine.characters:
                speaker = engine.characters[speaker]
            # Función para sustituir {alias} por el display name del personaje
            def replacer(match):
                key = match.group(1).strip()
                replacement = engine.characters.get(key, match.group(0))
                print(f"[DEBUG] Reemplazando '{{{key}}}' por '{replacement}'")
                return replacement
            dialogue = re.sub(r"\{([^}]+)\}", replacer, dialogue)
            full_text = f"{speaker}: {dialogue}"
        else:
            full_text = arg
        engine.current_dialogue = full_text
        engine.wait_for_keypress()
        engine.current_dialogue = ""


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

    def handle_Load(self, arg, engine):
        """
        Carga un archivo dado en formato: @Load("ruta/al/archivo.kag")
        Almacena el contenido en engine.loaded_files y procesa dinámicamente
        cada línea que sea un comando (aquellas que comienzan con '@').
        """
        # Limpieza del argumento: quitar paréntesis y comillas
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        arg = arg.strip(' "\'')
        
        # Construir la ruta completa del archivo usando el path recibido
        file_path = os.path.join(engine.game_path, "data", arg)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"[Load] Error al cargar {file_path}: {e}")
            return  # Se detiene si ocurre algún error
        
        # Almacenar el contenido en engine.loaded_files para referencia futura
        engine.loaded_files[arg] = content
        print(f"[Load] Archivo cargado: {file_path}")
        
        # Procesar dinámicamente cada línea del archivo:
        # Se recorren todas las líneas y se invoca self.handle() en las que sean comandos.
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # Ignorar líneas vacías o comentarios
            # Si la línea comienza con '@', la consideramos un comando a procesar.
            if line.startswith("@"):
                self.handle(line, engine)


    def handle_scene(self, arg, engine):
        """
        Procesa la definición de una escena.
        Se espera el formato: <alias> = "archivo"
        Ejemplo:
            @scene first = "first"
        Lo que significa que el alias 'first' corresponde al archivo "first.kag"
        (ubicado en data/scenes/). Se almacena en engine.scenes.
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
        Se espera que se pase el alias de la escena (por ejemplo: first).
        Se busca en engine.scenes la definición correspondiente y se carga el archivo:
          <game_path>/data/scenes/<archivo>.kag
        que se procesa línea por línea.
        """
        parts = [p.strip() for p in arg.split("|") if p.strip()]
        if len(parts) == 1:
            scene_alias = parts[0]
            if scene_alias in engine.scenes:
                scene_file_name = engine.scenes[scene_alias]  # Ejemplo: "first"
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
            # Caso extendido (para formatos más complejos, no usado en este ejemplo)
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
        Define un personaje. Se permiten dos formatos:
          1) @char K as "Kuro"   -> Define el alias "K" con display name "Kuro".
          2) @char K            -> Define el alias "K" y se usa "K" como nombre a mostrar.
        """
        if " as " in arg:
            parts = arg.split(" as ")
            if len(parts) == 2:
                alias = parts[0].strip()
                display_name = parts[1].strip().strip('"')
                engine.characters[alias] = display_name
                print(f"[char] Definido personaje: alias '{alias}', nombre '{display_name}'")
            else:
                print("[char] Formato inválido. Se esperaba: @char alias as \"nombre\"")
        else:
            alias = arg.strip()
            if alias:
                engine.characters[alias] = alias  # Usa el alias como nombre por defecto
                print(f"[char] Definido personaje: alias '{alias}', nombre '{alias}'")
            else:
                print("[char] Formato inválido. Se esperaba: @char alias [as \"nombre\"]")
