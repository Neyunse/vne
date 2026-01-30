import pygame
import time
import re

class Theme:
    def __init__(self, **kwargs):
        self.bg_color = kwargs.get('bg_color', (50, 50, 50))
        self.border_color = kwargs.get('border_color', (255, 255, 255))
        self.button_color = kwargs.get('button_color', (100, 100, 100))
        self.button_text_color = kwargs.get('button_text_color', (255, 255, 255))
        self.font = kwargs.get('font', None)
        self.border_width = kwargs.get('border_width', 2)
        self.radius = kwargs.get('radius', 0)
        self.bg_image = kwargs.get('bg_image', None)

# Global theme instance (can be replaced at runtime)
global_theme = Theme()

class Animation:
    def __init__(self, duration=0.5):
        self.duration = duration
        self.start_time = None
        self.finished = False
    def start(self):
        self.start_time = time.time()
        self.finished = False
    def update(self, element):
        pass

class FadeAnimation(Animation):
    def __init__(self, fade_in=True, duration=0.5):
        super().__init__(duration)
        self.fade_in = fade_in
    def update(self, element):
        if self.start_time is None:
            self.start()
        elapsed = time.time() - self.start_time
        t = min(elapsed / self.duration, 1.0)
        if self.fade_in:
            element.alpha = int(255 * t)
        else:
            element.alpha = int(255 * (1 - t))
        if t >= 1.0:
            self.finished = True

class DissolveAnimation(Animation):
    def __init__(self, duration=0.5):
        super().__init__(duration)

    def update(self, element):
        if self.start_time is None:
            self.start()
        elapsed = time.time() - self.start_time
        t = min(elapsed / self.duration, 1.0)
        element.alpha = int(255 * t)
        if t >= 1.0:
            self.finished = True

class VisualElement:
    def __init__(self, x=0, y=0, width=100, height=40, visible=True, theme=None, z_index=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = visible
        self.children = []
        self.parent = None
        self.theme = theme or global_theme
        self.bg_color = None
        self.border_color = None
        self.bg_image = None
        self.border_width = None
        self.radius = None
        self.alpha = 255
        self.animations = []
        self.shadow = False
        self.shadow_color = (0,0,0,128)
        self.shadow_offset = (2,2)
        self.blur = False
        self.z_index = z_index
        self.padding = 0
        self.margin = 0
        self.hover_bg_color = None
        self.hover_border_color = None
        self.hovered = False

    def add_child(self, child):
        child.parent = self
        self.children.append(child)
    
    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def add_animation(self, animation):
        self.animations.append(animation)
        animation.start()

    def update_animations(self):
        for anim in self.animations[:]:
            anim.update(self)
            if anim.finished:
                self.animations.remove(anim)

    def render(self, surface):
        if not self.visible:
            return
        self.update_animations()
        abs_x, abs_y = self.get_absolute_position()
        
        # abs_x, abs_y = self.get_absolute_position()
        
        # Determine colors based on hover state
        bg_color = self.bg_color or self.theme.bg_color
        border_color = self.border_color or self.theme.border_color
        
        if self.hovered:
            if self.hover_bg_color: bg_color = self.hover_bg_color
            if self.hover_border_color: border_color = self.hover_border_color

        if self.bg_image is not None:
            surface.blit(self.bg_image, (abs_x, abs_y))
        else:
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, bg_color, temp_surface.get_rect(), border_radius=self.radius or self.theme.radius)
            
            border_width = self.border_width if self.border_width is not None else self.theme.border_width
            if border_width > 0:
                pygame.draw.rect(temp_surface, border_color, temp_surface.get_rect(), border_width, border_radius=self.radius or self.theme.radius)
            
            temp_surface.set_alpha(self.alpha)
            surface.blit(temp_surface, (abs_x, abs_y))
            
        self.children.sort(key=lambda c: getattr(c, 'z_index', 0))
        for child in self.children:
            child.render(surface)

    def handle_event(self, event):
        abs_x, abs_y = self.get_absolute_position()
        rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = rect.collidepoint(event.pos)
            
        for child in self.children:
            if child.handle_event(event):
                return True
        return False

    def get_absolute_position(self):
        if self.parent:
            px, py = self.parent.get_absolute_position()
            return self.x + px, self.y + py
        return self.x, self.y

    def apply_style(self, style):
        """Applies a dictionary of properties to this element."""
        for key, value in style.items():
            if hasattr(self, key):
                setattr(self, key, value)

