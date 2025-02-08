# engine/vne/events.py
import os
import pygame
import re
from vne.lexer import ScriptLexer
from vne.xor_data import xor_data
from vne.config import key

class EventManager:
    def __init__(self):
        self.event_handlers = {}
        self.register_default_events()
    
    def register_default_events(self):
        self.register_event("say", self.handle_say)
        self.register_event("bg", self.handle_bg)
        self.register_event("exit", self.handle_exit)
        self.register_event("Load", self.handle_Load)
        self.register_event("process_scene", self.handle_process_scene)
        self.register_event("jump_scene", self.handle_jump_scene)
        self.register_event("char", self.handle_char)
        self.register_event("scene", self.handle_scene)
        self.register_event("def", self.handle_define)
        self.register_event("sprite", self.handle_sprite)
        self.register_event("hide", self.handle_hide)

    def register_event(self, event_name, handler):
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
    
    def handle(self, command, engine=None):
        command = command.strip()
        # Si el comando comienza con "@", es un comando especial.
        if command.startswith("@"):
            stripped = command[1:].strip()
            # Extraer el nombre del comando y el argumento usando regex.
            match = re.match(r"(\w+)(.*)", stripped)
            if match:
                event_name = match.group(1)
                arg = match.group(2).strip()
                # Si arg comienza con ":" (por ejemplo, en "@menu:"), lo quitamos.
                arg = arg.lstrip(":").strip()
            else:
                event_name = stripped
                arg = ""
            self.dispatch(event_name, arg, engine)
        elif ':' in command:
            event_name, arg = command.split(":", 1)
            event_name = event_name.strip()
            arg = arg.strip()
            if event_name in self.event_handlers:
                self.dispatch(event_name, arg, engine)
            else:
                self.handle_say(command, engine)
        else:
            self.dispatch("say", command.strip(), engine)
    
    def dispatch(self, event_name, arg, engine=None):
        handlers = self.event_handlers.get(event_name, [])
        if not handlers:
            raise Exception(f"[ERROR] No hay manejadores para el evento '{event_name}'.")
        for handler in handlers:
            handler(arg, engine)
    
    def handle_say(self, arg, engine):
        """
        Procesa un diálogo:
        - Con speaker: <speaker>: <dialogue>
        - Sin speaker: simplemente el diálogo.
        Reemplaza marcadores {alias} buscando en engine.characters, engine.scenes y engine.vars.
        Si se usa un speaker que no está definido, lanza un error.
        Asigna el nombre del personaje a engine.current_character_name y el diálogo a engine.current_dialogue.
        Luego espera a que el usuario haga clic (en lugar de esperar una tecla).
        """
        import re
        if ':' in arg:
            speaker, dialogue = arg.split(":", 1)
            speaker = speaker.strip()
            dialogue = dialogue.strip()
            if speaker not in engine.characters:
                raise Exception(f"[ERROR] El personaje '{speaker}' no está definido.")
            # Se asigna el nombre registrado en engine.characters (por ejemplo, "Kuro")
            engine.current_character_name = engine.characters[speaker]
            # Se procesa el diálogo para reemplazar marcadores {alias}
            def replacer(match):
                key = match.group(1).strip()
                if key in engine.characters:
                    return engine.characters[key]
                elif key in engine.scenes:
                    return engine.scenes[key]
                elif key in engine.vars:
                    return engine.vars[key]
                else:
                    raise Exception(f"[ERROR] No está definida la variable para '{key}'.")
            dialogue = re.sub(r"\{([^}]+)\}", replacer, dialogue)
            # El diálogo se asigna sin el nombre, ya que éste se mostrará en una caja aparte
            engine.current_dialogue = dialogue
        else:
            # Si no hay speaker, se asigna el diálogo y se limpia el nombre
            engine.current_dialogue = arg.strip()
            engine.current_character_name = ""
            def replacer(match):
                key = match.group(1).strip()
                if key in engine.characters:
                    return engine.characters[key]
                elif key in engine.scenes:
                    return engine.scenes[key]
                else:
                    raise Exception(f"[ERROR] No está definida la variable para '{key}'.")
            engine.current_dialogue = re.sub(r"\{([^}]+)\}", replacer, engine.current_dialogue)
        
        # Esperar al clic del ratón (en lugar de wait_for_keypress)
        engine.wait_for_keypress()
        # Limpiar después de avanzar
        engine.current_dialogue = ""
        engine.current_character_name = ""

    
    def handle_bg(self, arg, engine):
        """
        Carga la imagen de fondo. Se espera que 'arg' sea el nombre del archivo,
        por ejemplo, "school.png". Se busca en "images/bg/".
        """
        load_image = ScriptLexer(engine.game_path, engine).load_image
        # Construir la ruta relativa para el fondo
        relative_path = os.path.join("images", "bg", arg)
        try:
            bg_image = load_image(relative_path)
            # Escalar la imagen al tamaño de la pantalla
            bg_image = pygame.transform.scale(bg_image, (engine.renderer.screen.get_width(),
                                                        engine.renderer.screen.get_height()))
            engine.current_bg = bg_image
        except Exception as e:
            raise Exception(f"[bg] Error al cargar la imagen de fondo: {e}")

    
    def handle_exit(self, arg, engine):
        print("Evento 'exit'", arg)
        engine.running = False
    
    def handle_Load(self, arg, engine):
        # Limpiar el argumento: quitar paréntesis y comillas
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        arg = arg.strip('"').strip("'")
        
        # Determinar si este archivo es de definiciones (dinámico)
        # Aquí se evalúa si en el nombre aparece "characters.kag", "vars.kag" o "scenes.kag"
        force_compiled = any(keyword in arg.lower() for keyword in ["characters.kag", "vars.kag", "scenes.kag"])
        
        try:
            if force_compiled:
                # Forzar el uso de la versión compilada
                if not arg.lower().endswith(".kagc"):
                    compiled_arg = arg[:-4] + ".kagc"
                else:
                    compiled_arg = arg
                data = engine.resource_manager.get_bytes(compiled_arg)
                 
                # Descifrar el contenido
                data = xor_data(data, key)
                print(f"[Load] Archivo compilado cargado: {compiled_arg}")
                engine.loaded_files[compiled_arg] = data
                content = data.decode("utf-8", errors="replace")
            else:
                # Para otros recursos, cargar normalmente
                data = engine.resource_manager.get_bytes(arg)
                print(f"[Load] Archivo cargado: {arg}")
                engine.loaded_files[arg] = data
                content = data.decode("utf-8", errors="replace")
            
            # Procesar el contenido si parece contener directivas (líneas que comienzan con "@")
            if any(line.strip().startswith("@") for line in content.splitlines()):
              
                commands = ScriptLexer(engine.game_path, engine).parse_script(content)
                for cmd in commands:
                    print(f"[Load-Process] Ejecutando comando: {cmd}")
                    self.handle(cmd, engine)
        except Exception as e:
            print(f"[Load] Error al cargar {arg}: {e}")

    
    def handle_scene(self, arg, engine):
        """
        Define una escena. Formato: @scene alias = "archivo"
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
        
    def handle_define(self, arg, engine):
        """
        Define una variable. Formato: @def alias = "valor"
        Se almacena en engine.variables.
        """
        parts = arg.split("=")
        if len(parts) == 2:
            alias = parts[0].strip()
            filename = parts[1].strip().strip('"')
            engine.vars[alias] = filename
            print(f"[variable] Variable definida: alias '{alias}', archivo '{filename}'")
        else:
            raise Exception("[ERROR] Formato inválido en @def. Se esperaba: @def alias = \"valor\"")
    
    def handle_process_scene(self, arg, engine):

        # Limpiar el argumento para extraer el alias de la escena.
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
            arg = arg[1:-1].strip()
        
        scene_alias = arg
        # Usar la definición en engine.scenes, si existe.
        if scene_alias in engine.scenes:
            filename = engine.scenes[scene_alias]
        else:
            filename = scene_alias

        # Construir la ruta base: se asume que las escenas están en la carpeta "scenes".
        base_name = os.path.join("scenes", filename)

        # Primero intentamos cargar la versión compilada (".kagc").
        try:
            # Construir la ruta completa agregando la extensión .kagc
            compiled_path = base_name + ".kagc"
            file_bytes = engine.resource_manager.get_bytes(compiled_path)
            # Aplicar XOR para descifrar el contenido.
            content = xor_data(file_bytes, key).decode("utf-8", errors="replace")
        except Exception as e:
            # Si falla (por ejemplo, no se encuentra la versión compilada), se lanza error.
            raise Exception(f"[ERROR] No se encontró la versión compilada del script para '{base_name}': {e}")

        print(f"[process_scene] Procesando escena '{scene_alias}'.")
        scene_commands = ScriptLexer(engine.game_path, engine).parse_script(content)
        for cmd in scene_commands:
            print(f"[process_scene] Comando de escena: {cmd}")
            engine.event_manager.handle(cmd, engine)
        engine.wait_for_keypress()



    def handle_jump_scene(self, arg, engine):
        """
        Salta a otra escena sin esperar keypress.
        Se espera el alias de la escena.
        """
        parts = [p.strip() for p in arg.split("|") if p.strip()]
        if len(parts) == 1:
            scene_alias = parts[0]
            if scene_alias in engine.scenes:
                scene_file_name = engine.scenes[scene_alias]
                scene_file_path = os.path.join(engine.game_path, "data", "scenes", f"{scene_file_name}.kag")
                print(f"[jump_scene] Saltando a escena '{scene_alias}' desde: {scene_file_path}")
                try:
                    with open(scene_file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    scene_commands = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
                    for cmd in scene_commands:
                        print(f"[jump_scene] Comando de escena: {cmd}")
                        engine.event_manager.handle(cmd, engine)
                except Exception as e:
                    raise Exception(f"[jump_scene] Error al cargar la escena '{scene_alias}': {e}")
            else:
                raise Exception(f"[ERROR] Escena '{scene_alias}' no está definida en system/scenes.kag.")
        else:
            raise Exception("[ERROR] Formato extendido en @jump_scene no implementado.")
    
    def handle_char(self, arg, engine):
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
                engine.characters[alias] = alias
                print(f"[char] Definido personaje: alias '{alias}', nombre '{alias}'")
            else:
                print("[char] Formato inválido. Se esperaba: @char alias [as \"nombre\"]")

    def handle_sprite(self, arg, engine):
        """
        Muestra un sprite en pantalla.
        Se espera que el comando tenga el formato:
            @sprite kuro
        o, opcionalmente, con posición:
            @sprite kuro at left
        Los valores de posición pueden ser "left", "center" o "right" (por defecto, "center").
        """
        parts = arg.split(" at ")
        sprite_alias = parts[0].strip()
        position = parts[1].strip().lower() if len(parts) > 1 else "center"
        # Se asume que los sprites están en data/images/sprites y tienen extensión .png
        sprite_path = os.path.join(engine.game_path, "data", "images", "sprites", sprite_alias + ".png")
        if not os.path.exists(sprite_path):
            raise Exception(f"[sprite] No se encontró el sprite '{sprite_alias}' en {sprite_path}.")
        try:
            sprite_image = pygame.image.load(sprite_path).convert_alpha()
        except Exception as e:
            raise Exception(f"[sprite] Error al cargar el sprite '{sprite_alias}': {e}")
        # Almacenar el sprite en engine.sprites (un diccionario)
        if not hasattr(engine, "sprites"):
            engine.sprites = {}
        engine.sprites[sprite_alias] = {"image": sprite_image, "position": position}
        print(f"[sprite] Sprite '{sprite_alias}' mostrado en posición '{position}'.")
    
    def handle_hide(self, arg, engine):
        """
        Oculta (elimina) un sprite previamente mostrado.
        Se espera: @hide kuro
        """
        sprite_alias = arg.strip()
        if hasattr(engine, "sprites") and sprite_alias in engine.sprites:
            del engine.sprites[sprite_alias]
            print(f"[hide] Sprite '{sprite_alias}' ocultado.")
        else:
            print(f"[hide] No se encontró el sprite '{sprite_alias}' para ocultarlo.")