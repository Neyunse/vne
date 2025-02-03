# engine/vne/config.py

# Configuración del motor
# engine/vne/config.py
CONFIG = {
    "screen_width": 800,
    "screen_height": 600,
    "fullscreen": False,
    "font_name": "Arial",
    "font_size": 24,
    "bg_color": (0, 0, 0),  # Color de fondo en ausencia de imagen
    "dialogue_rect": { 
         "x": 50, "y": 450, "width": 700, "height": 120,
         "bg_color": (50, 50, 50),
         "border_color": (255, 255, 255)
    }
}




def say(character, dialogue):
    """
    Muestra un diálogo en la consola.
    """
    print(f"{character}: {dialogue}")

def menu(options):
    """
    Muestra un menú en la consola y retorna la opción seleccionada.
    """
    print("Menú:")
    for idx, option in enumerate(options, start=1):
        print(f"{idx}. {option}")
    while True:
        try:
            choice = int(input("Seleccione una opción: "))
            if 1 <= choice <= len(options):
                return choice - 1
            else:
                print("Opción no válida. Intente de nuevo.")
        except ValueError:
            print("Entrada no válida. Ingrese un número.")
