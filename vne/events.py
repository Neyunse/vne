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
        """
        The function `register_default_events` registers various event handlers for different events in
        a Python class.
        """
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
        self.register_event("hide", self.handle_hide_sprite)
        self.register_event("rename", self.handle_rename)

        self.register_event("if", self.handle_if)
        self.register_event("else", self.handle_else)
        self.register_event("endif", self.handle_endif)
        self.register_event("checkpoint", self.handle_checkpoint)
        self.register_event("goto", self.handle_goto)
        self.register_event("set", self.handle_set)


    def register_event(self, event_name, handler):
        """
        The function `register_event` adds a handler to a list of event handlers associated with a
        specific event name.
        
        :param event_name: The `event_name` parameter is a string that represents the name of the event
        being registered
        :param handler: The `handler` parameter in the `register_event` method is a function or method
        that will be called when the specified `event_name` is triggered. It is essentially the callback
        function that will be executed when the event occurs
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
    
    def handle(self, command, engine=None):
        """
        The function `handle` processes a command by extracting event name and argument, then dispatches
        the event with the argument to the appropriate handler.
        
        :param command: The `command` parameter in the `handle` method is a string that represents the
        input command to be processed. It may contain various types of commands, such as event triggers,
        messages, or other instructions to be handled by the method. The method processes the command
        based on its structure and content to
        :param engine: The `engine` parameter in the `handle` method is used to specify the engine that
        will be passed to the `dispatch` method. It is an optional parameter, meaning that if no engine
        is provided when calling the `handle` method, it will default to `None`. The `engine`
        """
        command = command.strip()
         
        if command.startswith("@"):
            stripped = command[1:].strip()
         
            match = re.match(r"(\w+)(.*)", stripped)
            if match:
                event_name = match.group(1)
                arg = match.group(2).strip()
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
        """
        The `dispatch` function takes an event name, argument, and optional engine, then calls the
        corresponding event handlers with the argument and engine.
        
        :param event_name: The `event_name` parameter in the `dispatch` method is a string that
        represents the name of the event for which you want to dispatch the handlers. It is used to look
        up the appropriate handlers for that specific event from the `event_handlers` dictionary
        :param arg: The `arg` parameter in the `dispatch` method represents the argument that will be
        passed to the event handlers when the event is triggered. It could be any data or object that
        the event handlers need to process or work with
        :param engine: The `engine` parameter in the `dispatch` method is an optional argument that
        represents the engine or system on which the event is being dispatched. It is used to provide
        additional context or functionality to the event handlers when they are called. If an `engine`
        is provided, it will be passed along
        """
        control_commands = {"if", "else", "endif", "checkpoint", "goto"}
        if event_name not in control_commands:
            
            if hasattr(engine, "condition_stack") and engine.condition_stack:
        
                if not all(engine.condition_stack):
                    return
        handlers = self.event_handlers.get(event_name, [])
        if not handlers:
            raise Exception(f"[ERROR] No hay manejadores para el evento '{event_name}'.")
        for handler in handlers:
            handler(arg, engine)
    
    def handle_say(self, arg, engine):
        """
        The `handle_say` function in Python processes dialogue for characters in a game engine,
        replacing variables with their corresponding values before waiting for user input.
        
        :param arg: The `arg` parameter in the `handle_say` method is used to represent the input string
        that contains the dialogue to be spoken by a character. This method handles parsing the input
        string to extract the speaker (if specified) and the dialogue itself. If the speaker is
        specified, it checks if
        :param engine: The `engine` parameter in the `handle_say` method seems to be an object that
        contains information about characters, scenes, and variables in a storytelling engine. It is
        used to process dialogue and replace placeholders with corresponding values before displaying
        the dialogue. The method also waits for a keypress before clearing
        """
 
        if ':' in arg:
            speaker, dialogue = arg.split(":", 1)
            speaker = speaker.strip()
            dialogue = dialogue.strip()
            if speaker not in engine.characters:
                raise Exception(f"[ERROR] El personaje '{speaker}' no está definido.")
    
            engine.current_character_name = engine.characters[speaker]
       
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
 
            engine.current_dialogue = dialogue
        else:
        
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
        
 
        engine.wait_for_keypress()
 
        engine.current_dialogue = ""
        engine.current_character_name = ""

    
    def handle_bg(self, arg, engine):
        """
        The function `handle_bg` loads and scales a background image for a game engine in Python.
        
        :param arg: The `arg` parameter in the `handle_bg` method seems to represent the name or
        identifier of the background image that needs to be loaded and displayed. It is used to
        construct the relative path to the background image file by joining the "images/bg" directory
        with the provided argument followed by the "
        :param engine: The `engine` parameter seems to be an object that contains information and
        functionality related to the game engine. It likely has attributes or methods that are being
        used in the `handle_bg` method, such as `game_path`, `renderer`, and `current_bg`
        """
 
        load_image = ScriptLexer(engine.game_path, engine).load_image
        
        relative_path = os.path.join("images", "bg", arg + ".jpg")
        try:
            bg_image = load_image(relative_path)
            
            bg_image = pygame.transform.scale(bg_image, (engine.renderer.screen.get_width(),
                                                        engine.renderer.screen.get_height()))
            engine.current_bg = bg_image
        except Exception as e:
            raise Exception(f"[bg] Error al cargar la imagen de fondo: {e}")
        
    def handle_sprite(self, arg, engine):
        """
        The function `handle_sprite` loads and stores a sprite image with a specified alias and position
        in the game engine.
        
        :param arg: The `arg` parameter in the `handle_sprite` method is a string that contains
        information about the sprite to be handled. It is expected to have the format "sprite_alias at
        position", where:
        :param engine: The `engine` parameter in the `handle_sprite` method seems to be an object that
        contains information and functionality related to the game engine or game environment. It likely
        includes attributes and methods that are used to manage game elements, such as loading images,
        handling sprites, and storing sprite information
        """
 
        load_image = ScriptLexer(engine.game_path, engine).load_image
 
        parts = arg.split(" at ")
        sprite_alias = parts[0].strip()
        position = parts[1].strip().lower() if len(parts) > 1 else "center"
         
        relative_path = os.path.join("images", "sprites", sprite_alias + ".png")
        try:
            sprite_image = load_image(relative_path)
        except Exception as e:
            raise Exception(f"[sprite] {e}")
         
        if not hasattr(engine, "sprites"):
            engine.sprites = {}
        engine.sprites[sprite_alias] = {"image": sprite_image, "position": position}
        print(f"[sprite] Sprite '{sprite_alias}' mostrado en posición '{position}'.")
    
    def handle_hide_sprite(self, arg, engine):
        """
        This Python function handles hiding a sprite in a game engine by removing it from the engine's
        sprites dictionary if it exists.
        
        :param arg: The `arg` parameter in the `handle_hide_sprite` function is expected to be a string
        that represents the alias of a sprite that needs to be hidden. This alias is used to identify
        the specific sprite that should be removed from the `engine.sprites` dictionary if it exists
        :param engine: The `engine` parameter in the `handle_hide_sprite` function seems to be an object
        that contains a dictionary attribute named `sprites`. This dictionary likely stores sprite
        aliases as keys and corresponding sprite objects as values. The function checks if the provided
        `sprite_alias` exists in the `engine.sprites` dictionary
        """
 
        sprite_alias = arg.strip()
        if hasattr(engine, "sprites") and sprite_alias in engine.sprites:
            del engine.sprites[sprite_alias]
            print(f"[hide] Sprite '{sprite_alias}' ocultado.")
        else:
            print(f"[hide] No se encontró el sprite '{sprite_alias}' para ocultarlo.")
    
    def handle_exit(self, arg, engine):
        """
        The function `handle_exit` prints a message and sets the `running` attribute of the `engine`
        object to `False`.
        
        :param arg: The `arg` parameter in the `handle_exit` method is typically used to pass any
        additional information or arguments related to the exit event that triggered the method. It can
        be used to provide context or specific details about the exit event being handled
        :param engine: The `engine` parameter in the `handle_exit` method seems to be an object that
        contains a boolean attribute `running`. This attribute is being set to `False` when the method
        is called, likely to indicate that the engine should stop running or exit
        """
        print("Evento 'exit'", arg)
        engine.running = False
    
    def handle_Load(self, arg, engine):
        """
        The `handle_Load` function in Python loads and processes KAG/KAGC files, handling both compiled
        and regular files, executing commands found in the content.
        
        :param arg: The `arg` parameter in the `handle_Load` method is a string that represents the file
        path or name of the resource that needs to be loaded. It is processed to handle different cases
        such as stripping whitespace, removing quotes, and checking for specific keywords to determine
        if the resource needs to be compiled
        :param engine: The `engine` parameter in the `handle_Load` method seems to be an instance of
        some class that contains methods and attributes related to resource management and script
        execution in a game engine. It is likely used to interact with game resources, load files, and
        execute commands within the game environment
        """
   
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        arg = arg.strip('"').strip("'")
        
        force_compiled = any(keyword in arg.lower() for keyword in ["characters.kag", "vars.kag", "scenes.kag"])
        
        try:
            if force_compiled:
                
                if not arg.lower().endswith(".kagc"):
                    compiled_arg = arg[:-4] + ".kagc"
                else:
                    compiled_arg = arg
                data = engine.resource_manager.get_bytes(compiled_arg)
                 
         
                data = xor_data(data, key)
                print(f"[Load] Archivo compilado cargado: {compiled_arg}")
                engine.loaded_files[compiled_arg] = data
                content = data.decode("utf-8", errors="replace")
            else:
                data = engine.resource_manager.get_bytes(arg)
                print(f"[Load] Archivo cargado: {arg}")
                engine.loaded_files[arg] = data
                content = data.decode("utf-8", errors="replace")
            
            
            if any(line.strip().startswith("@") for line in content.splitlines()):
              
                commands = ScriptLexer(engine.game_path, engine).parse_script(content)
                for cmd in commands:
                    print(f"[Load-Process] Ejecutando comando: {cmd}")
                    self.handle(cmd, engine)
        except Exception as e:
            print(f"[Load] Error al cargar {arg}: {e}")

    
    def handle_scene(self, arg, engine):
        """
        The function `handle_scene` parses and stores scene aliases and filenames in a dictionary within
        the engine object.
        
        :param arg: The `arg` parameter in the `handle_scene` method is a string that represents the
        input provided by the user. It is expected to be in the format `alias = "filename"`, where
        `alias` is the name or identifier for the scene, and `filename` is the name of
        :param engine: The `engine` parameter in the `handle_scene` method seems to be an instance of a
        class that has a `scenes` attribute. This attribute is used to store mappings between scene
        aliases and their corresponding filenames. The method takes an argument `arg`, which is expected
        to be in the format `
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
        The function `handle_define` parses and stores variable definitions in a specified engine.
        
        :param arg: The `arg` parameter in the `handle_define` method is a string that represents the
        input provided by the user. It is expected to be in the format `alias = "filename"`, where
        `alias` is the variable name and `filename` is the value assigned to that variable
        :param engine: The `engine` parameter in the `handle_define` method seems to be an object that
        contains a `vars` attribute. This attribute is used to store key-value pairs where the key is an
        alias and the value is a filename. The method takes an argument `arg`, which is expected to be
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
        """
        The function `handle_process_scene` processes a scene by retrieving its compiled script, parsing
        it, and executing the commands within the scene.
        
        :param arg: The `arg` parameter in the `handle_process_scene` method seems to represent a scene
        alias or filename that needs to be processed. The method first strips any leading or trailing
        whitespace from the input `arg`. It then checks if the `arg` is enclosed in parentheses or
        quotes and removes them if
        :param engine: The `engine` parameter in the `handle_process_scene` method seems to be an
        instance of some class that contains information and functionality related to scenes, scripts,
        and event handling in a game engine. It likely has attributes or methods related to scenes,
        resource management, event handling, and game paths
        """

 
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
            arg = arg[1:-1].strip()
        
        scene_alias = arg
   
        if scene_alias in engine.scenes:
            filename = engine.scenes[scene_alias]
        else:
            filename = scene_alias
 
        base_name = os.path.join("scenes", filename)
 
        try:
     
            compiled_path = base_name + ".kagc"
            file_bytes = engine.resource_manager.get_bytes(compiled_path)
        
            content = xor_data(file_bytes, key).decode("utf-8", errors="replace")
        except Exception as e:
      
            raise Exception(f"[ERROR] No se encontró la versión compilada del script para '{base_name}': {e}")

        print(f"[process_scene] Procesando escena '{scene_alias}'.")
        scene_commands = ScriptLexer(engine.game_path, engine).parse_script(content)
        for cmd in scene_commands:
            print(f"[process_scene] Comando de escena: {cmd}")
            engine.event_manager.handle(cmd, engine)
        engine.wait_for_keypress()



    def handle_jump_scene(self, arg, engine):
        """
        Procesa el comando de salto de escena.
        Se acepta un alias de escena (sin formato extendido). El método intenta primero
        cargar la versión compilada (.kagc) de la escena; si no se encuentra, carga la versión sin compilar (.kag).
        """
        parts = [p.strip() for p in arg.split("|") if p.strip()]
        if len(parts) != 1:
            raise Exception("[ERROR] Formato extendido en @jump_scene no implementado.")
        
        scene_alias = parts[0]
        
        # Determinar el nombre del archivo de escena: si existe en engine.scenes se usa su definición;
        # de lo contrario, se usa directamente el alias.
        if scene_alias in engine.scenes:
            scene_file_name = engine.scenes[scene_alias]
        else:
            scene_file_name = scene_alias

        # Construir la ruta relativa para la versión compilada.
        compiled_path = os.path.join("scenes", f"{scene_file_name}.kagc")
        content = ""
        try:
            file_bytes = engine.resource_manager.get_bytes(compiled_path)
            content = xor_data(file_bytes, key).decode("utf-8", errors="replace")
            print(f"[jump_scene] Cargada escena compilada '{scene_alias}' desde: {compiled_path}")
        except Exception as e:
            # Si falla la carga de la versión compilada, se intenta la versión sin compilar.
            non_compiled_path = os.path.join(engine.game_path, "data", "scenes", f"{scene_file_name}.kag")
            try:
                with open(non_compiled_path, "r", encoding="utf-8") as f:
                    content = f.read()
                print(f"[jump_scene] Cargada escena sin compilar '{scene_alias}' desde: {non_compiled_path}")
            except Exception as e2:
                raise Exception(f"[jump_scene] Error al cargar la escena '{scene_alias}': {e2}")

        print(f"[jump_scene] Saltando a escena '{scene_alias}'.")
        scene_commands = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
        for cmd in scene_commands:
            print(f"[jump_scene] Comando de escena: {cmd}")
            engine.event_manager.handle(cmd, engine)

    
    def handle_char(self, arg, engine):
        """
        The function `handle_char` defines character aliases and display names in a game engine based on
        the input arguments provided.
        
        :param arg: The `arg` parameter in the `handle_char` method is a string that represents the
        input provided to define a character in the engine. It can take the form of either just an alias
        for the character or an alias followed by "as" and the display name in double quotes. The method
        parses
        :param engine: The `engine` parameter in the `handle_char` method seems to be an object that
        contains a `characters` dictionary. This dictionary is used to store aliases and display names
        of characters. The method `handle_char` is responsible for defining characters with their
        aliases and display names in the `engine`
        """
        parts = arg.split(" as ")
        alias = arg.strip()
        if " as " in arg:
            if len(parts) == 2:
                alias = parts[0].strip()
                display_name = parts[1].strip().strip('"')
                engine.characters[alias] = display_name
                print(f"[char] Definido personaje: alias '{alias}', nombre '{display_name}'")
            else:
                print("[char] Formato inválido. Se esperaba: @char alias as \"nombre\"")
        else:
            if alias:
                engine.characters[alias] = alias
                print(f"[char] Definido personaje: alias '{alias}', nombre '{alias}'")
            else:
                print("[char] Formato inválido. Se esperaba: @char alias [as \"nombre\"]")

    def handle_rename(self, arg, engine):
        """
        The function `handle_rename` renames a character in a game engine based on the provided alias
        and new display name.
        
        :param arg: The `arg` parameter in the `handle_rename` method is expected to be a string that
        contains the command for renaming a character. The format of the command should be `@rename
        alias as "NewName"`, where `alias` is the current name of the character to be renamed, and
        :param engine: The `engine` parameter in the `handle_rename` method seems to be an object that
        contains a dictionary of characters where the key is the alias of the character and the value is
        the display name of the character. The method is designed to handle renaming a character by
        updating the display name in the `
        """
 
        if " as " in arg:
            parts = arg.split(" as ")
            if len(parts) == 2:
                alias = parts[0].strip()
                new_display_name = parts[1].strip().strip('"')
                if alias not in engine.characters:
                    raise Exception(f"[rename] El personaje '{alias}' no está definido, no se puede renombrar.")
                engine.characters[alias] = new_display_name
                print(f"[rename] Personaje '{alias}' renombrado a '{new_display_name}'.")
            else:
                raise Exception("[rename] Formato inválido. Se esperaba: @rename alias as \"NuevoNombre\"")
        else:
            raise Exception("[rename] Formato inválido. Se esperaba: @rename alias as \"NuevoNombre\"")
    
    def handle_set(self, arg, engine):
        """
        Updates the value of an already defined variable.
        Syntax: @set variable = "new value".
        If the variable does not exist, an error is thrown.
        """
        parts = arg.split("=")
        if len(parts) != 2:
            raise Exception("[set] Formato inválido. Se esperaba: @set variable = \"nuevo valor\"")
        
        var_name = parts[0].strip()
        new_value = parts[1].strip().strip('"')
        
        if var_name not in engine.vars:
            raise Exception(f"[set] La variable '{var_name}' no está definida. Use @def para definirla.")
        
        engine.vars[var_name] = new_value
        print(f"[set] Variable '{var_name}' actualizada a '{new_value}'.")


    def handle_if(self, arg, engine):
        """
        Evaluates the condition and marks the beginning of a conditional block.
        It is expected that 'arg' is the name of a variable defined with @def.
        The condition is interpreted as true if engine.vars[var] is "true" (ignoring case),
        and false otherwise.
        """
        var_name = arg.strip()
        if not hasattr(engine, "condition_stack"):
            engine.condition_stack = []
        
        if var_name in engine.vars:
            value = engine.vars[var_name].lower()
            condition = (value == "true")
        else:
         
            condition = False
        engine.condition_stack.append(condition)
        print(f"[if] Evaluación de '{var_name}': {condition}")

    def handle_else(self, arg, engine):
        """
        Reverses the condition in the current conditional block.
        """
        if not hasattr(engine, "condition_stack") or not engine.condition_stack:
            raise Exception("[else] No hay bloque if abierto.")
        current = engine.condition_stack.pop()
        engine.condition_stack.append(not current)
        print(f"[else] Se invierte la condición: ahora {not current}")

    def handle_endif(self, arg, engine):
        """
        Closes the current conditional block.
        """
        if not hasattr(engine, "condition_stack") or not engine.condition_stack:
            raise Exception("[endif] No hay bloque if abierto.")
        engine.condition_stack.pop()
        print("[endif] Fin del bloque if.")

    def handle_checkpoint(self, arg, engine):
        """
        Marca un checkpoint en el script actual.
        Se espera la sintaxis:
            @checkpoint <label>
        Se guarda la posición actual del lexer (engine.lexer.current) en engine.checkpoints.
        """
        label = arg.strip()
        if not hasattr(engine, "checkpoints"):
            engine.checkpoints = {}
     
        engine.checkpoints[label] = engine.lexer.current
        print(f"[checkpoint] Checkpoint '{label}' guardado en índice {engine.lexer.current}.")

    def handle_goto(self, arg, engine):
        """
        Salta a un checkpoint previamente definido.
        Se espera la sintaxis:
            @goto <label>
        Se modifica engine.lexer.current para reiniciar la ejecución del script desde el checkpoint.
        """
        label = arg.strip()
        if not hasattr(engine, "checkpoints") or label not in engine.checkpoints:
            raise Exception(f"[goto] Checkpoint '{label}' no existe.")
        print(f"[goto] Antes del salto: engine.lexer.current = {engine.lexer.current}")
        engine.lexer.current = engine.checkpoints[label]
        
        print(f"[goto] Saltando al checkpoint '{label}' (índice {engine.lexer.current}).")
