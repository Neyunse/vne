Images
---------

|product| and like many other visual novel engines use images to display scenes, sprites or any other resource.

Supported files
*******************

- **Sprites**: :file:`images/sprites/**/**.png`
- **Background**: :file:`images/bg/**.jpg`
- **window_icon**: :file:`ui/icon/window_icon.jpg`
- **SplashScreen**: :file:`ui/splash.jpg`

.. admonition:: Important
   :class: Important

   Remember to correctly place the images in their respective folders before defining/showing them.

Showing a sprite
*******************
.. py:function:: @sprite
    
    Show an sprite

   :param filename: Required
   :type filename: tag

   :param variation: Optional, default is `default`
   :type variation: modifier

   :param position: Optional, default is `center`
   :type position: string

   :param animation: Optional, default is `none`
   :type animation: string, valid values are `dissolve`, `fadein`, `fadeout`

   :type: Rendering

.. code-block::
   :caption: scenes/first.script
   
   @sprite kuro

.. admonition:: Note
   :class: tip

   If you want to use a variation of the sprite you can define it as :file:`@sprite kuro:variation`, where `variation` is the name of the sprite variation. like `kuro:happy` or `kuro:sad`.
   
   That will use the image :file:`images/sprites/kuro/kuro_happy.png` or :file:`images/sprites/kuro/kuro_sad.png` respectively.
   If you want to use the default sprite you can define it as :file:`@sprite kuro`, but you need to have the image :file:`images/sprites/kuro/kuro_default.png`.

.. admonition:: Note
   :class: Important

   At the moment only 1 sprite can be displayed on the screen.


Showing a Background
*********************
.. py:function:: @bg
    
    Show a Background

   :param filename: Required
   :type filename: tag

   :type: Rendering

.. code-block::
   :caption: scenes/first.script
   
   @bg bedroom

.. admonition:: Note
   :class: tip

   If your image is located in a subdirectory you can define it as :file:`@bg home/bedroom`.