class AutoSizedBackground(VisualElement):
    def __init__(self, x=0, y=0, width=0, height=0, theme=None, **kwargs):
        super().__init__(x, y, width, height, theme=theme, **kwargs)

    def render(self, surface):
        self.width = surface.get_width()
        self.height = surface.get_height()
        # super().render(surface)
        super().render(surface)

class TextElement(VisualElement):
    def __init__(self, text, font=None, color=(255,255,255), x=0, y=0, theme=None, **kwargs):
        super().__init__(x, y, 0, 0, theme=theme, **kwargs)
        self.text = text
        self.font = font
        self.color = color
        self._recalculate_size()

    def _recalculate_size(self):
        font = self.font or self.theme.font
        if font:
            self.width, self.height = font.size(self.text)

    def render(self, surface):
        if not self.visible: return
        self._recalculate_size()
        font = self.font or self.theme.font
        if font:
            text_surf = font.render(self.text, True, self.color)
            abs_x, abs_y = self.get_absolute_position()
            surface.blit(text_surf, (abs_x, abs_y))

class ImageElement(VisualElement):
    def __init__(self, image, x=0, y=0, width=None, height=None, theme=None, **kwargs):
        img_w = width or image.get_width()
        img_h = height or image.get_height()
        super().__init__(x, y, img_w, img_h, theme=theme, **kwargs)
        self.image = image
        if width or height:
            self.image = pygame.transform.smoothscale(image, (img_w, img_h))

    def render(self, surface):
        if not self.visible: return
        self.update_animations()
        abs_x, abs_y = self.get_absolute_position()
        
        # abs_x, abs_y = self.get_absolute_position()

        # Apply alpha if needed
        if self.alpha < 255:
            temp = self.image.copy()
            temp.set_alpha(self.alpha)
            surface.blit(temp, (abs_x, abs_y))
        else:
            surface.blit(self.image, (abs_x, abs_y))
            
        for child in self.children:
            child.render(surface)

class Button(VisualElement):
    def __init__(self, label, action, x=0, y=0, width=200, height=40, theme=None, **kwargs):
        super().__init__(x, y, width, height, theme=theme, **kwargs)
        self.label = label
        self.action = action
        self.text_color = None
        self.hover_text_color = None
        self.font = None

    def render(self, surface):
        super().render(surface) # Draw background/border
        
        abs_x, abs_y = self.get_absolute_position()
        rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
        
        font = self.font or self.theme.font
        text_color = self.text_color or self.theme.button_text_color
        if self.hovered and self.hover_text_color:
            text_color = self.hover_text_color
            
        if font:
            text_surf = font.render(self.label, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        was_handled = super().handle_event(event)
        if was_handled: return True
        
        abs_x, abs_y = self.get_absolute_position()
        rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(event.pos):
                # if callable(self.action):
                if callable(self.action):
                    self.action()
                return True
        return False

class MenuPanel(VisualElement):
    def __init__(self, 
                 x=0, 
                 y=0, 
                 width=300, 
                 height=400, 
                 layout="default", 
                 theme=None,
                 no_bg=False,
                 no_border=False,
                 is_main_menu=False,
                 is_modal=True,
                 **kwargs
        ):
        super().__init__(x, y, width, height, theme=theme, **kwargs)
        if layout == "default":
            self.layout = VerticalLayout()
        else:
            self.layout = layout
        self.no_bg = no_bg
        self.no_border = no_border
        self.modal = is_modal
        self.is_main_menu = is_main_menu

    def render(self, surface):
        if not self.visible:
            return
        abs_x, abs_y = self.get_absolute_position()
        panel_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)

        if not self.no_bg or not self.no_border:
            temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            if not self.no_bg:
                color = self.bg_color or self.theme.bg_color
                pygame.draw.rect(temp_surface, color, temp_surface.get_rect(), border_radius=self.radius or self.theme.radius)
            if not self.no_border:
                border_color = self.border_color or self.theme.border_color
                border_width = self.border_width or self.theme.border_width
                if border_width > 0:
                    pygame.draw.rect(temp_surface, border_color, temp_surface.get_rect(), border_width, border_radius=self.radius or self.theme.radius)
            temp_surface.set_alpha(self.alpha)
            surface.blit(temp_surface, (abs_x, abs_y))

        if self.layout:
            self.layout.apply(self)

        for child in self.children:
            child.render(surface)

