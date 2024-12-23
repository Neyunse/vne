# Visual Novel Engine (VNEngine)

**VNEngine** es un motor para novelas visuales desarrollado en Python utilizando Pygame. Ofrece una forma flexible y sencilla de crear novelas visuales con soporte para personajes, fondos, sprites, diálogos, condiciones y etiquetas.

## Características

- **Fácil configuración**: Define variables, personajes, fondos, sprites y más utilizando comandos simples en un archivo de script.
- **Motor basado en Pygame**: Renderizado de gráficos y manejo de eventos mediante Pygame.
- **Soporte de lógica de flujo**: Uso de etiquetas, saltos entre escenas y condiciones para controlar el flujo narrativo. (beta)
- **Herramientas de depuración**: Registro automático de eventos y soporte para manejo de errores.

## Instalación (build)

1. Descarga el ejecutable

2. Ejecuta el motor (engine.exe)

3. Edita

4. Diviertete!

## Instalación (SRC)

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tuusuario/vnengine.git
   cd vnengine
   ```

2. Instala las dependencias necesarias:
   ```bash
   pip install pygame
   ```

3. Ejecuta el motor:
   ```bash
   python engine.py
   ```

## Estructura del Proyecto

```plaintext
.
├── vne.exe            # SDK / motor.
├── game/              # Carpeta para los archivos del juego.
│   ├── assets/        # Contiene recursos del juego.
│   │   ├── bg/        # Imágenes de fondo.
│   │   └── sprites/   # Imágenes de personajes
│   └── script.kag     # Archivo de script principal.

```

## Sintaxis del Script

El archivo `script.kag` utiliza una sintaxis sencilla para definir el flujo de la novela visual. Algunos comandos principales incluyen:

>Nota: el motor no soporta "menus de elecciones", "guardado", "carga de partidas" por el momento. Y no tiene interfaz de usuario.

- **Configuración inicial**:
  ```plaintext
  @game_title "Título de la Novela Visual"
  
  # By default 1280 720 is recommended, you can change the size but you can see problems.
  # @game_size 1280 720

  # por defecto icon.png y se debe colocar junto a engine.exe
  # en caso de personalizar el nombre usa la siguiente forma.
  # Sin embargo, tenga en cuenta que no debe contener .png,.jpg, etc
  # y debe estar en la raiz junto a engine.exe
  # @game_icon my_icon_name
  ```

- **Definición de personajes**:
  ```plaintext
  @char Sayuri
  ```

- **Definición de variables**:
  ```plaintext
  @var test = "test"

  Sayuri: {test}

  @setVar test = "hello world!"

  Sayuri: {test}
  ```

> Nota: las variables no tienen un uso importante en este momento.

- **Renombrar personaje**:
  ```plaintext
  @renameChar Sayuri = Ami
  ```
> Nota: Renombrar un personaje no cambia su definicion, solo el nombre a mostrar. Tanto el valor definido como el nombre renombrado son unicos y no puede haber 2 del mismo tipo.


- **Diálogos**:
  ```plaintext
  Sayuri: ¡Hola, mundo!
  ```

- **Fondos**:
  ```plaintext
  @background bosque = "forest.jpg"
  # @bg bosque
  ```

- **Sprites**:
  ```plaintext
  @sprite sayuri_happy = "sayuri_happy.png"
  # @show_sprite sayuri_happy x=100 y=200 zoom=0.7
  ```
>INFO: Los fondos y los Sprites deben ser solamente los nombres y su formato, el motor se encarga de buscarlos en la carpetas correspondientes

>Nota: Los sprites estan en fase de desarrollo y no funcionan bien, solo se mostrara 1 sprite, el resto puede sobrescribirse con el ultimo si se intenta cambiar. (es probable que los background tambien sean afectados por este bug)

- **Escenas**:
  ```plaintext
  @scene inicio
    Sayuri: Este es el comienzo
    @change_scene final

    Sayuri: Regrese al comienzo! ahora terminare mi historia
    @endScene

  @scene final
    Sayuri: Estoy en el final! Ahora regresare al comienzo
    @return
    
  ```
>INFO: `@return` retorna a una linea despues de que se cambio de escena

## Ejemplo de Script

```plaintext
@game_title "Mi Primera Novela Visual"
@game_size 1280 720

@char Sayuri
@background parque = "park"
@sprite sayuri_normal = "sayuri"

@scene inicio
    @bg parque
    @show_sprite sayuri_normal
    Sayuri: ¡Bienvenidos a nuestra novela visual!
    Sayuri: Disfruten la experiencia.
@endScene
```

## Cómo Personalizar

1. **Editar `script.kag`**: Modifica el script para añadir tu propia historia.
2. **Añadir recursos**: Coloca imágenes de fondo en `game/assets/bg` y sprites en `game/assets/sprites`.
3. **Ejecutar**: Vuelve a ejecutar `vne.exe` para ver los cambios.

## Licencia

VNengine © 2024 by Neyunse is licensed under Creative Commons Attribution-NoDerivatives 4.0 International 

## Contribuciones

Sientete libre de crear un fork y contribuir a este motor.

---