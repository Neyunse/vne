1.0.0-alpha.12
--------------

**Fixes**

**Changes**

- Game optimizations to improve performance.
- Added support for sprite transitions, allowing for smoother visual effects. `@sprite kuro animation="dissolve"`
- Added support for position sprites, allowing sprites to be positioned relative to the screen or other elements. `@sprite kuro position="center"`, `@sprite kuro position="left"`, `@sprite kuro position="right"`
- Updated the engine to use `pygame-ce` for better performance and compatibility.
- Now sprites can use alternative sprites more easily. `@sprite kuro` will use `kuro_default.png` as the sprite, and `@sprite kuro:alternative` will use `kuro_alternative.png`. for example, `@sprite kuro:happy` will use `kuro_happy.png` and `@sprite kuro:sad` will use `kuro_sad.png`.
- Now @mainMenu can use `layout` and `position` parameters to customize the menu layout and position. `@mainMenu layout="horizontal" position="centerBottom"` will create a horizontal menu at the bottom center of the screen.

:gh_release:`v1.0.0-alpha.12`

....