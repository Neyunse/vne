# Visual Novel Engine (VNEngine)

**VNEngine** is a visual novel engine developed in Python using Pygame. It offers a flexible and simple way to create visual novels with support for characters, backgrounds, sprites, dialogues, conditions, and labels.

>INFO: The name of the engine is temporary!

## Features

- **Easy setup**: Define variables, characters, backgrounds, sprites, and more using simple commands in a script file.
- **Pygame-based engine**: Rendering of graphics and event handling via Pygame.
- **Flow logic support**: Use of labels, scene jumps, and conditions to control the narrative flow. (beta)
- **Debugging tools**: Automatic event logging and error handling support.

## Installation (build)

1. Download the executable (https://github.com/Neyunse/vne/releases)
2. Put the SDK in a folder with the name of your project and Run the engine (vne.exe)
3. Edit
4. Have fun!

## Installation (SRC)

1. Clone this repository:
   ```bash
   git clone https://github.com/Neyunse/vne
   cd vne
   ```

2. Install necessary dependencies:
   ```bash
   pip install pygame
   ```

3. Run the engine:
   ```bash
   python engine.py
   ```
### Requirements

* Pygame

## Project Structure

```plaintext
.
├── vne.exe            # SDK / engine.
├── game/              # Folder for game files.
│   ├── assets/        # Contains game resources.
│   │   ├── bg/        # Background images.
│   │   └── sprites/   # Character images.
│   └── script.kag     # Main script file.
```

## Script Syntax

The `script.kag` file uses a simple syntax to define the flow of the visual novel. Some key commands include:

>Note: the engine does not support "choice menus", "saving", or "loading" at the moment. It also has no user interface.

- **Initial setup**:
  ```plaintext
  @game_title "Visual Novel Title"

  # by default icon.png and it should be placed next to engine.exe
  # to customize the name, use this format.
  # However, note that it should not contain .png, .jpg, etc.
  # and must be in the root alongside engine.exe
  # @game_icon my_icon_name
  ```

- **Character definition**:
  ```plaintext
  @char Sayuri
  ```

- **Variable definition**:
  ```plaintext
  @var test = "test"

  Sayuri: {test}

  @setVar test = "hello world!"

  Sayuri: {test}
  ```

> Note: Variables are not very useful at the moment.

- **Renaming a character**:
  ```plaintext
  @renameChar Sayuri = Ami
  ```
> Note: Renaming a character does not change its definition, only the displayed name. Both the defined value and the renamed name are unique and cannot have two of the same type.

- **Dialogues**:
  ```plaintext
  Sayuri: Hello, world!
  ```

- **Backgrounds**:
  ```plaintext
  @background forest = "forest.jpg"
  # @bg forest
  ```

- **Versioning**
  ```plaintext
  @game_version 1.0.0
  ```

- **Sprites**:
  ```plaintext
  @sprite sayuri_happy = "sayuri_happy.png"
  # @show_sprite sayuri_happy 
  ```

- **Hide sprites**:
  ```plaintext
  # @remove_sprite sayuri_happy 
  ```

>INFO: Backgrounds and Sprites should only include the name and their format. The engine will search for them in the appropriate folders.

>Note: Sprites are under development and may not work correctly. Only one sprite will be shown; others might be overwritten if changed. (Backgrounds could also be affected by this bug).

- **Scenes**:
  ```plaintext
  @scene start
    Sayuri: This is the beginning
    @change_scene end

    Sayuri: I returned to the beginning! Now I will finish my story
    @endScene

  @scene end
    Sayuri: I’m at the end! Now I’ll return to the beginning
    @return
  ```

>INFO: `@return` returns to a line after changing scenes.

>INFO: All `@scene` need to be closed with `@endScene`, except when using `@return`.

## Example Script

```plaintext
@game_title "My First Visual Novel"

@char Sayuri
@background park = "park.jpg"
@sprite sayuri_normal = "sayuri.png"
@sprite sayuri_happy = "sayuri-happy.png"
@scene start
    @bg park
    @show_sprite sayuri_normal
    Sayuri: Welcome to our visual novel!
    @show_sprite sayuri_happy
    @remove_sprite sayuri_normal
    Sayuri: Enjoy the experience.
@endScene
```

## How to Customize

1. **Edit `script.kag`**: Modify the script to add your own story.
2. **Add resources**: Place background images in `game/assets/bg` and sprites in `game/assets/sprites`.
3. **Run**: Rerun `vne.exe` to see the changes.

## License

VNengine © 2024 by Neyunse is licensed under Creative Commons Attribution-NoDerivatives 4.0 International

## Contributions

Feel free to fork and contribute to this engine.

---