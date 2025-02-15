Images
---------

|product| and like many other visual novel engines use images to display scenes, sprites or any other resource.

Supported files
*******************

- **Sprites**: :file:`images/sprites/**.png`
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

   :type: Rendering

.. code-block::
   :caption: scenes/first.kag
   
   @sprite kuro

.. admonition:: Note
   :class: tip

   If your image is located in a subdirectory you can define it as :file:`@sprite kuro/kuro_happy`.


Hide a sprite
++++++++++++++

.. py:function:: @hide
    
    Hide a specific sprite

   :param filename: Required
   :type filename: tag
   :require: @sprite
   :type: Rendering

.. code-block::
   :caption: scenes/first.kag
   
   @hide kuro


Showing a Background
*********************
.. py:function:: @bg
    
    Show a Background

   :param filename: Required
   :type filename: tag

   :type: Rendering

.. code-block::
   :caption: scenes/first.kag
   
   @bg bedroom

.. admonition:: Note
   :class: tip

   If your image is located in a subdirectory you can define it as :file:`@bg home/bedroom`.