class DialogPanel(VisualElement):
    def __init__(self, text, font=None, x=0, y=0, width=400, height=120, theme=None, **kwargs):
        super().__init__(x, y, width, height, theme=theme, **kwargs)
        self.text = text
        self.font = font
        self.text_color = (255,255,255)
        self.shadow = False
        self.shadow_offset = (2,2)
        self.shadow_color = (0,0,0,128)
        self.character_name = None  # Nuevo: nombre del personaje
        self.name_font = None       # Nuevo: fuente para el nombre
        self.name_color = self.text_color  # Color por defecto para el nombre
        self.name_bg_color = (40,40,40)  # Fondo del frame del nombre
        self.name_border_color = (255,255,255)  # Borde del frame del nombre
        self.name_border_width = 2
        self.name_radius = 5
        
        # Typewriter state
        self.full_text = text
        self.display_text = ""
        self.typewriter_speed = 30 # characters per second
        self.typewriter_index = 0
        self.last_update = 0
        self.finished_typewriter = False
        
    def set_text(self, text):
        self.full_text = text
        self.display_text = ""
        self.typewriter_index = 0
        self.last_update = pygame.time.get_ticks()
        self.finished_typewriter = False

    def finish_typewriter(self):
        self.typewriter_index = len(self.full_text)
        self.display_text = self.full_text
        self.finished_typewriter = True

    def update(self):
        if self.finished_typewriter:
            return
            
        now = pygame.time.get_ticks()
        if self.last_update == 0:
            self.last_update = now
            
        elapsed = now - self.last_update
        chars_to_add = int(elapsed * self.typewriter_speed / 1000)
        
        if chars_to_add > 0:
            self.typewriter_index = min(self.typewriter_index + chars_to_add, len(self.full_text))
            self.display_text = self.full_text[:self.typewriter_index]
            self.last_update = now
            
            if self.typewriter_index >= len(self.full_text):
                self.finished_typewriter = True
    
    def wrap_text(self, text, font, max_width):
      words = text.split(' ')
      lines = []
      current_line = ''
      for word in words:
          test_line = current_line + (' ' if current_line else '') + word
          width, _ = font.size(test_line)
          if width <= max_width:
              current_line = test_line
          else:
              lines.append(current_line)
              current_line = word
      if current_line:
          lines.append(current_line)
      return lines
  
    def render(self, surface):
        abs_x, abs_y = self.get_absolute_position()
        
        # Render Background (Image or Color)
        if hasattr(self, 'bg_image') and self.bg_image:
            img = pygame.transform.smoothscale(self.bg_image, (self.width, self.height))
            img.set_alpha(self.alpha)
            surface.blit(img, (abs_x, abs_y))
        else:
            super().render(surface)

        font = self.font or self.theme.font
        # Renderizar nombre del personaje encima del textbox si existe
        if self.character_name:
            name_font = self.name_font or font
            if name_font:
                name_surface = name_font.render(self.character_name, True, self.name_color)
                name_rect = name_surface.get_rect()
                name_rect.left = abs_x + 20
                name_rect.bottom = abs_y - 10  # Encima del textbox
                # Frame adaptado al tamaño del texto
                padding_x = 24
                padding_y = 12
                frame_rect = pygame.Rect(
                    name_rect.left - padding_x//2,
                    name_rect.top - padding_y//2,
                    name_rect.width + padding_x,
                    name_rect.height + padding_y
                )
                pygame.draw.rect(surface, self.name_bg_color, frame_rect, border_radius=self.name_radius)
                pygame.draw.rect(surface, self.name_border_color, frame_rect, self.name_border_width, border_radius=self.name_radius)
                surface.blit(name_surface, name_rect)
        if font:
          self.update() # Ensure state is updated before rendering
          max_text_width = self.width - 20  # margen interno
          lines = self.wrap_text(self.display_text, font, max_text_width)
          line_height = font.get_linesize()
          for i, line in enumerate(lines):
              y = abs_y + 10 + i * line_height
              if self.shadow:
                  shadow_surface = font.render(line, True, self.shadow_color)
                  surface.blit(shadow_surface, (abs_x + 10 + self.shadow_offset[0], y + self.shadow_offset[1]))
              text_surface = font.render(line, True, self.text_color)
              surface.blit(text_surface, (abs_x + 10, y))
