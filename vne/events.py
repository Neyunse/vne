import io
import os
import pygame
from collections import ChainMap
import re
from vne.lexer import ScriptLexer
from vne.xor_data import xor_data
from vne.config import key
import pickle

class EventManager:
    def __init__(self):
        self.event_handlers = {}
        self.register_default_events()
        self.system_files = [
            "vars.kag", 
            "characters.kag", 
            "ui.kag",
            "scenes.kag"
        ]

    def register_default_events(self):
        """
        Registers various event handlers for different events.
        """
        self.register_event("say", self.handle_say)
        self.register_event("bg", self.handle_bg)
        self.register_event("exit", self.handle_exit)
        self.register_event("Load", self.handle_Load)
        self.register_event("LoadSystem", self.handle_load_system)
        self.register_event("LoadMainMenu", self.handle_load_main_menu)
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
        self.register_event("Display", self.handle_display)
        self.register_event("GameTitle", self.handle_game_title)
        self.register_event("GameIconName", self.handle_game_window_icon)
        self.register_event("SplashScreen", self.handle_splash_screen)
        self.register_event("menu", self.handle_menu)
        self.register_event("button", self.handle_button)
        self.register_event("endMenu", self.handle_endmenu)
        self.register_event("bgm", self.handle_bgm)
        self.register_event("sfx", self.handle_sfx)




        # Command events
        self.register_event("Scene", self.handle_process_scene)
        self.register_event("Set", self.handle_Set_event)
        self.register_event("Quit",  self.handle_exit)

    def register_event(self, event_name, handler):
        """
        Adds a handler to the list of event handlers for the given event name.
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
    
    def handle(self, command, engine=None):
        """
        Processes a command by extracting the event name and argument,
        then dispatching the event to the appropriate handler.
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
        Calls the corresponding event handlers with the provided argument and engine.
        """
        control_commands = {"if", "else", "endif", "checkpoint", "goto"}
        if event_name not in control_commands:
            if hasattr(engine, "condition_stack") and engine.condition_stack:
                if not all(engine.condition_stack):
                    return
        handlers = self.event_handlers.get(event_name, [])
        if not handlers:
            raise Exception(f"[ERROR] No handlers for event '{event_name}'.")
        for handler in handlers:
            handler(arg, engine)

    def substitute_variables(self, text, engine):
        mapping = ChainMap(engine.characters, engine.scenes, engine.vars)
        def replacer(match):
            key = match.group(1).strip()
            return str(mapping.get(key, match.group(0)))
        return re.sub(r'\{([^}]+)\}', replacer, text)
    
    def handle_say(self, arg, engine):
        """
        Processes dialogue for characters, replacing variables with their corresponding values before waiting for user input.
        """
        if ':' in arg:
            speaker, dialogue = arg.split(":", 1)
            speaker = speaker.strip()
            dialogue = dialogue.strip()
            if speaker not in engine.characters:
                raise Exception(f"[ERROR] The character '{speaker}' is not defined.")
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
                    raise Exception(f"[ERROR] The variable for '{key}' is not defined.")
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
                elif key in engine.vars:
                    return engine.vars[key]
                else:
                    raise Exception(f"[ERROR] The variable for '{key}' is not defined.")
            engine.current_dialogue = re.sub(r"\{([^}]+)\}", replacer, engine.current_dialogue)
        engine.wait_for_keypress()
        engine.current_dialogue = ""
        engine.current_character_name = ""
    
    def handle_bg(self, arg, engine):
        """
        Loads and scales a background image.
        """
        load_image = ScriptLexer(engine.game_path, engine).load_image
        relative_path = os.path.join("images", "bg", arg + ".jpg")
        try:
            bg_image = load_image(relative_path)
            bg_image = pygame.transform.scale(bg_image, (engine.renderer.screen.get_width(),
                                                         engine.renderer.screen.get_height()))
            engine.current_bg = bg_image
        except Exception as e:
            raise Exception(f"[bg] Error loading background image: {e}")
    
    def handle_splash_screen(self, arg, engine):
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        arg = arg.strip('"').strip("'")

        if not arg:
            arg = "splash"

        load_image = ScriptLexer(engine.game_path, engine).load_image
        relative_path = os.path.join("ui", arg + ".jpg")

        try:
            bg_image = load_image(relative_path)
            bg_image = pygame.transform.scale(bg_image, (engine.renderer.screen.get_width(),
                                                         engine.renderer.screen.get_height()))
    
        except Exception as e:
            raise Exception(f"[bg] Error loading splash image: {e}")
        
        engine.renderer.screen.blit(bg_image, (0, 0))
        pygame.display.flip()

         
        splash_duration = 2000   
        start_time = pygame.time.get_ticks()
        while engine.running and pygame.time.get_ticks() - start_time < splash_duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    engine.running = False
                    return
             
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return
     
    def handle_sprite(self, arg, engine):
        """
        Loads and stores a sprite image with a specified alias and position.
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
        engine.Log(f"[sprite] Sprite '{sprite_alias}' displayed at position '{position}'.")
    
    def handle_hide_sprite(self, arg, engine):
        """
        Hides a sprite by removing it from the engine's sprite dictionary.
        """
        sprite_alias = arg.strip()
        if hasattr(engine, "sprites") and sprite_alias in engine.sprites:
            del engine.sprites[sprite_alias]
            engine.Log(f"[hide] Sprite '{sprite_alias}' hidden.")
        else:
            engine.Log(f"[hide] Sprite '{sprite_alias}' not found to hide.")
    
    def handle_exit(self, arg, engine):
        """
        Prints a message and stops the engine.
        """
        engine.Log("Event 'exit'", arg)
        engine.running = False
    
    def handle_Load(self, arg, engine):
        """
        Loads and processes KAG/KAGC files.
        """
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        arg = arg.strip('"').strip("'")
        force_compiled = any(keyword in arg.lower() for keyword in self.system_files)
        try:
            if force_compiled:
                if not arg.lower().endswith(".kagc"):
                    compiled_arg = arg[:-4] + ".kagc"
                else:
                    compiled_arg = arg
                data = engine.resource_manager.get_bytes(compiled_arg)
                data = xor_data(data, key)
                engine.Log(f"[Load] Compiled file loaded: {compiled_arg}")
                engine.loaded_files[compiled_arg] = data
                content = data.decode("utf-8", errors="replace")

            else:
                data = engine.resource_manager.get_bytes(arg)
                engine.Log(f"[Load] File loaded: {arg}")
                engine.loaded_files[arg] = data
                content = data.decode("utf-8", errors="replace")
            if any(line.strip().startswith("@") for line in content.splitlines()):
                commands = ScriptLexer(engine.game_path, engine).parse_script(content)
                for cmd in commands:
                    engine.Log(f"[Load-Process] Executing command: {cmd}")
                    self.handle(cmd, engine)
        except Exception as e:
            raise Exception(f"[Load] Error loading {arg}: {e}")
    
    def handle_load_system(self, arg, engine):
        for file in self.system_files:
            self.handle_Load(f'("system/{file}")', engine)
    
    def handle_load_main_menu(self, arg, engine):
        if not "main_menu.kag" in self.system_files:
            self.system_files.append("main_menu.kag")
        self.handle_Load('("system/main_menu.kag")', engine)
    
    def handle_scene(self, arg, engine):
        """
        Parses and stores scene aliases and filenames.
        """
        parts = arg.split("=")
        if len(parts) == 2:
            alias = parts[0].strip()
            filename = parts[1].strip().strip('"')
            engine.scenes[alias] = filename
            engine.Log(f"[scene] Scene defined: alias '{alias}', file '{filename}'")
        else:
            raise Exception("[ERROR] Invalid format in @scene. Expected: @scene alias = \"file\"")
        
    def handle_define(self, arg, engine):
        """
        Parses and stores variable definitions.
        """
        parts = arg.split("=")
        if len(parts) == 2:
            alias = parts[0].strip()
            var = parts[1].strip().strip('"')
            string_var = self.substitute_variables(var, engine)

            engine.vars[alias] = string_var
            engine.Log(f"[variable] Variable defined: alias '{alias}', file '{string_var}'")
        else:
            raise Exception("[ERROR] Invalid format in @def. Expected: @def alias = \"value\"")
    
    def handle_process_scene(self, arg, engine):
        """
        Processes a scene by loading and parsing a script file based on the scene alias.
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
            raise Exception(f"[ERROR] Compiled version of the script for '{base_name}' not found: {e}")
        engine.Log(f"[process_scene] Processing scene '{scene_alias}'.")
        new_lexer = ScriptLexer(engine.game_path, engine)
        new_lexer.commands = new_lexer.parse_script(content)
        new_lexer.original_commands = list(new_lexer.commands)
        new_lexer.current = 0
        engine.lexer = new_lexer
        engine.Log(f"[process_scene] New scene loaded with {len(engine.lexer.commands)} commands.")
    
    def handle_jump_scene(self, arg, engine):
        """
        Processes the scene jump command.
        """
        parts = [p.strip() for p in arg.split("|") if p.strip()]
        if len(parts) != 1:
            raise Exception("[ERROR] Extended format in @jump_scene not implemented.")
        scene_alias = parts[0]
        if scene_alias in engine.scenes:
            scene_file_name = engine.scenes[scene_alias]
        else:
            scene_file_name = scene_alias
        compiled_path = os.path.join("scenes", f"{scene_file_name}.kagc")
        content = ""
        try:
            file_bytes = engine.resource_manager.get_bytes(compiled_path)
            content = xor_data(file_bytes, key).decode("utf-8", errors="replace")
            engine.Log(f"[jump_scene] Compiled scene '{scene_alias}' loaded from: {compiled_path}")
        except Exception as e:
            non_compiled_path = os.path.join(engine.game_path, "data", "scenes", f"{scene_file_name}.kag")
            try:
                with open(non_compiled_path, "r", encoding="utf-8") as f:
                    content = f.read()
                engine.Log(f"[jump_scene] Uncompiled scene '{scene_alias}' loaded from: {non_compiled_path}")
            except Exception as e2:
                raise Exception(f"[jump_scene] Error loading scene '{scene_alias}': {e2}")
        new_lexer = ScriptLexer(engine.game_path, engine)
        new_lexer.commands = new_lexer.parse_script(content)
        new_lexer.original_commands = list(new_lexer.commands)
        new_lexer.current = 0
        engine.lexer = new_lexer
        engine.Log(f"[jump_scene] New scene loaded with {len(engine.lexer.commands)} commands.")
        engine.Log(f"[jump_scene] Jumping to scene '{scene_alias}'.")
    
    def handle_char(self, arg, engine):
        """
        Defines character aliases and display names.
        """
        parts = arg.split(" as ")
        alias = arg.strip()
        if " as " in arg:
            if len(parts) == 2:
                alias = parts[0].strip()
                display_name = parts[1].strip().strip('"')
                engine.characters[alias] = display_name
                engine.Log(f"[char] Character defined: alias '{alias}', name '{display_name}'")
            else:
                raise Exception("[char] Invalid format. Expected: @char alias as \"name\"")
        else:
            if alias:
                engine.characters[alias] = alias
                engine.Log(f"[char] Character defined: alias '{alias}', name '{alias}'")
            else:
                raise Exception("[char] Invalid format. Expected: @char alias [as \"name\"]")
    
    def handle_rename(self, arg, engine):
        """
        Renames a character based on the provided alias and new display name.
        """
        if " as " in arg:
            parts = arg.split(" as ")
            if len(parts) == 2:
                alias = parts[0].strip()
                new_display_name = parts[1].strip().strip('"')
                if alias not in engine.characters:
                    raise Exception(f"[rename] Character '{alias}' is not defined, cannot rename.")
                engine.characters[alias] = new_display_name
                engine.Log(f"[rename] Character '{alias}' renamed to '{new_display_name}'.")
            else:
                raise Exception("[rename] Invalid format. Expected: @rename alias as \"NewName\"")
        else:
            raise Exception("[rename] Invalid format. Expected: @rename alias as \"NewName\"")
    
    def handle_set(self, arg, engine):
        """
        Updates the value of an already defined variable.
        Syntax: @set variable = "new value".
        """
        parts = arg.split("=")
        if len(parts) != 2:
            raise Exception("[set] Invalid format. Expected: @set variable = \"new value\"")
        var_name = parts[0].strip()
        new_value = parts[1].strip().strip('"')

        if var_name in engine.characters:
            raise Exception(f"[set] The variable '{var_name}' cannot be modified as it is an already defined character!")
        
        if var_name in engine.scenes:
            raise Exception(f"[set] The variable '{var_name}' cannot be modified as it is an already defined scene!")
        
        if var_name not in engine.vars:
            raise Exception(f"[set] The variable '{var_name}' is not defined. Use @def to define it.")

        
        new_value = self.substitute_variables(new_value, engine)

        engine.vars[var_name] = new_value
        engine.Log(f"[set] Variable '{var_name}' updated to '{new_value}'.")
    
    def handle_if(self, arg, engine):
        """
        Evaluates the condition and marks the beginning of a conditional block.
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
        engine.Log(f"[if] Evaluation of '{var_name}': {condition}")
    
    def handle_else(self, arg, engine):
        """
        Reverses the condition in the current conditional block.
        """
        if not hasattr(engine, "condition_stack") or not engine.condition_stack:
            raise Exception("[else] No open if block.")
        current = engine.condition_stack.pop()
        engine.condition_stack.append(not current)
        engine.Log(f"[else] Condition reversed: now {not current}")
    
    def handle_endif(self, arg, engine):
        """
        Closes the current conditional block.
        """
        if not hasattr(engine, "condition_stack") or not engine.condition_stack:
            raise Exception("[endif] No open if block.")
        engine.condition_stack.pop()
        engine.Log("[endif] End of if block.")
    
    def handle_checkpoint(self, arg, engine):
        """
        Saves a checkpoint with a label and the current script line.
        """
        label = arg.strip()
        if not hasattr(engine, "checkpoints"):
            engine.checkpoints = {}
        if engine.lexer.current < len(engine.lexer.original_commands):
            checkpoint_line = engine.lexer.original_commands[engine.lexer.current]
        else:
            checkpoint_line = engine.lexer.original_commands[-1]
        engine.checkpoints[label] = checkpoint_line
        engine.Log(f"[checkpoint] Checkpoint '{label}' saved with line: {checkpoint_line}")
    
    def handle_goto(self, arg, engine):
        """
        Jumps to a specific checkpoint in the script based on the given label.
        """
        label = arg.strip()
        if not hasattr(engine, "checkpoints") or label not in engine.checkpoints:
            raise Exception(f"[goto] Checkpoint '{label}' does not exist.")
        checkpoint_line = engine.checkpoints[label]
        engine.Log(f"[goto] Searching for checkpoint line: '{checkpoint_line}'")
        found_index = None
        for i, cmd in enumerate(engine.lexer.original_commands):
            if cmd.strip() == checkpoint_line.strip():
                found_index = i
                break
        if found_index is None:
            raise Exception(f"[goto] Checkpoint line '{checkpoint_line}' not found in the original script.")
        engine.lexer.commands = engine.lexer.original_commands[found_index:]
        engine.lexer.current = 0
        engine.Log(f"[goto] Jumping to checkpoint '{label}' in the original script starting at index {found_index}.")

    def handle_game_title(self, arg, engine):
        """
        The function `handle_game_title` trims and sets the game title for a Pygame window.
        
        :param arg: The `arg` parameter in the `handle_game_title` function is a string representing the
        title of a game. The function is responsible for processing and setting the game title to the
        provided argument. The function first removes any leading or trailing whitespaces from the
        argument. Then, it checks if the argument
        :param engine: The `handle_game_title` function takes three parameters: `self`, `arg`, and
        `engine`. In this function, the `arg` parameter is a string representing the title of a game.
        The function first removes any leading or trailing whitespace from the `arg` string using the
        `strip()`
        """
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        arg = arg.strip('"').strip("'")

        pygame.display.set_caption(arg)
    
    def handle_game_window_icon(self, arg, engine):
        """
        This function handles loading and setting the window icon for a game using Pygame in Python.
        
        :param arg: The `arg` parameter in the `handle_game_window_icon` function seems to represent the
        name of the icon file without the file extension. The function then attempts to load an image
        file with the given name from the "ui/icon" directory with a ".jpg" extension and set it as the
        icon
        :param engine: The `engine` parameter in the `handle_game_window_icon` function seems to be an
        instance of some class that has a property or method called `game_path`. This property or method
        is used to construct the path to the game resources
        """
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        arg = arg.strip('"').strip("'")

        if not arg:
            arg = "window_icon"
    
        load_image = ScriptLexer(engine.game_path, engine).load_image

        relative_path = os.path.join("ui","icon", arg + ".jpg")

        try:
            icon = load_image(relative_path)
            pygame.display.set_icon(icon)
 
        except Exception as e:
            raise Exception(f"[Icon] Error loading the window icon: {e}")
        

    def handle_display(self, arg, engine):
        """
        Configures the window size and updates the configuration of the interface elements.
        The syntax is expected:
            @Display(800,800)
        where the numbers indicate the desired width and height, but are limited to the maximum of the monitor.
      
        """
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        parts = arg.split(",")
        if len(parts) != 2:
            raise Exception("[Display] Invalid format. Expected: @Display(width,height)")
        try:
            width = int(parts[0].strip())
            height = int(parts[1].strip())
        except ValueError:
            raise Exception("[Display] The dimensions must be whole numbers.")

    
 
        engine.config["screen_width"] = width
        engine.config["screen_height"] = height
        
        current_namebox_cfg = engine.config.get("namebox_rect", {})

        current_dialogue_cfg = engine.config.get("dialogue_rect", {})
        engine.config["dialogue_rect"] = {
            "x": int(width * 0.05),
            "y": int(height * 0.79),
            "width": int(width * 0.90),
            "height": int(height * 0.20),
            "bg_color": current_dialogue_cfg.get("bg_color", (50, 50, 50)),
            "border_color": current_dialogue_cfg.get("border_color", (255, 255, 255))
        }


        # Calcular el rectángulo del namebox basándose en el diálogo:
        # Se posiciona justo encima del cuadro de diálogo, con un margen (por ejemplo, 5 píxeles).
        namebox_height = engine.renderer.name_font.get_height()
        margin = 23
        # La coordenada Y se basa en dialogue_rect["y"] menos la altura del namebox y el margen.
        namebox_y = engine.config["dialogue_rect"]["y"] - namebox_height - margin

        engine.config["namebox_rect"] = {
            "x": int(width * 0.05),
            "y": namebox_y,
            "width": int(width * 0.2),
            "height": int(engine.renderer.name_font.get_height() * 2),
            "bg_color": current_namebox_cfg.get("bg_color", (50, 50, 50)),
            "border_color": current_namebox_cfg.get("border_color", (255, 255, 255))
        }

        
 
 
        engine.renderer.screen = pygame.display.set_mode((width, height))
        
        engine.Log(f"[Display] Window set to {width}x{height}.")

    def handle_menu(self, arg, engine):
        """
        Starts a menu block.
        It is expected that, after this command, @button commands will be issued to define the options.
        """
        engine.current_menu_buttons = []
        engine.Log("[menu] Menu block started.")

    def handle_button(self, arg, engine):
        """
        The function `handle_button` parses a string argument to extract a label and an event action,
        then adds them to a list in the `engine` object.
        
        :param arg: The `arg` parameter in the `handle_button` function is a string that represents the
        input provided by the user. It is expected to be in a specific format: "@button "Label" event
        <command>". The function then processes this input to extract the label and event command
        associated with a button
        :param engine: The `engine` parameter in the `handle_button` method seems to be an object that is
        used to store information related to the current menu buttons. It is used to keep track of the
        buttons that have been added to the menu so far. The method checks if the `engine` object has an
        """
     
        pattern = r'^"([^"]+)"\s+event\s+(.+)$'
        arg = arg.strip()
        match = re.match(pattern, arg)
        if not match:
            raise Exception('[button] Invalid format. Expected: @button "Label" event <command>.')
        raw_label = match.group(1)
        action = match.group(2).strip()
        if not hasattr(engine, "current_menu_buttons"):
            engine.current_menu_buttons = []
      
        engine.current_menu_buttons.append({"raw_label": raw_label, "event": action})
        engine.Log(f"[button] Button added: '{raw_label}'. -> '{action}'")

    def handle_endmenu(self, arg, engine):
        """
        The function `handle_endmenu` in Python handles the display and interaction with a menu
        interface within a game engine.
        
        :param arg: The `arg` parameter in the `handle_endmenu` method seems to be unused in the
        provided code snippet. It is defined as a parameter but not referenced or utilized within the
        method. If you intended to use this parameter for some specific functionality or logic within
        the method, you may need to update
        :param engine: The `engine` parameter in the `handle_endmenu` method seems to be an object that
        contains various properties and methods related to the game engine. It is used to access
        configuration settings, handle events, render graphics, and manage the game state
        """
       
        clock = engine.clock

        if not hasattr(engine, "current_menu_buttons") or not engine.current_menu_buttons:
            raise Exception("[endmenu] There are no buttons defined in the menu.")

         
        screen_width = engine.config.get("screen_width", 800)
        screen_height = engine.config.get("screen_height", 600)
        panel_width = int(screen_width * 0.5)
        button_height = 40
        margin = 10
        panel_height = len(engine.current_menu_buttons) * (button_height + margin) + margin
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
   
        panel_bg_color = (50, 50, 50, 200)
        border_color = (255, 255, 255)
        font = engine.renderer.font

   
        buttons = []
        for i, btn in enumerate(engine.current_menu_buttons):
  
            label_text = self.substitute_variables(btn["raw_label"], engine)
            text_surface = font.render(label_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            btn_y = margin + i * (button_height + margin)
            btn_rect = pygame.Rect(0, btn_y, panel_width, button_height)
            text_rect.center = btn_rect.center
            buttons.append({"rect": btn_rect, "event": btn["event"], "text": text_surface, "text_rect": text_rect})
        
        selected_action = None
        running_menu = True
        while running_menu and engine.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    engine.running = False
                    running_menu = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if panel_rect.collidepoint(mouse_x, mouse_y):
                        local_x = mouse_x - panel_x
                        local_y = mouse_y - panel_y
                        for btn in buttons:
                            if btn["rect"].collidepoint(local_x, local_y):
                                selected_action = btn["event"]
                                running_menu = False
                                break
    
            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel_surface.fill(panel_bg_color)
            pygame.draw.rect(panel_surface, border_color, panel_surface.get_rect(), 2)
            for btn in buttons:
                pygame.draw.rect(panel_surface, (100, 100, 100), btn["rect"])
                pygame.draw.rect(panel_surface, border_color, btn["rect"], 2)
                panel_surface.blit(btn["text"], btn["text_rect"])
            engine.renderer.draw_background()
            engine.renderer.screen.blit(panel_surface, (panel_x, panel_y))
            pygame.display.update()
            clock.tick(30)
        
        if selected_action:
            if not selected_action.startswith("@"):
                selected_action = "@" + selected_action
            engine.Log(f"[menu] Selected action: {selected_action}")
            self.handle(selected_action, engine)

    def handle_Set_event(self, arg, engine):
        """
        Updates the value of a defined variable using the syntax:

            Set(variable, value)

        For example:
            @button "Exit" action Set(chek, true).

        This command extracts the variable name and the new value, and then assigns it in engine.vars.
        """
        arg = arg.strip()
         
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        parts = arg.split(",")
        if len(parts) != 2:
            raise Exception("[Set] Invalid format. Expected: Set(variable, value)")
        
        var_name = parts[0].strip()
        new_value = parts[1].strip().strip('"')
        
        if var_name in engine.characters:
            raise Exception(f"[Set] The variable '{var_name}' cannot be modified as it is an already defined character!")
        
        if var_name in engine.scenes:
            raise Exception(f"[Set] The variable '{var_name}' cannot be modified as it is an already defined scene!")
        
        if var_name not in engine.vars:
            raise Exception(f"[Set] The variable '{var_name}' is not defined. Use @def to define it.")
        

        new_value = self.substitute_variables(new_value, engine)
        
        engine.vars[var_name] = new_value
        engine.Log(f"[Set] Variable '{var_name}' updated to '{new_value}'.")



    
    # TODO: IMPLEMENT SAVE AND LOAD

    def handle_save(self, arg, engine):
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        engine.vars["continue"] = "true"
        state = {
            "vars": engine.vars,
            "characters": engine.characters,
            "scenes": engine.scenes,
            "lexer_current": engine.lexer.current,
            "original_commands": engine.lexer.original_commands,
            "checkpoints": engine.checkpoints if hasattr(engine, "checkpoints") else {},
        }
        file = f"{engine.game_path}/data.save"
        try:
            with open(file, "wb") as f:
                pickle.dump(state, f)
            print(f"[save] Game saved to '{file}'.")
        except Exception as e:
            raise Exception(f"[save] Error saving game: {e}")
    
 

    def handle_load_save(self, arg, engine):
        """
        Loads the game status from a file.
   
        """
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        try:
            file = f"{engine.game_path}/data.save"

            with open(file, "rb") as f:
                state = pickle.load(f)
            engine.vars = state.get("vars", {})
            engine.characters = state.get("characters", {})
            engine.scenes = state.get("scenes", {})
            
            if "original_commands" in state and "lexer_current" in state:
                engine.lexer.original_commands = state["original_commands"]
                engine.lexer.commands = state["original_commands"][state["lexer_current"]:]
                engine.lexer.current = 0
            engine.checkpoints = state.get("checkpoints", {})
            print(f"[load] Game loaded from '{file}'.")

        except Exception as e:
            raise Exception(f"[load] Error loading game: {e}")

    def handle_bgm(self, arg, engine):
        """
        Plays looping background music using a file located at:
        data/audio/bgm/<filename>.mp3.
        The files can be in data/loose or inside data.pkg.
        The ResourceManager is used to get the bytes and the sound is loaded from a BytesIO.
        Fade out is applied in case something is already playing and fade in when starting the new track.
        """
        filename = arg.strip()
        rel_path = os.path.join("audio", "bgm", filename + ".mp3")
        try:
            data_bytes = engine.resource_manager.get_bytes(rel_path)
            bgm_sound = pygame.mixer.Sound(io.BytesIO(data_bytes))
        except Exception as e:
            raise Exception(f"[bgm] Error loading background music from '{rel_path}': {e}")
        
        bgm_channel_number = engine.config.get("bgm_channel", 0)
        bgm_channel = pygame.mixer.Channel(bgm_channel_number)
        
        if bgm_channel.get_busy():
            bgm_channel.fadeout(2000)
            pygame.time.delay(2000)
            bgm_channel.stop()

        bgm_channel.play(bgm_sound, loops=-1, fade_ms=2000)
        bgm_channel.set_volume(0.6)
        engine.Log(f"[bgm] Background music '{filename}' playing on channel {bgm_channel_number} with fade in.")

    def handle_sfx(self, arg, engine):
        """
        Plays a sound effect using a file located at:
        data/audio/sfx/<filename>.wav.
        The files can be in data/loose or inside data.pkg.
        The ResourceManager is used to get the bytes and the sound is loaded from a BytesIO.
        If the channel is already playing another sound, a fade out (500 ms) is applied before playing the new sound.
        with a fade in of 500 ms.
        """
        filename = arg.strip()
        rel_path = os.path.join("audio", "sfx", filename + ".mp3")
        try:
            data_bytes = engine.resource_manager.get_bytes(rel_path)
            sfx_sound = pygame.mixer.Sound(io.BytesIO(data_bytes))
        except Exception as e:
            raise Exception(f"[sfx] Error loading sound effect from '{rel_path}': {e}")
        
        sfx_channel_number = engine.config.get("sfx_channel", 1)
        sfx_channel = pygame.mixer.Channel(sfx_channel_number)
        
        if sfx_channel.get_busy():
            sfx_channel.fadeout(500)  # Fade out en 500 ms si el canal ya está ocupado
            pygame.time.delay(500)    # Esperar 500 ms para que se complete el fade out
        
        sfx_channel.play(sfx_sound, fade_ms=500)  # Reproducir con fade in de 500 ms
        sfx_channel.set_volume(1.0)

        engine.Log(f"[sfx] Sound effect '{filename}' played on channel {sfx_channel_number} with fade in.")
