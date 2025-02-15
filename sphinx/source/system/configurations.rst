Configurations
--------------


.. py:function:: @Display(width,height)

   Configures the window size and updates the configuration of the interface elements.

   :param width: Required
   :type width: number

   :param height: Required
   :type height: number
   
   :type: Configuration
   
.. code-block::
   :caption: system/ui.kag
   
   @Display(800,800)


.. py:function:: @GameTitle(title)

   Change the window title of the game

   :param title: Required
   :type title: string
   
   :type: Configuration
   
.. code-block::
   :caption: system/ui.kag
   
   @GameTitle("My Awasome Game!")

.. py:function:: @GameIconName(filename)

   Change the window icon placed in :file:`/ui/icon/**.jpg`

   :param filename: Required
   :type filename: string
   
   :type: Configuration
   
.. code-block::
   :caption: system/ui.kag
   
   @GameIconName("window_icon")