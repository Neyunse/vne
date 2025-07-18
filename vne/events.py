import io
import os
import pygame
 
from collections import ChainMap
import re
from vne.lexer import ScriptLexer
from vne.aes import AES
from vne.config import (key, file_extension, aes_extension, bundle_extension,
                        engine_version)
import pickle
from vne.Audio import Audio
from vne.visual import VisualElement, Button, MenuPanel, VerticalLayout, DialogPanel, SpriteVisual
from vne.visual import SpriteVisual
from vne.visual import FadeAnimation, SlideAnimation

QUICKSAVE_SLOT = "__quicksave__"

class EventManager:
    def __init__(self):
        self.event_handlers = {}
        self.register_default_events()
        self.system_files = [
            f"vars{file_extension}", 
            f"characters{file_extension}", 
            f"ui{file_extension}",
            f"scenes{file_extension}"
        ]
 

    def register_default_events(self):
        """
        The function `register_default_events` registers various event handlers for different actions in
        a game engine.
        """
  
        # Primitive
        self.register_event("say", self.handle_say)
        self.register_event("end", self.handle_end)
        self.register_event("process_scene", self.handle_process_scene)

        # Importing/Loading & StartUp/init
        self.register_event("Load", self.handle_Load)
        self.register_event("LoadSystem", self.handle_load_system)
        self.register_event("LoadMainMenu", self.handle_load_main_menu)
        self.register_event("SplashScreen", self.handle_splash_screen)
        
        # Scenes Flow
        self.register_event("jump_scene", self.handle_jump_scene)
        self.register_event("checkpoint", self.handle_checkpoint)
        self.register_event("goto", self.handle_goto)
        
        # Variable definitions
        self.register_event("char", self.handle_char)
        self.register_event("scene", self.handle_scene)
        self.register_event("def", self.handle_define)

        # Mutations
        self.register_event("set", self.handle_set)
        self.register_event("rename", self.handle_rename)

        # Images
        self.register_event("bg", self.handle_bg)
        self.register_event("sprite", self.handle_sprite)
        self.register_event("hide", self.handle_hide_sprite)
        
        # Audio
        self.register_event("bgm", self.handle_bgm)
        self.register_event("sfx", self.handle_sfx)

        # Configurations
        self.register_event("Display", self.handle_display)
        self.register_event("GameTitle", self.handle_game_title)
        self.register_event("GameIconName", self.handle_game_window_icon)
        
        # Conditional flags
        self.register_event("if", self.handle_if)
        self.register_event("else", self.handle_else)
        self.register_event("endif", self.handle_endif)

        # Menu
        self.register_event("mainMenu", self.handle_menu)
        self.register_event("button", self.handle_button)
        self.register_event("endMainMenu", self.handle_endmenu)
        
        # quick menu
        self.register_event("qm", self.handle_qm)
        self.register_event("qmBtn", self.handle_qm_button)
        self.register_event("qmEnd", self.handle_qm_end)

        # choices
        self.register_event("choice", self.handle_choice_menu)
        self.register_event("option", self.handle_option_button)
        self.register_event("end_choice", self.handle_end_choice)

        # Events
        self.register_event("Scene", self.handle_process_scene)
        self.register_event("Set", self.handle_Set_event)
        self.register_event("Quit", self.handle_Quit)
        
        #TOOLS
        
        self.register_event("Log", self.handle_log)
        self.register_event("Save", self.handle_save)
        self.register_event("Continue", self.handle_load_save)
    
    def handle_log(self, arg, engine):
        arg = arg.strip()
        mapping = ChainMap(engine.characters, engine.scenes, engine.vars)
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()

            # String log
            if arg.startswith('"')  and arg.endswith('"'):
                arg = arg.strip('"').strip("'")
                vrs = self.substitute_variables(arg, engine)
                engine.Log(f"[Log] {vrs}")
                print(f"[Log] {vrs}")
            else:
                engine.Log(f"[Log] {mapping[arg]}")
                print(f"[Log] {mapping[arg]}")
                

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

        if engine is not None and hasattr(engine, "should_execute_line"):
            is_conditional_command = command.startswith("@if") or command.startswith("@else") or command.startswith("@endif")
            if not engine.should_execute_line() and not is_conditional_command:
                return

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
        # Instead of setting engine.current_dialogue, show a DialogPanel overlay
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
        elif '*' in arg:
            speaker, dialogue = arg.split("*", 1)
            speaker = speaker.strip()
            dialogue = dialogue.strip()
            engine.current_character_name = speaker
            def replacer(match):
                key = match.group(1).strip()
                if key in speaker:
                    return speaker
                elif key in engine.characters:
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
        # Usar un único DialogPanel persistente y mantenerlo siempre visible
        font = engine.renderer.font
        name_font = getattr(engine.renderer, 'name_font', font)
        screen_w = engine.config.get("screen_width", 800)
        screen_h = engine.config.get("screen_height", 600)
        padding = 35
        panel_x = padding
        panel_y = screen_h - 120 - padding
        panel_width = screen_w - 2 * padding
        panel_height = 120
        if not hasattr(engine, "current_dialog_panel") or engine.current_dialog_panel is None:
            engine.current_dialog_panel = DialogPanel("", font=font, x=panel_x, y=panel_y, width=panel_width, height=panel_height)
            engine.current_dialog_panel.name_font = name_font
            engine.screen_manager.show(engine.current_dialog_panel, force_top=True)
        panel = engine.current_dialog_panel
        panel.z_index = 10
        panel.text = ""
        # Mostrar nombre del personaje si existe
        if engine.current_character_name:
            panel.character_name = engine.current_character_name
            panel.name_font = name_font
        else:
            panel.character_name = None
        if panel not in engine.screen_manager.screens:
            engine.screen_manager.show(panel, force_top=True)
        # Efecto máquina de escribir
        full_text = engine.current_dialogue
        text_cps = 30
        typewriter_index = 0
        last_update = pygame.time.get_ticks()
        mostrar_todo = False
        waiting = True
        # Control de texto visto (estricto: incluye nombre, texto, y snapshot de variables)
        if not hasattr(engine, "seen_dialogue"):
            engine.seen_dialogue = set()
        scene_id = getattr(engine, "current_scene", None) or engine.vars.get("scene", "")
        context_vars = tuple(sorted((k, str(v)) for k, v in engine.vars.items()))
        key_seen = (scene_id, engine.current_character_name, engine.current_dialogue, context_vars)
        while waiting and engine.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    engine.running = False
                    waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Primero dejar que los paneles manejen el evento
                    handled = engine.screen_manager.handle_event(event)
                    if handled:
                        # El evento fue consumido por un panel, no avanzar el diálogo
                        continue
                    # Si no fue manejado, entonces avanzamos el diálogo
                    if typewriter_index < len(full_text):
                        mostrar_todo = True
                    else:
                        waiting = False
                else:
                    engine.screen_manager.handle_event(event)
            now = pygame.time.get_ticks()
            if typewriter_index < len(full_text):
                if mostrar_todo:
                    typewriter_index = len(full_text)
                    panel.text = full_text
                else:
                    chars_to_add = int((now - last_update) * text_cps / 1000)
                    if chars_to_add > 0:
                        typewriter_index = min(typewriter_index + chars_to_add, len(full_text))
                        panel.text = full_text[:typewriter_index]
                        last_update = now
            engine.clock.tick(30)
            engine.screen_manager.render(engine.renderer.screen)
            pygame.display.update()
        engine.seen_dialogue.add(key_seen)
        engine.current_dialogue = ""
        engine.current_character_name = ""

    def handle_bg(self, arg, engine):
        """
        Loads and scales a background image to fit the window, manteniendo aspecto.
        """
        engine.current_bg_filename = arg
        load_image = ScriptLexer(engine.game_path, engine).load_image
        relative_path = os.path.join("images", "bg", arg + ".jpg")
        try:
            bg_image = load_image(relative_path)
            # Obtener tamaño de ventana
            win_w = engine.renderer.screen.get_width()
            win_h = engine.renderer.screen.get_height()
            img_w, img_h = bg_image.get_width(), bg_image.get_height()
            scale = min(win_w / img_w, win_h / img_h)
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            scaled_bg = pygame.transform.smoothscale(bg_image, (new_w, new_h))
            # Centrar
            bg_visual = SpriteVisual(scaled_bg, x=(win_w-new_w)//2, y=(win_h-new_h)//2, width=new_w, height=new_h)
            engine.current_bg_visual = bg_visual
            # Show as background overlay (lowest layer)
            if hasattr(engine, "bg_layer"):
                engine.screen_manager.hide(engine.bg_layer)
            engine.bg_layer = bg_visual
            engine.screen_manager.screens.insert(0, bg_visual)
        except Exception as e:
            raise Exception(f"[bg] Error loading background image: {e}")
    
    def handle_splash_screen(self, arg, engine):
        """
        This function handles displaying a splash screen image for a specified duration in a Python game
        engine.
        
        :param arg: The `arg` parameter in the `handle_splash_screen` function is used to specify the
        name of the splash screen image file to be displayed. It is processed to remove any leading or
        trailing whitespace, parentheses, single quotes, or double quotes. If `arg` is empty after
        processing, the
        :param engine: The `engine` parameter in the `handle_splash_screen` function seems to be an
        object that contains information and functionality related to the game engine. It is used to
        access the game path, load images, and interact with the game renderer and screen. The `engine`
        object is crucial for displaying
        :return: The function `handle_splash_screen` returns either when the user closes the window (by
        clicking the close button) or when the user presses a key or clicks the mouse during the splash
        screen display.
        """
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
        Loads and stores a sprite image with a specified alias, position y animación.
        Sintaxis: @sprite personaje at left fadein
        Sintaxis: @sprite personaje at x=100,y=200 slidein
        """
        load_image = ScriptLexer(engine.game_path, engine).load_image
        parts = arg.split(" at ")
        sprite_alias = parts[0].strip()
        position = "center"
        animation = None
        if len(parts) > 1:
            # Permitir: at <pos> <anim>
            pos_anim = parts[1].strip().split()
            if len(pos_anim) == 2:
                position, anim = pos_anim
            elif len(pos_anim) == 1:
                position, anim = pos_anim[0], None
            else:
                position, anim = "center", None
            # Animaciones básicas
            if anim == "fadein":
                animation = FadeAnimation(fade_in=True, duration=0.5)
            elif anim == "fadeout":
                animation = FadeAnimation(fade_in=False, duration=0.5)
                
            # elif anim == "slidein":
          
            #     animation = SlideAnimation(direction="left", duration=0.5)
            # elif anim == "slideout":
          
            #     animation = SlideAnimation(direction="right", duration=0.5)
        relative_path = os.path.join("images", "sprites", sprite_alias + ".png")
        try:
            sprite_image = load_image(relative_path)
            
            sprite_visual = SpriteVisual(sprite_image, position=position, animation=animation)
            sprite_visual.z_index = 1
  
            # TODO: THIS DON'T WORK CORRECTLY WITH @HIDE  
            # if sprite_alias in engine.sprite_layers:
            #     engine.screen_manager.hide(engine.sprite_layers[sprite_alias])
            
            engine.sprite_layers[sprite_alias] = sprite_visual
            engine.screen_manager.show(sprite_visual)
        except Exception as e:
            raise Exception(f"[sprite] {e}")

    def handle_hide_sprite(self, arg, engine):
        """
        Hides a sprite from the screen and removes it from the sprite_layers dictionary.
        """
        sprite_alias = arg.strip()

        if not sprite_alias:
            engine.Log("[hide] Error: No sprite alias provided.")
            return

        if not hasattr(engine, "sprite_layers"):
            engine.Log("[hide] Error: Engine has no 'sprite_layers' attribute.")
            return

        sprite = engine.sprite_layers.get(sprite_alias)
        if not sprite:
            engine.Log(f"[hide] Warning: Sprite '{sprite_alias}' not found.")
            return

        try:
            # Hide the sprite visually
            engine.screen_manager.hide(sprite)

            # Remove the sprite from the dictionary
            del engine.sprite_layers[sprite_alias]

            engine.Log(f"[hide] Sprite '{sprite_alias}' hidden and removed from sprite_layers.")
        except Exception as e:
            engine.Log(f"[hide] Error while hiding sprite '{sprite_alias}': {e}")

    def handle_Quit(self, arg, engine):
        """
        Prints a message and stops the engine.
        """
        engine.Log("Event 'exit'", arg)
        engine.running = False
    
    def handle_end(self, arg, engine):
        """
        Returns to the main menu by clearing all visual elements (sprites, overlays)
        and applying a dissolve-to-black effect.
        """
        
        # hide all sprites and overlays 
        engine.screen_manager.hide_all()
        # Dissolve to black effect
        surface = engine.renderer.screen
        clock = engine.clock
        fade_surface = pygame.Surface(surface.get_size())
        fade_surface.fill((0, 0, 0))
        
        for alpha in range(0, 256, 16):
            fade_surface.set_alpha(alpha)
            engine.screen_manager.render(surface)
            surface.blit(fade_surface, (0, 0))
            pygame.display.update()
            clock.tick(60)

        # Reset and reload scene
        engine.lexer.current = 0
        engine.lexer.load_scripts()
        self.clear_scene(engine)
    
    def clear_scene(self, engine):
        """
        The `clear_scene` function resets various attributes and data structures in the game engine to
        clear the current scene.

        """

        engine.sprite_layers.clear()
        engine.current_bg = None
        engine.current_bgm = None
        engine.sprite_layers = {}
        
        engine.characters.clear()
        engine.vars.clear()
        engine.scenes.clear()
        engine.loaded_files.clear()
        engine.sprites.clear()
        engine.current_menu_buttons = []
        engine.current_dialogue = ""
        engine.current_character_name = ""
        engine.condition_stack = []
        engine.checkpoints.clear()
        engine.current_choice_buttons = []
        
    def handle_Load(self, arg, engine):
        """
        Loads and processes .script files.
        """
        arg = arg.strip()
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()
        arg = arg.strip('"').strip("'")
        force_compiled = any(keyword in arg.lower() for keyword in self.system_files)
        
        try:
            if force_compiled:
                if not arg.lower().endswith(aes_extension):
                    base, _ = os.path.splitext(arg)
                    compiled_arg = base + aes_extension
                else:
                    compiled_arg = arg
                
                data = engine.resource_manager.get_bytes(compiled_arg)
                data = AES(data, key).decrypt().decode("utf-8", errors="replace")
                engine.Log(f"[Load] Compiled file loaded: {compiled_arg}")
                engine.loaded_files[compiled_arg] = data
                content = data

            else:
                data = engine.resource_manager.get_bytes(arg)
                engine.Log(f"[Load] File loaded: {arg}")
                engine.loaded_files[arg] = data
                content = data
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
        if not f"main_menu{file_extension}" in self.system_files:
            self.system_files.append(f"main_menu{file_extension}")
        self.handle_Load(f'("system/main_menu{file_extension}")', engine)
    
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
        if hasattr(engine, "current_menu_panel") and engine.current_menu_panel:
            engine.screen_manager.hide(engine.current_menu_panel)
            engine.current_menu_panel = None
            engine.current_menu_buttons = []
            
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
            compiled_path = base_name + aes_extension
            file_bytes = engine.resource_manager.get_bytes(compiled_path)
            content = AES(file_bytes, key).decrypt().decode("utf-8", errors="replace")

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
        compiled_path = os.path.join("scenes", f"{scene_file_name}{aes_extension}")
        content = ""
        try:
            file_bytes = engine.resource_manager.get_bytes(compiled_path)
            content = AES(file_bytes, key).decrypt().decode("utf-8", errors="replace")
            engine.Log(f"[jump_scene] Compiled scene '{scene_alias}' loaded from: {compiled_path}")
        except Exception as e:
            non_compiled_path = os.path.join(engine.game_path, "data", "scenes", f"{scene_file_name}{aes_extension}")
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
        The function `handle_if` evaluates a condition based on a variable in the `engine` object and
        logs the result.
        
        :param arg: The `arg` parameter in the `handle_if` method is a string that represents a variable
        name. It is stripped of any leading or trailing whitespace before being used in the method
        :param engine: The `engine` parameter in the `handle_if` function seems to be an object that
        contains some properties and methods related to handling conditions and logging. It appears to
        have a `vars` property that stores variables, a `condition_stack` property to keep track of
        conditions, and a `Log`
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
        The function `handle_else` reverses the current condition in the engine's condition stack if
        there is an open if block.
        
        :param arg: The `arg` parameter in the `handle_else` method is likely used to pass any
        additional arguments or values that may be needed for processing the "else" condition. In this
        context, it may be used to provide any specific data or instructions related to the "else" block
        within the code logic
        :param engine: The `engine` parameter in the `handle_else` function seems to be an object that
        has a `condition_stack` attribute. This function is designed to handle an "else" statement in
        some sort of conditional logic. The function checks if there is an open "if" block in the
        `engine
        """
        if not hasattr(engine, "condition_stack") or not engine.condition_stack:
            raise Exception("[else] No open if block.")
        current = engine.condition_stack.pop()
        engine.condition_stack.append(not current)
        engine.Log(f"[else] Condition reversed: now {not current}")

    def handle_endif(self, arg, engine):
        """
        The function `handle_endif` checks for an open if block in the condition stack of the engine and
        pops it if found, logging the end of the if block.
        
        :param arg: The `arg` parameter in the `handle_endif` method is typically used to pass any
        arguments or values that are relevant to the operation being performed. In this context, `arg`
        might contain information related to the `endif` statement or the if block that is being closed.
        It could be
        :param engine: The `engine` parameter is likely an object that contains information and methods
        related to the execution of the code or script. In this specific function `handle_endif`, the
        `engine` object is used to access a `condition_stack` attribute, which is assumed to be a stack
        data structure used to
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

        namebox_height = engine.renderer.name_font.get_height()
        margin = 23
        
        namebox_y = engine.config["dialogue_rect"]["y"] - namebox_height - margin

        engine.config["namebox_rect"] = {
            "x": int(width * 0.05),
            "y": namebox_y,
            "width": int(width * 0.2),
            "height": int(engine.renderer.name_font.get_height() * 2),
            "bg_color": current_namebox_cfg.get("bg_color", (50, 50, 50)),
            "border_color": current_namebox_cfg.get("border_color", (255, 255, 255))
        }

        engine.renderer.update_set_mode((width, height))
        
        engine.Log(f"[Display] Window set to {width}x{height}.")
    
    # TODO: add quick menu 
    def handle_qm(self, arg, engine):
        """
        Inicia un nuevo menú rápido (resetea botones actuales).
        Este menú NO bloquea el flujo del juego.
        """
        engine.quick_menu_buttons = []
        engine.Log("[quickmenu] Preparando Quick Menu.")

    def handle_qm_button(self, arg, engine):
        """
        Agrega un botón al Quick Menu.
        """
        import re
        pattern = r'^"([^"]+)"\s+event\s+(.+)$'
        match = re.match(pattern, arg.strip())
        if not match:
            raise Exception('[quickmenu-button] Formato inválido. Usa: @qm-button "Texto" event Acción')
        
        label = match.group(1)
        event = match.group(2).strip()
        engine.quick_menu_buttons.append({"label": label, "event": event})
        engine.Log(f"[quickmenu] Botón agregado: '{label}' -> @{event}")

    def handle_qm_end(self, arg, engine):
        """
        Crea y muestra el panel del Quick Menu en pantalla.
        Se mantiene visible durante el juego.
        """
        from vne.visual import MenuPanel, Button, VerticalLayout
        screen_width = engine.config.get("screen_width", 800)
        width = 140
        height = len(engine.quick_menu_buttons) * 50 + 20
        x = screen_width - width - 10
        y = 10

        panel = MenuPanel(
            width=width,
            height=height,
            layout=VerticalLayout(),
            x=x,
            y=y
        )
        panel.z_index = 50  # z-index alto para estar siempre visible
        font = engine.renderer.font

        for btn in engine.quick_menu_buttons:
            label_text = self.substitute_variables(btn["label"], engine)
            def make_action(event_str=btn["event"]):
                def action():
                    engine.Log(f"[quickmenu] Acción: @{event_str}")
                    engine.event_manager.handle(f"@{event_str}", engine)
                return action
            button = Button(
                label=label_text,
                action=make_action(),
                width=width - 20,
                height=40,
                font=font
            )
            panel.add_child(button)

        # Si ya había uno, reemplazarlo
        if engine.quick_menu_panel:
            engine.screen_manager.hide(engine.quick_menu_panel)

        engine.quick_menu_panel = panel
        engine.screen_manager.show(panel, force_top=True)
        engine.Log("[quickmenu] Quick Menu activo.")

    # example
    def handle_choice_menu(self, arg, engine):
        """
        Initiates a choicemenu block where subsequent @option commands define menu options.
        
        :param arg: Unused argument.
        :param engine: The game engine instance.
        """
        engine.current_choice_buttons = []
        engine.Log("[choice] Menu block started.")
    
    def handle_option_button(self, arg, engine):
        """
        Parses a button command to extract a label and an event action, then adds them to the current menu.
        Expected syntax: @button "Label" event <command>
        
        :param arg: The argument string containing the label and the event command.
        :param engine: The game engine instance.
        """
        pattern = r'^"([^"]+)"\s+event\s+(.+)$'
        arg = arg.strip()
        match = re.match(pattern, arg)
        if not match:
            raise Exception('[choice-button] Invalid format. Expected: @option "Label" event Set(var, test).')
        raw_label = match.group(1)
        action = match.group(2).strip()
        if not hasattr(engine, "current_choice_buttons"):
            engine.current_choice_buttons = []
        if not action.startswith("Set"):
            raise Exception('[choice-button] Invalid event. Expected: @option "Label" event Set(var, test).')
        
        engine.current_choice_buttons.append({"raw_label": raw_label, "event": action})
        engine.Log(f"[choice-button] Button added: '{raw_label}' -> '{action}'.")
    
    def handle_end_choice(self, arg, engine):
        """
        Crea y muestra el panel visual para el menú de opciones (choicemenu).
        """
        if not hasattr(engine, "current_choice_buttons") or not engine.current_choice_buttons:
            raise Exception("[endmenu] There are no buttons defined in the menu.")
        screen_width = engine.config.get("screen_width", 800)
        screen_height = engine.config.get("screen_height", 600)
        panel_width = int(screen_width * 0.5)
        button_height = 40
        margin = 10
        panel_height = len(engine.current_choice_buttons) * (button_height + margin) + margin
        panel_x = (screen_width - panel_width) // 2
        panel_y = (screen_height - panel_height) // 2
        # Crear el panel visual si no existe
        from vne.visual import MenuPanel, Button, VerticalLayout
        engine.current_menu_panel = MenuPanel(
            width=panel_width, 
            height=panel_height, 
            layout=VerticalLayout(),
            x=panel_x,
            y=panel_y,
        )
        engine.current_menu_panel.z_index = 10
        font = engine.renderer.font
        for i, btn in enumerate(engine.current_choice_buttons):
            label_text = self.substitute_variables(btn["raw_label"], engine)
            def make_action(event_str=btn["event"]):
                def action():
                    engine.Log(f"[menu] Selected action: @{event_str}")
                    engine.screen_manager.hide(engine.current_menu_panel)
                    engine.event_manager.handle(f"@{event_str}", engine)
                return action
            button = Button(
                label=label_text,
                action=make_action(),
                width=panel_width - 2*margin,
                height=button_height,
                font=font
            )
            engine.current_menu_panel.add_child(button)
        engine.screen_manager.show(engine.current_menu_panel, force_top=True)
        # Esperar a que se cierre el menú, procesando eventos para evitar freeze
        while engine.current_menu_panel in engine.screen_manager.screens and engine.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    engine.running = False
                else:
                    engine.screen_manager.handle_event(event)
            engine.clock.tick(30)
            engine.screen_manager.render(engine.renderer.screen)
            pygame.display.update()
        engine.current_menu_buttons = []
        engine.current_menu_panel = None

    def handle_menu(self, arg, engine):
        engine.current_menu_buttons = []
        engine.Log("[menu] Menu block started.")

    def handle_button(self, arg, engine):
        arg = arg.strip()
        pattern = r'^"([^"]+)"\s+event\s+(.+)$'
        match = re.match(pattern, arg)
        if not match:
            raise Exception('[button] Invalid format. Expected: @button "Label" event <command>.')
        raw_label = match.group(1)
        rest = match.group(2).strip()
        parts = rest.split()
        action = parts[0]
        params = parts[1:] if len(parts) > 1 else []
        visual_params = {}
        for p in params:
            if '=' in p:
                k, v = p.split('=', 1)
                visual_params[k.strip().lower()] = v.strip()
        button_data = {"raw_label": raw_label, "event": action}
        if visual_params:
            button_data["visual_params"] = visual_params
        if not hasattr(engine, "current_menu_buttons"):
            engine.current_menu_buttons = []
        engine.current_menu_buttons.append(button_data)
        engine.Log(f"[button] Button added: '{raw_label}' -> '{action}' params: {visual_params if visual_params else '{}'}.")

    def handle_endmenu(self, arg, engine):
        if not hasattr(engine, "current_menu_buttons") or not engine.current_menu_buttons:
            raise Exception("[endmenu] There are no buttons defined in the menu.")
        engine.current_menu_panel = MenuPanel(width=500, height=400, layout=VerticalLayout(), no_bg=True, no_border=True, is_main_menu=True, is_modal=False)
        font = engine.renderer.font
        for btn in engine.current_menu_buttons:
            v = btn.get("visual_params", {})
            width = int(v.get("width", 200))
            height = int(v.get("height", 40))
            color = (100, 100, 100)
            if "color" in v:
                try:
                    c = v["color"]
                    if c.startswith('#'):
                        c = c[1:]
                    if len(c) == 6:
                        color = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
                except:
                    pass
            btn_font = font
            if "font" in v and hasattr(engine.renderer, "get_font"):
                try:
                    btn_font = engine.renderer.get_font(v["font"])
                except:
                    pass
            
            button = None
            def make_action(event_str=btn["event"]):
                def action():
                    # 💥 LIMPIEZA del menú actual antes de ejecutar el evento
                  
                  
                    engine.screen_manager.hide(engine.current_menu_panel)
                    engine.current_menu_panel.remove_child(button)
                    engine.Log(f"[menu] Selected action: @{event_str}")
                     
                    engine.event_manager.handle(f"@{event_str}", engine)
                return action
            button = Button(
                label=btn["raw_label"],
                action=make_action(),
                width=width,
                height=height,
                color=color,
                font=btn_font
            )
            engine.current_menu_panel.add_child(button)
        engine.screen_manager.show(engine.current_menu_panel, False)
        # Wait for menu to close, process events to avoid freeze
        while engine.current_menu_panel in engine.screen_manager.screens and engine.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    engine.running = False
                else:
                    engine.screen_manager.handle_event(event)
            engine.clock.tick(30)
            engine.screen_manager.render(engine.renderer.screen)
            pygame.display.update()
            
        engine.current_menu_buttons = []
        engine.current_menu_panel = None

    def handle_Set_event(self, arg, engine):
        """
        Updates the value of a defined variable using the syntax: Set(variable, value)
        For example, @button "Exit" event Set(chek, true).
        
        :param arg: The argument string containing the variable name and new value.
        :param engine: The game engine instance.
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
    
    def handle_save(self, arg, engine):
        """
        Saves the current game state to a slot.
        Syntax: @save("slot1") or @save() for quicksave.
        """
        slot_name = arg.strip().strip('()').strip('"')
        if not slot_name:
            # If no slot name is provided, use the default quicksave slot.
            slot_name = QUICKSAVE_SLOT

        saves_dir = os.path.join(engine.game_path, "saves")
        if not os.path.exists(saves_dir):
            os.makedirs(saves_dir)

        save_path = os.path.join(saves_dir, f"{slot_name}.sav")

        # Gather serializable state.
        # SpriteVisual objects contain pygame surfaces, which are not pickleable.
        # We need to store the information required to recreate them.
        
        sprite_states = {}
        for alias, sprite_visual in engine.sprite_layers.items():
          
            sprite_states[alias] = {
                'alias': alias,
      
                'position': sprite_visual.position,
                'x': sprite_visual.x,
                'y': sprite_visual.y,
                'z_index': sprite_visual.z_index,
                'alpha': sprite_visual.alpha,
                # Animación no guardada
            }
        
        save_data = {
            'version': engine_version,
            'vars': engine.vars,
            'characters': engine.characters,
            'scenes': engine.scenes,
            'checkpoints': engine.checkpoints,
            'condition_stack': engine.condition_stack,
            'qm': engine.quick_menu_buttons,
            'lexer_state': {
                'commands': engine.lexer.commands,
                'original_commands': engine.lexer.original_commands,
                'current': engine.lexer.current-1 # adding -1 improve the save fidelity
            },
            'visual_state': {
                'bg_filename': getattr(engine, 'current_bg_filename', None),
                'sprites': sprite_states,
            },
            'audio_state': {
                'bgm_filename': getattr(engine, 'current_bgm_filename', None)
            }
        }

        try:
            with open(save_path, 'wb') as f:
                pickle.dump(save_data, f)
            engine.Log(f"[save] Game state saved to slot '{slot_name}'.")
        except Exception as e:
            raise Exception(f"[save] Failed to save game to slot '{slot_name}': {e}")
    
    def handle_load_save(self, arg, engine):
        """
        Loads the game state from a slot.
        Syntax: @load("slot1") or @load() for quickload.
        """
        slot_name = arg.strip().strip('()').strip('"')
        if not slot_name:
            # If no slot name is provided, use the default quickload slot.
            slot_name = QUICKSAVE_SLOT

        save_path = os.path.join(engine.game_path, "saves", f"{slot_name}.sav")

        if not os.path.exists(save_path):
            raise Exception(f"[load] Save slot '{slot_name}' not found.")

        try:
            with open(save_path, 'rb') as f:
                loaded_data = pickle.load(f)
        except Exception as e:
            raise Exception(f"[load] Failed to load game from slot '{slot_name}': {e}")

        if loaded_data.get('version') != engine_version:
            engine.Log(f"[load] Warning: Save file version '{loaded_data.get('version')}' differs from engine version '{engine_version}'.")

        # --- Restore State ---
        engine.screen_manager.hide_all()
        engine.sprite_layers.clear()
        engine.quick_menu_buttons.clear()
      
        engine.vars.update(loaded_data['vars'])
        engine.characters.update(loaded_data['characters'])
        engine.scenes.update(loaded_data['scenes'])
        engine.checkpoints = loaded_data['checkpoints']
        engine.condition_stack = loaded_data['condition_stack']

        lexer_state = loaded_data['lexer_state']
        engine.lexer.commands = lexer_state['commands']
        engine.lexer.original_commands = lexer_state['original_commands']
        engine.lexer.current = lexer_state['current']
        
        for qm in loaded_data['qm']:
            engine.quick_menu_buttons.append(qm)

        self.dispatch("qmEnd", arg, engine)

        visual_state = loaded_data['visual_state']
        if visual_state.get('bg_filename'):
            self.handle_bg(visual_state['bg_filename'], engine)

        for alias, state in visual_state.get('sprites', {}).items():
            self.handle_sprite(f"{alias}", engine)

        audio_state = loaded_data.get('audio_state', {})
        if audio_state.get('bgm_filename'):
            self.handle_bgm(audio_state['bgm_filename'], engine)

        engine.Log(f"[load] Game state loaded from slot '{slot_name}'.")
    
    def handle_bgm(self, arg, engine):
        """
        Plays looping background music using a file located at:
        data/audio/bgm/<filename>.mp3.
        """
        filename = arg.strip()
        engine.current_bgm_filename = filename

        bgm = Audio(filename, "bgm", engine)

        bgm.play(loop=-1)
      
        engine.Log(f"[bgm] Playing background music '{filename}'.")
    
    def handle_sfx(self, arg, engine):
        """
        Plays a sound effect using a file located at:
        data/audio/sfx/<filename>.mp3.
        """
        filename = arg.strip()
        
        sfx = Audio(filename, "sfx", engine)

        sfx.play(loop=-1)
        engine.Log(f"[sfx] Playing sound effect '{filename}'.")

### despues de aqui realiza la implementaciones.