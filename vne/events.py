import io
import os
import pygame
import re
 
from collections import ChainMap
from vne.lexer import ScriptLexer
from vne.aes import AES, SCRIPT_AAD
from vne.config import (key, file_extension, aes_extension, bundle_extension,
                        engine_version, init_file)
import pickle
from vne.Audio import Audio
from vne.visual import VisualElement, Button, MenuPanel, VerticalLayout, DialogPanel, SpriteVisual, AutoSizedBackground, HorizontalLayout
from vne.visual import SpriteVisual
from vne.visual import FadeAnimation, SlideAnimation, DissolveAnimation

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
        
        self.exposed_api = {}
 

    def register_default_events(self):
        """
        La función `register_default_events` registra varios manejadores de eventos para diferentes acciones en
        un motor de juego.
        """
  
        # Primitivos
        self.register_event("say", self.handle_say)
        self.register_event("end", self.handle_end)
        self.register_event("process_scene", self.handle_process_scene)

        # Importación/Carga y Inicio/Inicialización
        self.register_event("Load", self.handle_Load)
        self.register_event("LoadSystem", self.handle_load_system)
        self.register_event("LoadMainMenu", self.handle_load_main_menu)
        self.register_event("SplashScreen", self.handle_splash_screen)
        
        # Flujo de escenas
        self.register_event("jump_scene", self.handle_jump_scene)
        self.register_event("checkpoint", self.handle_checkpoint)
        self.register_event("goto", self.handle_goto)
        
        # Definiciones de variables
        self.register_event("char", self.handle_char)
        self.register_event("scene", self.handle_scene)
        self.register_event("def", self.handle_define)

        # Mutaciones
        self.register_event("set", self.handle_set)
        self.register_event("rename", self.handle_rename)

        # Imágenes
        self.register_event("bg", self.handle_bg)
        self.register_event("sprite", self.handle_sprite)
        self.register_event("hide", self.handle_hide_sprite)
        
        # Audio
        self.register_event("bgm", self.handle_bgm)
        self.register_event("sfx", self.handle_sfx)

        # Configuraciones
        self.register_event("Display", self.handle_display)
        self.register_event("GameTitle", self.handle_game_title)
        self.register_event("GameIconName", self.handle_game_window_icon)
        
        # Banderas condicionales
        self.register_event("if", self.handle_if)
        self.register_event("else", self.handle_else)
        self.register_event("endif", self.handle_endif)

        # Menú
        self.register_event("mainMenu", self.handle_menu)
        self.register_event("button", self.handle_button)
        self.register_event("endMainMenu", self.handle_endmenu)
        
        # Menú rápido
        self.register_event("qm", self.handle_qm)
        self.register_event("qmBtn", self.handle_qm_button)
        self.register_event("qmEnd", self.handle_qm_end)
        self.register_event("quick_menu", self.handle_quick_menu)
        self.register_event("history", self.handle_history)

        # Opciones
        self.register_event("choice", self.handle_choice_menu)
        self.register_event("option", self.handle_option_button)
        self.register_event("end_choice", self.handle_end_choice)
        
        # UI Screens
        self.register_event("save_screen", self.handle_save_screen)
        self.register_event("SaveScreen", self.handle_save_screen)
        self.register_event("load_screen", self.handle_load_screen)
        self.register_event("LoadScreen", self.handle_load_screen)
        self.register_event("prefs", self.handle_prefs)
        self.register_event("Prefs", self.handle_prefs)
        
        # Eventos
        self.register_event("Scene", self.handle_process_scene)
        self.register_event("Set", self.handle_Set_event)
        self.register_event("side_image", self.handle_side_image)
        self.register_event("ctc", self.handle_ctc)
        self.register_event("Quit", self.handle_Quit)
        
        # Herramientas
        
        self.register_event("Log", self.handle_log)
        self.register_event("Save", self.handle_save)
        self.register_event("Continue", self.handle_load_save)
        # Hot-reload (dev only)
        self.register_event("reload", self.handle_reload)

        # Modules
        self.register_event("Python", self.handle_python)

        # UI & Screen Language
        self.register_event("ui_style", self.handle_ui_style)
        self.register_event("screen", self.handle_screen)
        self.register_event("add_button", self.handle_add_button)
        self.register_event("add_text", self.handle_add_text)
        self.register_event("add_image", self.handle_add_image)
        self.register_event("add_box", self.handle_add_box)
        self.register_event("end_box", self.handle_end_box)
        self.register_event("end_screen", self.handle_end_screen)
        self.register_event("show_screen", self.handle_show_screen)
        self.register_event("hide_screen", self.handle_hide_screen)
        self.register_event("ui_config", self.handle_ui_config)

    def handle_log(self, arg, engine):
        arg = arg.strip()
        mapping = ChainMap(engine.characters, engine.scenes, engine.vars)
        if arg.startswith("(") and arg.endswith(")"):
            arg = arg[1:-1].strip()

            # Registro de cadenas
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
        # Unify all mappings. Order of ChainMap determines priority.
        mapping = ChainMap(engine.vars, engine.characters, engine.scenes)
        
        def replacer(match):
            key = match.group(1).strip()
            if key in mapping:
                return str(mapping[key])
            else:
                # If not found, keep the {key} or raise if strictly required
                # For now, let's keep the engine's original behavior of raising if missing in some handlers
                # but making it more robust here.
                return mapping.get(key, match.group(0))
        
        return re.sub(r'\{([^}]+)\}', replacer, text)
    
    def handle_say(self, arg, engine):
        """
        Processes dialogue for characters, replacing variables with their corresponding values.
        Sets the engine to wait for input.
        """
        if ':' in arg:
            speaker, dialogue = arg.split(":", 1)
            speaker = speaker.strip()
            dialogue = dialogue.strip()
            if speaker not in engine.characters:
                raise Exception(f"[ERROR] The character '{speaker}' is not defined.")
            engine.current_character_name = engine.characters[speaker]
        elif '*' in arg:
            speaker, dialogue = arg.split("*", 1)
            speaker = speaker.strip()
            dialogue = dialogue.strip()
            engine.current_character_name = speaker
        else:
            dialogue = arg.strip()
            engine.current_character_name = ""

        dialogue = self.substitute_variables(dialogue, engine)
        engine.current_dialogue = dialogue

        # Setup DialogPanel
        font = engine.renderer.font
        name_font = getattr(engine.renderer, 'name_font', font)
        
        if not engine.current_dialog_panel:
            cfg = engine.config.get("dialogue_rect", {})
            panel_x = cfg.get("x", 0)
            panel_y = cfg.get("y", 480)
            panel_width = cfg.get("width", engine.config.get("screen_width", 800))
            panel_height = cfg.get("height", 120)
            
            engine.current_dialog_panel = DialogPanel("", font=font, x=panel_x, y=panel_y, width=panel_width, height=panel_height)
            engine.current_dialog_panel.name_font = name_font
            if "dialogue_box" in engine.style_manager.styles:
                engine.style_manager.apply(engine.current_dialog_panel, "dialogue_box")
            engine.screen_manager.show(engine.current_dialog_panel, force_top=True)
        
        panel = engine.current_dialog_panel
        panel.z_index = 10
        panel.character_name = engine.current_character_name if engine.current_character_name else None
        panel.set_text(dialogue)
        
        # UI Overhaul: Quick Menu
        if hasattr(engine, "quick_menu_buttons") and engine.quick_menu_buttons:
            # Clear old buttons
            panel.children = [c for c in panel.children if not getattr(c, 'is_qm', False)]
            
            # Create a localized quick menu
            qm_y = panel.height - 30
            spacing = 80
            x_start = panel.width - (len(engine.quick_menu_buttons) * spacing) - 20
            
            for i, label in enumerate(engine.quick_menu_buttons):
                def make_qm_action(l):
                    # Mapping standard labels to engine functions
                    cmds = {
                        "Save": "save_screen",
                        "Load": "load_screen",
                        "History": "history",
                        "Skip": "skip",
                        "Auto": "auto",
                        "Settings": "prefs"
                    }
                    cmd = cmds.get(l, l.lower())
                    return lambda: engine.event_manager.handle('@' + cmd, engine)
                
                btn = Button(label, make_qm_action(label), x=x_start + i*spacing, y=qm_y, width=70, height=25)
                btn.is_qm = True
                btn.font = pygame.font.SysFont("Arial", 12)
                panel.add_child(btn)
        
        # UI Overhaul: Add to history
        engine.add_to_history(panel.character_name or "", dialogue)
        
        if panel not in engine.screen_manager.screens:
            engine.screen_manager.show(panel, force_top=True)

        engine.awaiting_input = True
        
        # Track seen dialogue (optional but kept for compatibility)
        if not hasattr(engine, "seen_dialogue"):
            engine.seen_dialogue = set()
        scene_id = getattr(engine, "current_scene", None) or engine.vars.get("scene", "")
        context_vars = tuple(sorted((k, str(v)) for k, v in engine.vars.items()))
        engine.seen_dialogue.add((scene_id, engine.current_character_name, dialogue, context_vars))

    def handle_quick_menu(self, arg, engine):
        """
        Defines or shows the quick menu on the dialogue box.
        @quick_menu "Save", "Load", "History"
        """
        # For now, we'll just store the labels
        parts = [p.strip().strip('"') for p in arg.split(',')]
        engine.quick_menu_buttons = parts
        engine.Log(f"[ui] Quick Menu set: {parts}")

    def handle_history(self, arg, engine):
        """
        Shows the history/backlog screen.
        """
        from vne.visual import MenuPanel, TextElement, ScrollArea, VerticalLayout
        
        win_w = engine.config.get("screen_width", 1280)
        win_h = engine.config.get("screen_height", 720)
        
        panel = MenuPanel(width=win_w, height=win_h, no_bg=False, layout=None, z_index=100)
        panel.bg_color = (10, 10, 20, 230)
        
        # Title
        title = TextElement("HISTORY", x=50, y=30)
        title.color = (255, 255, 255)
        panel.add_child(title)
        
        # Scroll Area for history
        content_h = len(engine.history) * 60 + 100
        scroll = ScrollArea(x=50, y=100, width=win_w-100, height=win_h-200, content_height=content_h)
        
        y_off = 0
        for entry in reversed(engine.history):
            name = entry.get("name", "")
            text = entry.get("text", "")
            
            line = TextElement(f"{name}: {text}" if name else text, x=0, y=y_off)
            line.color = (200, 200, 200)
            scroll.add_child(line)
            y_off += 60
            
        panel.add_child(scroll)
        
        # Close button
        btn = Button("Close", lambda: engine.screen_manager.hide(panel), x=win_w-150, y=win_h-70, width=120, height=40)
        panel.add_child(btn)
        
        engine.screen_manager.show(panel)

    def handle_side_image(self, arg, engine):
        """
        Sets the side image for the current dialogue.
        @side_image "Kuro:Happy" (Autoconverts to Kuro_Happy)
        """
        if not arg.strip():
            if engine.current_dialog_panel:
                engine.current_dialog_panel.side_image = None
            return

        raw_name = arg.strip().strip('"')
        safe_name = raw_name.replace(":", "_")
        
        try:
            img = engine.lexer.load_image(safe_name)
            if engine.current_dialog_panel:
                engine.current_dialog_panel.side_image = img
                engine.Log(f"[ui] Side image set: {safe_name}")
        except Exception as e:
            engine.Log(f"[ui] Warning: Could not load side image '{safe_name}': {e}")
            # Don't crash, just don't show image
            if engine.current_dialog_panel:
                engine.current_dialog_panel.side_image = None

    def handle_ctc(self, arg, engine):
        """
        Sets the CTC icon.
        @ctc "ui/ctc_arrow"
        """
        if not arg.strip():
            if engine.current_dialog_panel:
                engine.current_dialog_panel.ctc_icon = None
            return

        raw_name = arg.strip().strip('"')
        
        try:
            img = engine.lexer.load_image(raw_name)
            if engine.current_dialog_panel:
                engine.current_dialog_panel.ctc_icon = img
                engine.Log(f"[ui] CTC icon set: {raw_name}")
        except Exception:
             engine.Log(f"[ui] Warning: Could not load CTC icon '{raw_name}'")

    def parse_color(self, arg):
        """
        Converts a color name or hexadecimal code to an RGB color.
        """
        named_colors = {
            "black": (0, 0, 0),
            "white": (255, 255, 255),
        }

        if arg.lower() in named_colors:
            return named_colors[arg.lower()]
        
        # Hex: #rgb o #rrggbb
        hex_match = re.match(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", arg)
        if hex_match:
            hex_value = hex_match.group(1)
            if len(hex_value) == 3:
                r = int(hex_value[0]*2, 16)
                g = int(hex_value[1]*2, 16)
                b = int(hex_value[2]*2, 16)
            else:
                r = int(hex_value[0:2], 16)
                g = int(hex_value[2:4], 16)
                b = int(hex_value[4:6], 16)
            return (r, g, b)

        return None  

    def handle_bg(self, arg, engine):
        """
        Loads and scales a background image to fit the window, manteniendo aspecto.
        """
        engine.current_bg_filename = arg
        win_w = engine.renderer.screen.get_width()
        win_h = engine.renderer.screen.get_height()
        engine.Log(f"[bg] Attempting to set background: '{arg}' (win: {win_w}x{win_h})")

        try:
            color = self.parse_color(arg)

            if color:
                # Color sólido
                bg_visual = AutoSizedBackground(0, 0, win_w, win_h)
                bg_visual.bg_color = color
                bg_visual.border_width = 0
                bg_visual.z_index = -100
            else:
                # Imagen
                load_image = ScriptLexer(engine.game_path, engine).load_image
                bg_image = load_image(arg)

                img_w, img_h = bg_image.get_width(), bg_image.get_height()
                scale = min(win_w / img_w, win_h / img_h)
                new_w, new_h = int(img_w * scale), int(img_h * scale)

                bg_visual = SpriteVisual(
                    bg_image,
                    width=new_w,
                    height=new_h,
                    z_index=-100
                )

            engine.current_bg_visual = bg_visual

            # Fondo en capa más baja
            if hasattr(engine, "bg_layer") and engine.bg_layer:
                engine.screen_manager.hide(engine.bg_layer)
            engine.bg_layer = bg_visual
            engine.screen_manager.show(bg_visual, force_top=False)
            engine.Log(f"[bg] Background set: {arg}")

        except Exception as e:
            raise Exception(f"[bg] Error loading background: {e}")
    
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
        
     
    def handle_sprite(self, arg, engine):
        """
        Loads and stores a sprite image with a specified alias, position y animación.
        Sintaxis: @sprite character position="left"
        Sintaxis: @sprite character:variation
        """
        parts = arg.split() # get arguments
        load_image = ScriptLexer(engine.game_path, engine).load_image
        sprite_alias = parts[0].strip() # get alias @sprite <alias>
        position = "center"
        animation = None
        relative_path = None

        # Verificar si el argumento contiene position="value"
        match = re.search(r'position="(.*?)"', arg)
        if match:
            position = match.group(1)
            
        # Manejar alias con formato base:variación y opciones adicionales (normalizar a minúsculas)
        base_alias, _, variation = sprite_alias.partition(":")
        base_alias = base_alias.lower()
        variation = variation.lower()
        
        
        

        if variation:
            relative_path = os.path.join("images", "sprites", base_alias, f"{base_alias}_{variation}.png")
        else:
            relative_path = os.path.join("images", "sprites", base_alias, f"{base_alias}_default.png")

        # Detectar animaciones en el argumento
        anim_match = re.search(r'animation="(.*?)"', arg)
        if anim_match:
            anim_type = anim_match.group(1).lower()
            if anim_type == "fadein":
                animation = FadeAnimation(fade_in=True, duration=0.5)
            elif anim_type == "fadeout":
                animation = FadeAnimation(fade_in=False, duration=0.5)
            elif anim_type == "dissolve":
                animation = DissolveAnimation(duration=0.5)

        try:
            sprite_image = load_image(relative_path)

            sprite_visual = SpriteVisual(sprite_image, position=position, animation=animation)
            sprite_visual.z_index = 1

            # TODO: THIS DON'T WORK CORRECTLY WITH @HIDE
            if sprite_alias in engine.sprite_layers:
                engine.screen_manager.hide(engine.sprite_layers[sprite_alias])

            engine.sprite_layers[sprite_alias] = sprite_visual
            engine.screen_manager.show(sprite_visual)
        except Exception as e:
            raise Exception(f"[sprite] {e}")

    def handle_hide_sprite(self, arg, engine):
        """
        Hides a sprite from the screen and removes it from the sprite_layers dictionary.
        Supports:
        - @hide Kuro          (hides all 'Kuro:*' sprites)
        - @hide Kuro:Happy    (hides exactly 'Kuro:Happy')
        - @hide all           (hides all sprites)
        """
        sprite_alias = arg.strip().lower()

        if not sprite_alias:
            engine.Log("[hide] Error: No sprite alias provided.")
            return

        if not hasattr(engine, "sprite_layers"):
            return

        to_remove = []
        if sprite_alias == "all":
            to_remove = list(engine.sprite_layers.keys())
        else:
            # Direct match
            if sprite_alias in engine.sprite_layers:
                to_remove.append(sprite_alias)
            else:
                # Base name match (e.g. "@hide Kuro" should hide "Kuro:Happy")
                for key in engine.sprite_layers.keys():
                    base, _, _ = key.partition(":")
                    if base.lower() == sprite_alias:
                        to_remove.append(key)

        if not to_remove:
            engine.Log(f"[hide] Warning: No sprite matching '{sprite_alias}' found.")
            return

        for alias in to_remove:
            sprite = engine.sprite_layers[alias]
            engine.screen_manager.hide(sprite)
            del engine.sprite_layers[alias]
            engine.Log(f"[hide] Sprite '{alias}' hidden.")

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
        
        engine.current_bg_visual = None 
        engine.bg_layer = None 
        engine.current_bg_filename = None
        
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
                data = AES(key).decrypt(data, aad=SCRIPT_AAD).decode("utf-8", errors="replace")
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
        engine.screen_manager.hide_all()
        engine.awaiting_input = False
  
        
        if engine.current_bg_visual is None and engine.bg_layer is None and engine.current_bg_filename is None:
            # SET A DEFAULT BG
            self.dispatch("bg", "black", engine)
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
            content = AES(key).decrypt(file_bytes, aad=SCRIPT_AAD).decode("utf-8", errors="replace")

        except Exception as e:
            raise Exception(f"[ERROR] Compiled version of the script for '{base_name}' not found: {e}")
        engine.Log(f"[process_scene] Processing scene '{scene_alias}'.")
        new_lexer = ScriptLexer(engine.game_path, engine)
        new_lexer.commands = new_lexer.parse_script(content)
        new_lexer.original_commands = list(new_lexer.commands)
        new_lexer.current = 0
        engine.lexer = new_lexer
        # Guardar identificador del script actual para re-sincronización tras hot-reload
        engine.current_script_id = filename
        engine.Log(f"[process_scene] New scene loaded with {len(engine.lexer.commands)} commands.")
        
    def handle_jump_scene(self, arg, engine):
        """
        Processes the scene jump command.
        """
        engine.screen_manager.hide_all()
        engine.awaiting_input = False
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
            content = AES(key).decrypt(file_bytes, aad=SCRIPT_AAD).decode("utf-8", errors="replace")
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
        engine.current_script_id = scene_file_name
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
        La función `handle_if` evalúa una condición basada en una variable en el objeto `engine` y
        registra el resultado.
        
        :param arg: El parámetro `arg` en el método `handle_if` es una cadena que representa un nombre de variable.
        Se utiliza para eliminar cualquier espacio en blanco al principio o al final antes de ser usado en el método
        :param engine: El parámetro `engine` en la función `handle_if` parece ser un objeto que
        contiene algunas propiedades y métodos relacionados con el manejo de condiciones y registros. Tiene una
        propiedad `vars` que almacena variables, una propiedad `condition_stack` para hacer seguimiento de
        condiciones, y un método `Log`
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
        
        :param arg: El parámetro `arg` en el método `handle_else` se utiliza probablemente para pasar cualquier
        argumento o valor adicional que pueda ser necesario para procesar la condición "else". En este
        contexto, puede ser usado para proporcionar datos o instrucciones específicas relacionadas con el bloque "else" 
        dentro de la lógica del código
        :param engine: El parámetro `engine` en la función `handle_else` parece ser un objeto que
        tiene un atributo `condition_stack`. Esta función está diseñada para manejar una declaración "else" en
        algún tipo de lógica condicional. La función verifica si hay un bloque "if" abierto en el
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
        
        :param arg: El parámetro `arg` en el método `handle_endif` se utiliza típicamente para pasar cualquier
        argumento o valor que sea relevante para la operación que se está realizando. En este contexto, `arg`
        podría contener información relacionada con la declaración `endif` o el bloque if que se está cerrando.
        Podría ser
        :param engine: El parámetro `engine` es probablemente un objeto que contiene información y métodos
        relacionados con la ejecución del código o script. En esta función específica `handle_endif`, el
        objeto `engine` se utiliza para acceder a un atributo `condition_stack`, que se supone es una pila
        estructura de datos utilizada para
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
                    engine.current_menu_panel = None
                    engine.awaiting_input = False
                    engine.event_manager.handle(f"@{event_str}", engine)
                return action
            button = Button(
                label=label_text,
                action=make_action(),
                width=panel_width - 2*margin,
                height=button_height,
                theme=engine.theme
            )
            button.font = font
            if "choice_button" in engine.style_manager.styles:
                engine.style_manager.apply(button, "choice_button")
            engine.current_menu_panel.add_child(button)
        engine.screen_manager.show(engine.current_menu_panel, force_top=True)
        engine.awaiting_input = True
        engine.current_choice_buttons = []
        
    def handle_menu(self, arg, engine):
        """
        Initializes the main menu and parses optional position and layout parameters.
        Syntax: @mainMenu position="leftTop" layout="vertical"
        """
        engine.current_menu_buttons = []
        engine.Log("[menu] Menu block started.")

        # Parse optional parameters
        position = "center"  # Default position
        layout = "vertical"  # Default layout

        # Extract position and layout from arguments
        match_position = re.search(r'position="(.*?)"', arg)
        if match_position:
            position = match_position.group(1).strip()

        match_layout = re.search(r'layout="(.*?)"', arg)
        if match_layout:
            layout = match_layout.group(1).strip()

        # Store the parsed values in the engine for later use in handle_endmenu
        engine.menu_position = position
        engine.menu_layout = layout

        engine.Log(f"[menu] Position set to '{position}', Layout set to '{layout}'.")
    
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
        
        # Check if we are defining a screen (new system)
        if hasattr(engine, 'screen_container_stack') and engine.screen_container_stack:
            # Convert to element definition for instantiate_elements
            # visual_params needs to be treated as kwargs
            # clean up styles: style="btn_main" might have quotes
            kwargs = {}
            if visual_params:
                for k, v in visual_params.items():
                    # Strip quotes if present
                    if isinstance(v, str):
                        clean_v = v.strip().strip('"').strip("'")
                        kwargs[k] = clean_v
                    else:
                        kwargs[k] = v
                        
            element = {
                'type': 'button',
                'label': raw_label,
                'action': action,
                'kwargs': kwargs
            }
            engine.screen_container_stack[-1].append(element)
            engine.Log(f"[button] Added to screen stack: '{raw_label}'")
            return

        if not hasattr(engine, "current_menu_buttons"):
            engine.current_menu_buttons = []
        engine.current_menu_buttons.append(button_data)
        engine.Log(f"[button] Button added: '{raw_label}' -> '{action}' params: {visual_params if visual_params else '{}'}.")
    
    def handle_endmenu(self, arg, engine):
        """
        Finalizes the main menu by creating and displaying the menu panel with buttons.
        """
        if not hasattr(engine, "current_menu_buttons") or not engine.current_menu_buttons:
            raise Exception("[endmenu] There are no buttons defined in the menu.")

        # Use stored position and layout values
        position = getattr(engine, "menu_position", "center")
        layout = getattr(engine, "menu_layout", "vertical")

        # Determine layout class
        layout_class = VerticalLayout if layout == "vertical" else HorizontalLayout

        # Determine panel position based on the position value
        screen_width = engine.config.get("screen_width", 800)
        screen_height = engine.config.get("screen_height", 600)
        panel_width = 500
        panel_height = 400
        # Adjust panel dimensions for horizontal layout
        if layout == "horizontal":
            panel_width = len(engine.current_menu_buttons) * 220  # Adjust width based on button count
            panel_height = 100  # Reduce height for horizontal layout

        if position == "leftTop":
            panel_x, panel_y = 10, 10
        elif position == "rightTop":
            panel_x, panel_y = screen_width - panel_width - 10, 10
        elif position == "leftBottom":
            panel_x, panel_y = 10, screen_height - panel_height - 10
        elif position == "rightBottom":
            panel_x, panel_y = screen_width - panel_width - 10, screen_height - panel_height - 10
        elif position == "centerBottom":
            panel_x = (screen_width - panel_width) // 2
            panel_y = screen_height - panel_height - 10
        else:  # Default to center
            panel_x = (screen_width - panel_width) // 2
            panel_y = (screen_height - panel_height) // 2


        engine.current_menu_panel = MenuPanel(
            width=panel_width,
            height=panel_height,
            layout=layout_class(),
            x=panel_x,
            y=panel_y,
            no_bg=True,
            no_border=True,
            is_main_menu=True
        )

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
            def make_action(event_str=btn["event"]):
                def action():
                    engine.Log(f"[menu] Selected action: @{event_str}")
                    engine.screen_manager.hide(engine.current_menu_panel)
                    engine.current_menu_panel = None
                    engine.awaiting_input = False
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
        engine.screen_manager.show(engine.current_menu_panel)
        engine.awaiting_input = True
        engine.current_menu_buttons = []

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
                # Guardamos current tal cual (apunta a la siguiente a ejecutar)
                'current': engine.lexer.current
            },
            # Información adicional para re-sincronizar después de hot-reload
            'script_meta': {
                'current_script_guess': getattr(engine, 'current_script_id', None) or engine.vars.get('scene') or '__init__',
                'last_command_text': (engine.lexer.commands[engine.lexer.current-1] if getattr(engine.lexer, 'current', 0) > 0 and engine.lexer.current-1 < len(engine.lexer.commands) else ""),
                # previous_index = línea ejecutada más recientemente que queremos repetir tras reload
                'previous_index': (engine.lexer.current - 1) if engine.lexer.current > 0 else 0
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
        script_meta = loaded_data.get('script_meta', {})
        
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
        # Re-sincronizar script si es un hot-reload temporal y tenemos compilación nueva
        if slot_name == "__reload_tmp__":
            try:
                current_script_guess = script_meta.get('current_script_guess')
                last_command_text = script_meta.get('last_command_text')
                previous_index = script_meta.get('previous_index')
                if current_script_guess:
                    # Determinar ruta compilada
                    if current_script_guess == '__init__':
                        base_name = f"{init_file}"
                    else:
                        base_name = os.path.join('scenes', current_script_guess)
                    compiled_path = base_name + aes_extension
                    try:
                        file_bytes = engine.resource_manager.get_bytes(compiled_path)
                        new_content = AES(key).decrypt(file_bytes, aad=SCRIPT_AAD).decode('utf-8', errors='replace')
                        new_lexer = ScriptLexer(engine.game_path, engine)
                        new_lexer.commands = new_lexer.parse_script(new_content)
                        new_lexer.original_commands = list(new_lexer.commands)
                        # Queremos repetir la misma línea ejecutada antes del reload.
                        resume_index = 0
                        if isinstance(previous_index, int) and 0 <= previous_index < len(new_lexer.original_commands):
                            resume_index = previous_index
                        else:
                            # Fallback: localizar por texto exacto y quedarse en esa misma línea
                            if last_command_text:
                                for idx, cmd in enumerate(new_lexer.original_commands):
                                    if cmd.strip() == last_command_text.strip():
                                        resume_index = idx
                                        break
                        new_lexer.current = resume_index
                        engine.lexer = new_lexer
                        engine.Log(f"[reload-sync] Script '{base_name}' recargado. Reanudando en índice {resume_index}.")
                    except Exception as e:
                        engine.Log(f"[reload-sync] No se pudo recargar script actualizado: {e}")
            except Exception as e:
                engine.Log(f"[reload-sync] Error general al re-sincronizar: {e}")
    
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
        
 
 

    def handle_python(self, arg, engine):
            """
            Execute an in-process Python script.
            
            - Usage: 
                @Python("path/to/script.py")
                @Python("script.py")
            
            unsecure event!
            """
            a = arg.strip()
            if a.startswith("(") and a.endswith(")"):
                a = a[1:-1].strip()
        
            a = a.strip().strip('"').strip("'")
            if not a:
                engine.Log("[python] No script path provided.")
                return False

            disk_path = a if os.path.isabs(a) else os.path.join(engine.game_path, "data", a)
            rel_path = a.replace("\\", "/")  

            engine.Log(f"[python] resolved disk_path={disk_path} rel_path={rel_path}")

            try:
                if os.path.exists(disk_path):
                    with open(disk_path, "r", encoding="utf-8") as f:
                        code = f.read()
                    engine.Log(f"[python] Loaded script from disk: {disk_path}")
                    compile_path = disk_path
                else:
                    if not hasattr(engine, "resource_manager"):
                        engine.Log(f"[python] File not found on disk and there is no resource_manager: {disk_path}")
                        return False
                    try:
                        file_bytes = engine.resource_manager.get_bytes(rel_path)
                    except Exception as e:
                        engine.Log(f"[python] resource_manager.get_bytes failed for {rel_path}: {e}")
                        return False

                    if rel_path.lower().endswith(aes_extension):
                        try:
                            code = AES(key).decrypt(file_bytes, aad=SCRIPT_AAD).decode("utf-8", errors="replace")
                        except Exception as e:
                            engine.Log(f"[python] Failed to decrypt {rel_path}: {e}")
                            return False
                    else:
                        try:
                            code = file_bytes.decode("utf-8")
                        except Exception:
                            code = file_bytes.decode("utf-8", errors="replace")
                    engine.Log(f"[python] Loaded script from package: {rel_path}")
                    compile_path = rel_path

                import io, sys, traceback
                old_stdout, old_stderr = sys.stdout, sys.stderr
                sys.stdout = io.StringIO()
                sys.stderr = io.StringIO()
                
                def _register_func(name, func):
                    import inspect
                    def handler(arg, _engine):
                        """
                        El motor llamará handler(arg, engine) — aquí adaptamos para que
                        la función del script reciba *solo* arg (o nada si no espera).
                        """
                        arg = arg.strip()
                        if arg.startswith("(") and arg.endswith(")"):
                            arg = arg[1:-1].strip()

                        arg = arg.strip().strip('"').strip("'")
                        try:
                            params = list(inspect.signature(func).parameters.values())
                            pos_params = [p for p in params if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
                            n = len(pos_params)
                        except Exception:
                            n = None

                        # Función sin parámetros -> llamar sin argumentos
                        if n == 0:
                            return func()

                        # Función con al menos 1 parámetro -> intentar pasar solo `arg`
                        # Si `arg` está vacío/None y la función acepta 1 parámetro, intentar llamar sin args.
                        try:
                            if arg is None or (isinstance(arg, str) and arg == ""):
                                # preferir llamar sin args si eso funciona
                                try:
                                    return func()
                                except TypeError:
                                    return func(arg)
                            return func(arg)
                        except TypeError:
                            # fallback: intentar sin argumentos
                            return func()

                    self.register_event(name, handler)
                
                # expose some API's
                api = {
                    "version": engine_version,
                    "vars": engine.vars,
                    "Log": lambda msg: engine.Log(msg),
                    "Func": lambda name, func: _register_func(name, func),
                    "SetVar": lambda arg: self.handle_Set_event(arg, engine),
                   
                }
                
                from types import SimpleNamespace
                
                vne_obj = SimpleNamespace(**api)
                g = {
                    "__name__": "__main__", 
                    "vne": vne_obj, 
                    "__file__": compile_path
                }

                try:
                    exec(compile(code, compile_path, "exec"), g)
                except Exception as e:
                    tb = traceback.format_exc()
                    out = sys.stdout.getvalue()
                    err = sys.stderr.getvalue()
                    sys.stdout, sys.stderr = old_stdout, old_stderr
                    engine.generate_traceback(e)
                    #engine.Log(f"[python] Error executing {rel_path if not os.path.exists(disk_path) else disk_path}: {e}\n{tb}")
                    if out:
                        engine.Log(f"[python] stdout:\n{out}")
                    if err:
                        engine.Log(f"[python] stderr:\n{err}")
                    return False
                else:
                    out = sys.stdout.getvalue()
                    err = sys.stderr.getvalue()
                    sys.stdout, sys.stderr = old_stdout, old_stderr
                    if out:
                        engine.Log(f"[python] stdout:\n{out}")
                    if err:
                        engine.Log(f"[python] stderr:\n{err}")
                    engine.Log(f"[python] Script executed: {rel_path}")
                    return True

            except Exception as e:
                engine.Log(f"[python] Unexpected error: {e}")
                return False

    def handle_reload(self, arg, engine):
        """
        Hot-reload en caliente (solo devMode).
        - Guarda estado temporal (si existe handler save)
        - Llama a main.compile_all_kag_in_folder(...) para recompilar scripts
        - Reinicia ResourceManager
        - Restaura desde el save temporal si es posible
        """
        import importlib, traceback

        try:
            if not getattr(engine, "devMode", False):
                engine.Log("[reload] Ignorado: no está en modo devMode.")
                return False

            engine.Log("[reload] Iniciando hot-reload (devMode)...")
            # Mostrar notificación visual si el motor tiene screen_manager y Toast está disponible
            toast = None
            try:
                from vne.visual import Toast
                toast = Toast("Hot-reload: iniciando...", font=getattr(engine.renderer, 'font', None), duration=2.0)
                # Only attach the toast if the renderer surface is usable
                try:
                    scr = getattr(engine, 'renderer', None)
                    if scr is not None and getattr(scr, 'screen', None) is not None:
                        # try to access width to ensure surface initialized
                        try:
                            _ = scr.screen.get_width()
                            engine.screen_manager.show(toast, force_top=True)
                        except Exception:
                            # surface not ready; skip visual toast
                            toast = None
                    else:
                        toast = None
                except Exception:
                    toast = None
            except Exception:
                toast = None

            tmp_slot = "__reload_tmp__"
            # 1) guardar estado temporal si está disponible
            try:
                if hasattr(self, "handle_save"):
                    engine.Log("[reload] Guardando estado temporal...")
                    self.handle_save(f'("{tmp_slot}")', engine)
            except Exception as e:
                engine.Log(f"[reload] Warning: no se pudo crear save temporal: {e}")

            # 2) compilar scripts usando main.compile_all_kag_in_folder (import dinámico)
            try:
                engine.Log("[reload] Llamando a compile_all_kag_in_folder...")
                main_mod = importlib.import_module("main")
                data_folder = os.path.join(engine.game_path, "data")
                main_mod.compile_all_kag_in_folder(data_folder, key)
                engine.Log("[reload] Compilación completada.")
            except Exception as e:
                engine.Log(f"[reload] Error compilando scripts: {e}")
                engine.Log(traceback.format_exc())
                try:
                    if toast:
                        toast.text = f"Hot-reload: error: {str(e)[:50]}"
                except Exception:
                    pass
                return False

            # 3) reinicializar ResourceManager para que refleje nuevos assets
            try:
                engine.Log("[reload] Reiniciando ResourceManager...")
                from vne.rm import ResourceManager
                engine.resource_manager = ResourceManager(engine.game_path, engine.Log)
                engine.Log("[reload] ResourceManager reiniciado.")
            except Exception as e:
                engine.Log(f"[reload] Warning al reiniciar ResourceManager: {e}")

            # 4) intentar restaurar estado desde el save temporal (si existe handler load)
            try:
                if hasattr(self, "handle_load_save"):
                    engine.Log("[reload] Restaurando estado desde save temporal...")
                    self.handle_load_save(f'("{tmp_slot}")', engine)
                    engine.Log("[reload] Estado restaurado desde save temporal.")
                else:
                    engine.Log("[reload] No hay handler de load disponible; continuar.")
            except Exception as e:
                engine.Log(f"[reload] No se pudo restaurar desde temp: {e}")

            # 5) limpieza tentativa del save temporal en disco
            try:
                saves_dir = os.path.join(engine.game_path, "saves")
                tmp_path = os.path.join(saves_dir, f"{tmp_slot}.sav")
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception:
                pass

            engine.Log("[reload] Hot-reload completado correctamente.")
            try:
                if toast:
                    toast.text = "Hot-reload: completado"
            except Exception:
                pass
            return True

        except Exception as e:
            engine.Log(f"[reload] Excepción inesperada: {e}")
            engine.Log(traceback.format_exc())
            return False

    def _parse_kwargs(self, arg):
        import re
        kwargs = {}
        # This regex handles:
        # 1. key="quoted value"
        # 2. key=(tuple, values)
        # 3. key={nested=dict}
        # 4. key=simple_value
        pattern = r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|(\{[^}]+\})|(\([^)]+\))|([^ \t,={}]+))'
        matches = re.findall(pattern, arg)
        
        for m in matches:
            k = m[0]
            # Find which group matched (index 1 is double quote, 2 is single, 3 is dict, 4 is tuple, 5 is simple)
            v = m[1] or m[2] or m[3] or m[4] or m[5]
            
            if v.startswith('(') and v.endswith(')'):
                try: 
                    parts = v[1:-1].split(',')
                    kwargs[k] = tuple(int(x.strip()) for x in parts)
                except: kwargs[k] = v
            elif v.startswith('{') and v.endswith('}'):
                kwargs[k] = self._parse_kwargs(v[1:-1])
            elif v.isdigit(): kwargs[k] = int(v)
            elif v.replace('.', '', 1).isdigit(): kwargs[k] = float(v)
            elif v.lower() == 'true': kwargs[k] = True
            elif v.lower() == 'false': kwargs[k] = False
            else: kwargs[k] = v
        return kwargs

    def handle_ui_style(self, arg, engine):
        import re
        name_match = re.search(r'"?(\w+)"?', arg)
        if not name_match: return
        name = name_match.group(1)
        kwargs = self._parse_kwargs(arg)
        
        parent = kwargs.pop('parent', None)
        
        # Load background image if specified in style
        if 'bg_image' in kwargs:
            kwargs['bg_image'] = engine.lexer.load_image(kwargs['bg_image'])
        
        engine.style_manager.define(name, parent=parent, **kwargs)
        engine.Log(f"[ui] Style defined: {name} (parent: {parent})")

    def handle_screen(self, arg, engine):
        import re
        name_match = re.search(r'"?(\w+)"?', arg)
        name = name_match.group(1) if name_match else "unnamed_screen"
        kwargs = self._parse_kwargs(arg)
        engine.current_screen_def = {"name": name, "elements": [], "kwargs": kwargs}
        # Initialize container stack with the root elements list
        engine.screen_container_stack = [engine.current_screen_def['elements']]
        engine.Log(f"[ui] Defining screen: {name}")

    def handle_add_box(self, arg, engine):
        kwargs = self._parse_kwargs(arg)
        name = kwargs.pop('name', 'box') # Optional name for the box
        
        box_def = {
            'type': 'box',
            'kwargs': kwargs,
            'elements': []
        }
        
        # Add the box to the current container
        if hasattr(engine, 'screen_container_stack') and engine.screen_container_stack:
            engine.screen_container_stack[-1].append(box_def)
            # Push the box's elements list as the new active container
            engine.screen_container_stack.append(box_def['elements'])
        else:
             engine.Log("[ui] Error: @add_box called outside of @screen block or stack missing.")

    def handle_end_box(self, arg, engine):
        if hasattr(engine, 'screen_container_stack') and len(engine.screen_container_stack) > 1:
            engine.screen_container_stack.pop()
        else:
            engine.Log("[ui] Error: @end_box called without a matching @add_box.")


    def handle_add_button(self, arg, engine):
        kwargs = self._parse_kwargs(arg)
        label = kwargs.pop('label', 'Button')
        action_str = kwargs.pop('action', '')
        
        element = {
            'type': 'button', 'label': label, 'action': action_str, 'kwargs': kwargs
        }
        
        if hasattr(engine, 'screen_container_stack') and engine.screen_container_stack:
            engine.screen_container_stack[-1].append(element)
        elif hasattr(engine, 'current_screen_def'):
             # Fallback for integrity, though stack should exist
             engine.current_screen_def['elements'].append(element)

    def handle_add_text(self, arg, engine):
        kwargs = self._parse_kwargs(arg)
        text = kwargs.pop('text', '')
        
        element = {
            'type': 'text', 'text': text, 'kwargs': kwargs
        }
        
        if hasattr(engine, 'screen_container_stack') and engine.screen_container_stack:
            engine.screen_container_stack[-1].append(element)
        elif hasattr(engine, 'current_screen_def'):
            engine.current_screen_def['elements'].append(element)

    def handle_add_image(self, arg, engine):
        kwargs = self._parse_kwargs(arg)
        src = kwargs.pop('src', '')
        
        element = {
            'type': 'image', 'src': src, 'kwargs': kwargs
        }
        
        if hasattr(engine, 'screen_container_stack') and engine.screen_container_stack:
            engine.screen_container_stack[-1].append(element)
        elif hasattr(engine, 'current_screen_def'):
            engine.current_screen_def['elements'].append(element)

    def handle_end_screen(self, arg, engine):
        sdef = getattr(engine, 'current_screen_def', None)
        if sdef:
            engine.screen_definitions[sdef['name']] = sdef
            engine.current_screen_def = None
            if hasattr(engine, 'screen_container_stack'):
                engine.screen_container_stack = []
            engine.Log(f"[ui] Screen finalized: {sdef['name']}")

    def handle_show_screen(self, arg, engine):
        name = arg.strip().strip('\"').strip("'")
        sdef = engine.screen_definitions.get(name)
        if not sdef:
            engine.Log(f"[ui] Error: Screen {name} not found.")
            return

        from vne.visual import MenuPanel, Button, TextElement, ImageElement, VerticalLayout, HorizontalLayout, FlexLayout, GridLayout
        
        screen_kwargs = sdef.get('kwargs', {})
        layout_type = screen_kwargs.get('layout', 'none').lower()
        margin = screen_kwargs.get('margin', 10)
        
        layout = None
        if layout_type == 'horizontal':
            layout = HorizontalLayout(margin=margin)
        elif layout_type == 'vertical': # Default vertical if explicit
            layout = VerticalLayout(margin=margin)
        elif layout_type == 'grid':
            rows = screen_kwargs.get('rows', 2)
            cols = screen_kwargs.get('cols', 2)
            layout = GridLayout(rows=rows, cols=cols, margin=margin)
        elif layout_type == 'flex':
            layout = FlexLayout(gap=margin)
        elif layout_type == 'none':
            layout = None
        else:
            layout = None

        panel = MenuPanel(width=engine.config['screen_width'], height=engine.config['screen_height'], no_bg=True, no_border=True, layout=layout)
        panel.screen_name = name

        engine.Log(f"[ui-debug] Instantiating screen '{name}' with elements: {len(sdef['elements'])}")
        import json
        def simple_dump(opts):
            return str([ (o.get('type'), o.get('label') or o.get('text'), len(o.get('elements', []))) for o in opts ])
        engine.Log(f"[ui-debug] Root structure: {simple_dump(sdef['elements'])}")

        def instantiate_elements(elements, parent_container):
            for el in elements:
                engine.Log(f"[ui-debug] Processing element type: {el.get('type')}")
                kwargs = el.get('kwargs', {}).copy()
                style_name = kwargs.pop('style', None)
                obj = None
                
                if el['type'] == 'button':
                    def make_action(cmd):
                         return lambda: engine.event_manager.handle('@' + cmd, engine)
                    label = el.get('label', 'Button')
                    action = el.get('action', '')
                    obj = Button(label, make_action(action))
                    obj.font = engine.renderer.font
                
                elif el['type'] == 'text':
                    text = el.get('text', '')
                    obj = TextElement(text)
                    obj.font = engine.renderer.font
                
                elif el['type'] == 'image':
                    src = el.get('src', '')
                    img = engine.lexer.load_image(src)
                    w = kwargs.pop('width', None)
                    h = kwargs.pop('height', None)
                    obj = ImageElement(img, width=w, height=h)
                
                elif el['type'] == 'box':
                    # Recursive container
                    box_layout_type = kwargs.pop('layout', 'vertical').lower() # Default boxes to vertical
                    box_w = kwargs.pop('width', 300)
                    box_h = kwargs.pop('height', 300)
                    no_bg = kwargs.pop('no_bg', False)
                    
                    box_layout = None
                    if box_layout_type == 'horizontal':
                        box_layout = HorizontalLayout()
                    elif box_layout_type == 'vertical':
                         box_layout = VerticalLayout()
                    
                    obj = MenuPanel(width=box_w, height=box_h, layout=box_layout, no_bg=no_bg)
                    
                    # Recursively instantiate children
                    instantiate_elements(el['elements'], obj)

                if obj:
                    if style_name:
                        engine.style_manager.apply(obj, style_name)
                    obj.apply_style(kwargs)
                    
                    # Manual positioning fallback (only if no layout or specifically centered)
                    # Note: Layouts in visual.py often override x/y, but we set them anyway
                    if obj.x == 'center':
                        if parent_container.width:
                            obj.x = (parent_container.width - obj.width) // 2
                        else:
                            obj.x = 0 
                            
                    # 'center' y processing might be tricky depending on parent height availability
                    if obj.y == 'center':
                        if parent_container.height:
                             obj.y = (parent_container.height - obj.height) // 2
                        else:
                             obj.y = 0

                    parent_container.add_child(obj)

        instantiate_elements(sdef['elements'], panel)

        engine.screen_manager.show(panel)
        engine.Log(f"[ui] Showing screen: {name}")

    def handle_hide_screen(self, arg, engine):
        name = arg.strip().strip('\"').strip("'")
        for s in engine.screen_manager.screens[:]:
            if getattr(s, 'screen_name', None) == name:
                engine.screen_manager.hide(s)
        engine.Log(f"[ui] Hiding screen: {name}")

    def handle_ui_config(self, arg, engine):
        kwargs = self._parse_kwargs(arg)
        for k, v in kwargs.items():
            if k in engine.config:
                if isinstance(engine.config[k], dict) and isinstance(v, dict):
                    engine.config[k].update(v)
                else:
                    engine.config[k] = v
                engine.Log(f"[ui] Config updated: {k}")
            else:
                engine.Log(f"[ui] Warning: '{k}' not found in engine configuration.")

    def handle_save_screen(self, arg, engine):
        from vne.visual import SaveScreen
        screen = SaveScreen(engine)
        engine.screen_manager.show(screen)

    def handle_load_screen(self, arg, engine):
        from vne.visual import LoadScreen
        screen = LoadScreen(engine)
        engine.screen_manager.show(screen)

    def handle_prefs(self, arg, engine):
        from vne.visual import PreferencesScreen
        screen = PreferencesScreen(engine)
        engine.screen_manager.show(screen)
