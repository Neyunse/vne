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
        #self.register_event("menu", self.handle_menu)
        # Registrar acciones para el menú:
        self.register_event("Start", self.handle_process_scene)  # Start("scene_alias")
        self.register_event("Quit", self.handle_exit)            # Quit()
    
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
        Procesa un diálogo.
          - Con speaker: <speaker>: <dialogue>
          - Sin speaker: simplemente el diálogo.
        Reemplaza marcadores {alias} buscando en engine.characters y engine.scenes.
        Si se usa un speaker que no está definido, lanza un error.
        """
        if ':' in arg:
            speaker, dialogue = arg.split(":", 1)
            speaker = speaker.strip()
            dialogue = dialogue.strip()
            if speaker not in engine.characters:
                raise Exception(f"[ERROR] El personaje '{speaker}' no está definido.")
            else:
                speaker = engine.characters[speaker]
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
            full_text = f"{speaker}: {dialogue}"
        else:
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
    
    def handle_bg(self, arg, engine):
        bg_path = os.path.join(engine.game_path, "data", "images", "bg", arg)
        if os.path.exists(bg_path):
            try:
                image = pygame.image.load(bg_path)
                image = pygame.transform.scale(image, (engine.renderer.screen.get_width(),
                                                         engine.renderer.screen.get_height()))
                engine.current_bg = image
            except Exception as e:
                raise Exception(f"[ERROR] Error al cargar la imagen de fondo: {e}")
        else:
            raise Exception(f"[ERROR] Imagen de fondo no encontrada: {bg_path}")
    
    def handle_exit(self, arg, engine):
        print("Evento 'exit':", arg)
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
                from vne.xor_data import xor_data
                from vne.config import key
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
                from vne.lexer import ScriptLexer
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

    
    def handle_menu(self, arg, engine):
        """
        Procesa un menú definido en bloque usando la siguiente sintaxis:
        
        @menu
        #Una lista de botones dentro de @menu
        button "Iniciar juego" action Start("second")
        button "Cerrar" action Quit()
        @endMenu
        
        Esta función:
        - Extrae las líneas entre @menu y @endMenu.
        - Elimina comentarios inline (todo lo que sigue a "#") y líneas vacías.
        - Verifica que cada línea siga el formato: 
                button "Etiqueta" action <comando>
        - Crea un panel semitransparente en el centro de la pantalla con las opciones.
        - Permite navegar con las teclas UP/DOWN y confirmar con Enter.
        - Una vez seleccionada la opción, añade el prefijo "@" si es necesario y ejecuta el comando.
        """
        import pygame
        import re

        # Dividir el bloque en líneas
        lines = arg.splitlines()
        options = []
        pattern = r'^button\s+"([^"]+)"\s+action\s+(.+)$'
        
        # Procesar cada línea: ignorar la línea de cierre '@endMenu'
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.lower() == "@endmenu":
                continue
            # Eliminar comentarios inline (todo lo que aparezca después de "#")
            if "#" in line:
                line = line.split("#", 1)[0].strip()
            match = re.match(pattern, line)
            if match:
                label = match.group(1)
                action = match.group(2).strip()
                options.append({"label": label, "action": action})
            else:
                raise Exception(f"[ERROR] Formato inválido en línea de menú: {line}")
        
        if not options:
            raise Exception("[ERROR] El menú no tiene opciones definidas. Verifica la sintaxis del bloque @menu.")

        # Variables para el menú personalizado
        selected_index = 0
        font = engine.renderer.font
        screen = engine.renderer.screen
        clock = engine.clock
        running = True

        # Calcular dimensiones y posición del panel de menú (centrado horizontal y verticalmente)
        panel_width = engine.config["screen_width"] - 200
        panel_height = len(options) * 60 + 20
        panel_x = 100
        panel_y = (engine.config["screen_height"] - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

        while running and engine.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    engine.running = False
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        running = False
                        break

            # Dibujar un overlay semitransparente para enfocar el menú
            overlay = pygame.Surface((engine.config["screen_width"], engine.config["screen_height"]), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            # Dibujar el panel de menú
            pygame.draw.rect(screen, (50, 50, 50), panel_rect)  # Fondo oscuro
            pygame.draw.rect(screen, (255, 255, 255), panel_rect, 2)  # Borde blanco
            
            # Dibujar las opciones
            for i, option in enumerate(options):
                color = (255, 255, 0) if i == selected_index else (255, 255, 255)
                text_surface = font.render(option["label"], True, color)
                text_rect = text_surface.get_rect()
                text_rect.centerx = panel_rect.centerx
                text_rect.top = panel_rect.top + 10 + i * 60
                screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            clock.tick(30)

        # Obtener la acción seleccionada
        selected_action = options[selected_index]["action"]
        # Si la acción no comienza con "@", se añade el prefijo
        if not selected_action.startswith("@"):
            selected_action = "@" + selected_action
        print(f"[menu] Acción seleccionada: {selected_action}")
        self.handle(selected_action, engine)
