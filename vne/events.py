import os
import pygame
import re

class EventManager:
    def __init__(self):
        self.event_handlers = {}
        self.register_default_events()

    def register_default_events(self):
        # Registro de comandos
        self.register_event("say", self.handle_say)
        # self.register_event("menu", self.handle_menu)  # Descomenta si es necesario
        self.register_event("exit", self.handle_exit)
        # Comandos especiales definidos con @
        self.register_event("Load", self.handle_Load)
        self.register_event("process_scene", self.handle_process_scene)
        self.register_event("char", self.handle_char)
        self.register_event("scene", self.handle_scene)
        self.register_event("jump_scene", self.handle_jump_scene)

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
            # se procesa; de lo contrario se trata como diálogo.
            if event_name in self.event_handlers:
                self.dispatch(event_name, arg, engine)
            else:
                # Se procesa como diálogo completo.
                self.handle_say(command, engine)
        else:
            self.dispatch("say", command.strip(), engine)

    def dispatch(self, event_name, arg, engine=None):
        handlers = self.event_handlers.get(event_name, [])
        if not handlers:
            # Si no hay manejadores definidos para el comando, se lanza un error.
            raise Exception(f"[ERROR] No hay manejadores para el evento '{event_name}'.")
        for handler in handlers:
            handler(arg, engine)

    def handle_say(self, arg, engine):
        """
        Procesa un diálogo. Se espera la siguiente sintaxis:
        - Con speaker: <speaker>: <dialogue text>
        - Sin speaker: <dialogue text>
        
        En ambos casos, si el texto contiene marcadores del tipo {alias},
        se reemplazan por el valor definido para ese alias en engine.characters o, 
        en su defecto, en engine.scenes.
        
        Si en el caso con speaker el alias (lo que aparece antes de ":") no está definido en
        engine.characters, se lanza un error. De igual forma, si algún marcador no está definido
        en ninguno de los diccionarios, se lanza un error.
        """
        import re
        if ':' in arg:
            # Se procesa la línea como diálogo con speaker.
            speaker, dialogue = arg.split(":", 1)
            speaker = speaker.strip()
            dialogue = dialogue.strip()
            
            # Verificar que el speaker esté definido en engine.characters.
            if speaker not in engine.characters:
                raise Exception(f"[ERROR] El personaje '{speaker}' (speaker) no está definido.")
            else:
                # Se reemplaza el speaker por su display name.
                speaker = engine.characters[speaker]
            
            # Función para reemplazar marcadores {alias} en el diálogo.
            def replacer(match):
                key = match.group(1).strip()
                if key in engine.characters:
                    return engine.characters[key]
                elif key in engine.scenes:
                    return engine.scenes[key]
                else:
                    raise Exception(f"[ERROR] No está definida la variable para '{key}'.")
            
            dialogue = re.sub(r"\{([^}]+)\}", replacer, dialogue)
            full_text = f"{speaker}: {dialogue}"
        else:
            # Se procesa la línea como diálogo sin speaker.
            dialogue = arg.strip()
            
            def replacer(match):
                key = match.group(1).strip()
                if key in engine.characters:
                    return engine.characters[key]
                elif key in engine.scenes:
                    return engine.scenes[key]
                else:
                    raise Exception(f"[ERROR] No está definida la variable para '{key}'.")
            
            dialogue = re.sub(r"\{([^}]+)\}", replacer, dialogue)
            full_text = dialogue

        engine.current_dialogue = full_text
        engine.wait_for_keypress()
        engine.current_dialogue = ""


    def handle_exit(self, arg, engine):
        print("Evento 'exit'", arg)
        engine.running = False

    def handle_Load(self, arg, engine):
        """
        Carga un archivo dado en formato: @Load("ruta/al/archivo.kag")
        Almacena el contenido en engine.loaded_files y procesa dinámicamente
        cada línea que sea un comando (líneas que comienzan con '@').
        """
        # Limpieza del argumento: quitar paréntesis y comillas
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        arg = arg.strip(' "\'')
        
        file_path = os.path.join(engine.game_path, "data", arg)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"[Load] Error al cargar {file_path}: {e}")
        
        engine.loaded_files[arg] = content
        print(f"[Load] Archivo cargado: {file_path}")
        
        # Procesa cada línea que comience con '@'
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("@"):
                self.handle(line, engine)

    def handle_scene(self, arg, engine):
        """
        Procesa la definición de una escena.
        Se espera el formato: <alias> = "archivo"
        Ejemplo: @scene first = "first"
        Se almacena en engine.scenes.
        """
        parts = arg.split("=")
        if len(parts) == 2:
            alias = parts[0].strip()
            filename = parts[1].strip().strip('"')
            engine.scenes[alias] = filename
            print(f"[scene] Escena definida: alias '{alias}', archivo '{filename}'")
        else:
            raise Exception("[ERROR] Formato inválido en @scene. Se esperaba: @scene alias = \"archivo\"")

    def handle_process_scene(self, arg, engine):
        """
        Procesa la escena de inicio.
        Se espera que se pase el alias de la escena (por ejemplo, first).
        Busca en engine.scenes la definición correspondiente y carga el archivo:
          <game_path>/data/scenes/<archivo>.kag
        Procesa cada línea de dicho archivo.
        """
        parts = [p.strip() for p in arg.split("|") if p.strip()]
        if len(parts) == 1:
            scene_alias = parts[0]
            if scene_alias in engine.scenes:
                scene_file_name = engine.scenes[scene_alias]
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
                    raise Exception(f"[process_scene] Error al cargar la escena '{scene_alias}': {e}")
            else:
                raise Exception(f"[ERROR] Escena '{scene_alias}' no está definida en system/scenes.kag.")
        else:
            # Caso extendido: no implementado en este ejemplo
            raise Exception("[ERROR] Formato extendido en @process_scene no implementado.")

    def handle_char(self, arg, engine):
        """
        Define un personaje. Se permiten dos formatos:
          1) @char K as "Kuro"   -> Define el alias "K" con display name "Kuro".
          2) @char K            -> Define el alias "K" y se usa "K" como display name.
        """
        if " as " in arg:
            parts = arg.split(" as ")
            if len(parts) == 2:
                alias = parts[0].strip()
                display_name = parts[1].strip().strip('"')
                engine.characters[alias] = display_name
                print(f"[char] Definido personaje: alias '{alias}', nombre '{display_name}'")
            else:
                raise Exception("[ERROR] Formato inválido en @char. Se esperaba: @char alias as \"nombre\"")
        else:
            alias = arg.strip()
            if alias:
                engine.characters[alias] = alias
                print(f"[char] Definido personaje: alias '{alias}', nombre '{alias}'")
            else:
                raise Exception("[ERROR] Formato inválido en @char. Se esperaba: @char alias [as \"nombre\"]")
    
    def handle_jump_scene(self, arg, engine):
        """
        Procesa el salto a otra escena. Se espera que se pase el alias de la escena a la que se desea saltar.
        Busca en engine.scenes la definición correspondiente y carga el archivo:
        <game_path>/data/scenes/<archivo>.kag
        que se procesa línea por línea.
        
        Ejemplo de uso:
        @jump_scene first
        """
        # Se espera que el argumento sea solo el alias de la escena
        parts = [p.strip() for p in arg.split("|") if p.strip()]
        if len(parts) != 1:
            raise Exception("[ERROR] Formato inválido en @jump_scene. Se esperaba: @jump_scene alias")
        
        scene_alias = parts[0]
        
        if scene_alias not in engine.scenes:
            raise Exception(f"[ERROR] Escena '{scene_alias}' no está definida en system/scenes.kag.")
        
        # Obtener el nombre del archivo de la escena a partir de la definición
        scene_file_name = engine.scenes[scene_alias]  # Por ejemplo, "first"
        scene_file_path = os.path.join(engine.game_path, "data", "scenes", f"{scene_file_name}.kag")
        
        print(f"[jump_scene] Saltando a escena '{scene_alias}' desde: {scene_file_path}")
        
        try:
            with open(scene_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Procesar cada línea del archivo (ignorando líneas vacías y comentarios)
            scene_commands = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
            for cmd in scene_commands:
                print(f"[jump_scene] Comando de escena: {cmd}")
                engine.event_manager.handle(cmd, engine)
        except Exception as e:
            raise Exception(f"[jump_scene] Error al cargar la escena '{scene_alias}': {e}")

