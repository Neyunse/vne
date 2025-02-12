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
        Registers various event handlers for different events.
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
        print(f"[sprite] Sprite '{sprite_alias}' displayed at position '{position}'.")
    
    def handle_hide_sprite(self, arg, engine):
        """
        Hides a sprite by removing it from the engine's sprite dictionary.
        """
        sprite_alias = arg.strip()
        if hasattr(engine, "sprites") and sprite_alias in engine.sprites:
            del engine.sprites[sprite_alias]
            print(f"[hide] Sprite '{sprite_alias}' hidden.")
        else:
            print(f"[hide] Sprite '{sprite_alias}' not found to hide.")
    
    def handle_exit(self, arg, engine):
        """
        Prints a message and stops the engine.
        """
        print("Event 'exit'", arg)
        engine.running = False
    
    def handle_Load(self, arg, engine):
        """
        Loads and processes KAG/KAGC files.
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
                print(f"[Load] Compiled file loaded: {compiled_arg}")
                engine.loaded_files[compiled_arg] = data
                content = data.decode("utf-8", errors="replace")
            else:
                data = engine.resource_manager.get_bytes(arg)
                print(f"[Load] File loaded: {arg}")
                engine.loaded_files[arg] = data
                content = data.decode("utf-8", errors="replace")
            if any(line.strip().startswith("@") for line in content.splitlines()):
                commands = ScriptLexer(engine.game_path, engine).parse_script(content)
                for cmd in commands:
                    print(f"[Load-Process] Executing command: {cmd}")
                    self.handle(cmd, engine)
        except Exception as e:
            print(f"[Load] Error loading {arg}: {e}")
    
    def handle_scene(self, arg, engine):
        """
        Parses and stores scene aliases and filenames.
        """
        parts = arg.split("=")
        if len(parts) == 2:
            alias = parts[0].strip()
            filename = parts[1].strip().strip('"')
            engine.scenes[alias] = filename
            print(f"[scene] Scene defined: alias '{alias}', file '{filename}'")
        else:
            raise Exception("[ERROR] Invalid format in @scene. Expected: @scene alias = \"file\"")
        
    def handle_define(self, arg, engine):
        """
        Parses and stores variable definitions.
        """
        parts = arg.split("=")
        if len(parts) == 2:
            alias = parts[0].strip()
            filename = parts[1].strip().strip('"')
            engine.vars[alias] = filename
            print(f"[variable] Variable defined: alias '{alias}', file '{filename}'")
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
        print(f"[process_scene] Processing scene '{scene_alias}'.")
        new_lexer = ScriptLexer(engine.game_path, engine)
        new_lexer.commands = new_lexer.parse_script(content)
        new_lexer.original_commands = list(new_lexer.commands)
        new_lexer.current = 0
        engine.lexer = new_lexer
        print(f"[process_scene] New scene loaded with {len(engine.lexer.commands)} commands.")
    
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
            print(f"[jump_scene] Compiled scene '{scene_alias}' loaded from: {compiled_path}")
        except Exception as e:
            non_compiled_path = os.path.join(engine.game_path, "data", "scenes", f"{scene_file_name}.kag")
            try:
                with open(non_compiled_path, "r", encoding="utf-8") as f:
                    content = f.read()
                print(f"[jump_scene] Uncompiled scene '{scene_alias}' loaded from: {non_compiled_path}")
            except Exception as e2:
                raise Exception(f"[jump_scene] Error loading scene '{scene_alias}': {e2}")
        new_lexer = ScriptLexer(engine.game_path, engine)
        new_lexer.commands = new_lexer.parse_script(content)
        new_lexer.original_commands = list(new_lexer.commands)
        new_lexer.current = 0
        engine.lexer = new_lexer
        print(f"[jump_scene] New scene loaded with {len(engine.lexer.commands)} commands.")
        print(f"[jump_scene] Jumping to scene '{scene_alias}'.")
    
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
                print(f"[char] Character defined: alias '{alias}', name '{display_name}'")
            else:
                print("[char] Invalid format. Expected: @char alias as \"name\"")
        else:
            if alias:
                engine.characters[alias] = alias
                print(f"[char] Character defined: alias '{alias}', name '{alias}'")
            else:
                print("[char] Invalid format. Expected: @char alias [as \"name\"]")
    
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
                print(f"[rename] Character '{alias}' renamed to '{new_display_name}'.")
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
        if var_name not in engine.vars:
            raise Exception(f"[set] The variable '{var_name}' is not defined. Use @def to define it.")
        engine.vars[var_name] = new_value
        print(f"[set] Variable '{var_name}' updated to '{new_value}'.")
    
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
        print(f"[if] Evaluation of '{var_name}': {condition}")
    
    def handle_else(self, arg, engine):
        """
        Reverses the condition in the current conditional block.
        """
        if not hasattr(engine, "condition_stack") or not engine.condition_stack:
            raise Exception("[else] No open if block.")
        current = engine.condition_stack.pop()
        engine.condition_stack.append(not current)
        print(f"[else] Condition reversed: now {not current}")
    
    def handle_endif(self, arg, engine):
        """
        Closes the current conditional block.
        """
        if not hasattr(engine, "condition_stack") or not engine.condition_stack:
            raise Exception("[endif] No open if block.")
        engine.condition_stack.pop()
        print("[endif] End of if block.")
    
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
        print(f"[checkpoint] Checkpoint '{label}' saved with line: {checkpoint_line}")
    
    def handle_goto(self, arg, engine):
        """
        Jumps to a specific checkpoint in the script based on the given label.
        """
        label = arg.strip()
        if not hasattr(engine, "checkpoints") or label not in engine.checkpoints:
            raise Exception(f"[goto] Checkpoint '{label}' does not exist.")
        checkpoint_line = engine.checkpoints[label]
        print(f"[goto] Searching for checkpoint line: '{checkpoint_line}'")
        found_index = None
        for i, cmd in enumerate(engine.lexer.original_commands):
            if cmd.strip() == checkpoint_line.strip():
                found_index = i
                break
        if found_index is None:
            raise Exception(f"[goto] Checkpoint line '{checkpoint_line}' not found in the original script.")
        engine.lexer.commands = engine.lexer.original_commands[found_index:]
        engine.lexer.current = 0
        print(f"[goto] Jumping to checkpoint '{label}' in the original script starting at index {found_index}.")
