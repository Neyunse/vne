class StyleManager:
    def __init__(self):
        self.styles = {}

    def define(self, name, parent=None, **properties):
        """Defines a new style with the given name and properties, optionally inheriting from a parent."""
        if name not in self.styles:
            self.styles[name] = {}
        
        if parent:
            parent_style = self.get(parent)
            self.styles[name].update(parent_style)
            
        self.styles[name].update(properties)

    def get(self, name, default=None):
        """Returns the properties of a style, or a default value."""
        return self.styles.get(name, default or {})

    def apply(self, element, style_name):
        """Applies a style to a visual element."""
        style = self.get(style_name)
        for key, value in style.items():
            if hasattr(element, key):
                setattr(element, key, value)
            elif key == "font_size" and hasattr(element, "font"):
                # Handle dynamic font resizing if possible
                pass
            # More specialized mappings can go here