class SpriteVisual(VisualElement):
    def __init__(self, image, x=None, y=None, width=None, height=None, theme=None, position="center", animation=None, **kwargs):
        screen = pygame.display.get_surface()
        win_w, win_h = (screen.get_width(), screen.get_height()) if screen else (800, 600)
        w = width or win_w
        h = height or win_h
        self.position = position
        self.custom_xy = None

        # Validar y calcular posición personalizada
        if isinstance(position, str) and re.match(r"x=\d+,y=\d+", position):
            m = re.match(r"x=(\d+),y=(\d+)", position)
            self.custom_xy = (int(m.group(1)), int(m.group(2)))
            x, y = self.custom_xy
        else:
            x, y = self.calculate_position(position, win_w, win_h, w, h)

        super().__init__(x, y, w, h, theme=theme, **kwargs)
        self.image = image
        self.alpha = 255
        self.animation = animation
        self._cached_surface = None
        self._last_win_size = (0, 0)
        
        if animation:
            self.add_animation(animation)

    def calculate_position(self, position, win_w, win_h, w, h):
        positions = {
            "center": ((win_w - w) // 2, (win_h - h) // 2),
            "left": (int(win_w * 0.1), (win_h - h) // 2),
            "right": (int(win_w * 0.9 - w), (win_h - h) // 2),
            "bottom": ((win_w - w) // 2, int(win_h * 0.9 - h)),
            "top": ((win_w - w) // 2, int(win_h * 0.1)),
            "topleft": (int(win_w * 0.1), int(win_h * 0.1)),
            "topright": (int(win_w * 0.9 - w), int(win_h * 0.1)),
            "bottomleft": (int(win_w * 0.1), int(win_h * 0.9 - h)),
            "bottomright": (int(win_w * 0.9 - w), int(win_h * 0.9 - h))
        }
        return positions.get(position, (0, 0))

    def add_animation(self, animation):
        """Agrega una animación al sprite."""
        self.animation = animation

    def update_animation(self):
        """Actualiza el estado de la animación si está activa."""
        if self.animation:
            self.animation.update(self)  # Pasar el elemento actual como argumento
            if self.animation.finished:
                self.animation = None

    def render(self, surface):
        if not self.visible:
            return

        self.update_animation()

        win_w, win_h = surface.get_width(), surface.get_height()
        target_w, target_h = self.width or win_w, self.height or win_h
        
        # Recalculate scaled surface only if window size changed or not cached
        if self._cached_surface is None or self._last_win_size != (win_w, win_h):
            img_w, img_h = self.image.get_width(), self.image.get_height()
            scale = min(target_w / img_w, target_h / img_h)
            self.new_w, self.new_h = int(img_w * scale), int(img_h * scale)
            self._cached_surface = pygame.transform.smoothscale(self.image, (self.new_w, self.new_h))
            self._last_win_size = (win_w, win_h)
            
            # Update absolute position based on new size
            if self.custom_xy:
                self.abs_x, self.abs_y = self.custom_xy
            else:
                self.abs_x, self.abs_y = self.calculate_position(self.position, win_w, win_h, self.new_w, self.new_h)

        # Draw
        if self.alpha < 255:
            self._cached_surface.set_alpha(self.alpha)
        else:
            self._cached_surface.set_alpha(255)
            
        # surface.blit(self._cached_surface, (self.abs_x, self.abs_y))
        surface.blit(self._cached_surface, (self.abs_x, self.abs_y))
        
        for child in self.children:
            child.render(surface)


class Toast(VisualElement):
    """Pequeña notificación temporal para dev-mode (texto centrado, aparece arriba)."""
    def __init__(self, text, font=None, duration=2.0, x=None, y=20, width=360, height=48, theme=None, z_index=1000):
        super().__init__(x or 0, y, width, height, theme=theme, z_index=z_index)
        self.text = text
        self.font = font or self.theme.font
        self.start_time = None
        self.duration = duration
        self.alpha = 0
        # small padding and colors
        self.bg_color = (0, 0, 0, 180)
        self.text_color = (255, 255, 255)
        self.radius = 6
        self.fade_in_duration = 0.15
        self.fade_out_duration = 0.25
        self.finished = False

    def start(self):
        self.start_time = time.time()
        self.visible = True

    def render(self, surface):
        if self.start_time is None:
            self.start()
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration + self.fade_out_duration:
            # mark finished and hide
            self.visible = False
            self.finished = True
            return

        # handle fade in/out alpha
        if elapsed < self.fade_in_duration:
            t = elapsed / max(self.fade_in_duration, 1e-6)
            self.alpha = int(255 * t)
        elif elapsed > self.duration:
            t = min((elapsed - self.duration) / max(self.fade_out_duration, 1e-6), 1.0)
            self.alpha = int(255 * (1.0 - t))
        else:
            self.alpha = 255

        # position centered horizontally if x == 0
        screen_w = surface.get_width()
        if self.x == 0:
            self.x = max(10, (screen_w - self.width) // 2)

        # draw background rect with alpha
        temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg = self.bg_color
        if len(bg) == 4:
            bg_color = (bg[0], bg[1], bg[2], int(bg[3] * (self.alpha / 255)))
        else:
            bg_color = bg
        pygame.draw.rect(temp_surface, bg_color, temp_surface.get_rect(), border_radius=self.radius)
        temp_surface.set_alpha(self.alpha)
        surface.blit(temp_surface, (self.x, self.y))

        # render text
        if self.font:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            surface.blit(text_surface, text_rect)

class VerticalLayout:
    def __init__(self, margin=10):
        self.margin = margin

    def apply(self, panel):
        y = self.margin
        for child in panel.children:
            child.x = self.margin
            child.y = y
            child.width = panel.width - 2 * self.margin
            y += child.height + self.margin
            child.height = child.height  # Mantener altura original

class HorizontalLayout:
    def __init__(self, margin=10, align="start", justify="start"):
        self.margin = margin
        self.align = align  # "start", "center", "end"
        self.justify = justify  # "start", "center", "end", "space-between", "space-around"

    def apply(self, panel):
        x = self.margin
        total_width = sum(child.width for child in panel.children) + (len(panel.children) - 1) * self.margin
        remaining_space = panel.width - total_width

        if self.justify == "center":
            x += remaining_space // 2
        elif self.justify == "end":
            x += remaining_space
        elif self.justify == "space-between" and len(panel.children) > 1:
            self.margin = remaining_space // (len(panel.children) - 1)
        elif self.justify == "space-around" and len(panel.children) > 0:
            self.margin = remaining_space // (len(panel.children) * 2)
            x += self.margin

        for child in panel.children:
            child.x = x
            child.y = self.margin
            child.height = child.height  # Mantener altura original

            x += child.width + self.margin
            
            

class GridLayout:
    def __init__(self, rows, cols, margin=10, align="start", justify="start"):
        self.rows = rows
        self.cols = cols
        self.margin = margin
        self.align = align  # "start", "center", "end"
        self.justify = justify  # "start", "center", "end", "space-between", "space-around"

    def apply(self, panel):
        cell_w = (panel.width - (self.cols + 1) * self.margin) // self.cols
        cell_h = (panel.height - (self.rows + 1) * self.margin) // self.rows

        for idx, child in enumerate(panel.children):
            row = idx // self.cols
            col = idx % self.cols

            x = self.margin + col * (cell_w + self.margin)
            y = self.margin + row * (cell_h + self.margin)

            if self.align == "center":
                x += (cell_w - child.width) // 2
            elif self.align == "end":
                x += cell_w - child.width

            if self.justify == "center":
                y += (cell_h - child.height) // 2
            elif self.justify == "end":
                y += cell_h - child.height

            child.x = x
            child.y = y
            child.width = cell_w
            child.height = cell_h

class SlideAnimation(Animation):
    def __init__(self, start_pos, end_pos, duration=0.5):
        super().__init__(duration)
        self.start_pos = start_pos
        self.end_pos = end_pos
    def update(self, element):
        if self.start_time is None:
            self.start()
        elapsed = time.time() - self.start_time
        t = min(elapsed / self.duration, 1.0)
        element.x = int(self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t)
        element.y = int(self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t)
        if t >= 1.0:
            self.finished = True

class ScaleAnimation(Animation):
    def __init__(self, start_scale, end_scale, duration=0.5):
        super().__init__(duration)
        self.start_scale = start_scale
        self.end_scale = end_scale
    def update(self, element):
        if self.start_time is None:
            self.start()
        elapsed = time.time() - self.start_time
        t = min(elapsed / self.duration, 1.0)
        scale = self.start_scale + (self.end_scale - self.start_scale) * t
        element.width = int(element.width * scale)
        element.height = int(element.height * scale)
        if t >= 1.0:
            self.finished = True

class FlexLayout:
    def __init__(self, direction="row", align="start", justify="start", gap=10):
        self.direction = direction  # "row" or "column"
        self.align = align  # "start", "center", "end"
        self.justify = justify  # "start", "center", "end", "space-between", "space-around"
        self.gap = gap

    def apply(self, panel):
        x, y = 0, 0
        if self.direction == "row":
            for child in panel.children:
                child.x = x
                child.y = y
                x += child.width + self.gap
        elif self.direction == "column":
            for child in panel.children:
                child.x = x
                child.y = y
                y += child.height + self.gap
