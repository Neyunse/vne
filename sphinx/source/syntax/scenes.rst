Scenes
------

|product| uses a scene system similar to KiriKiri to structure your story, the scenes must be created inside the :file:`/scenes/**.kag` folder.

::

        ├── engine.exe        
        ├── test-game/          
        │   ├── data/         
        │   │   ├── scenes/   
                    ├── first.kag
                    └── hello.kag 

Defining a Scene
+++++++++++++++++

By default |product| does not detect scenes created inside :file:`/scenes/**.kag`, to use them you need to define them first.

.. py:function:: @scene

   Define a scene

   :param scene: Required
   :type scene: tag

   :param value: Required
   :type value: string

   :type: Definition
   
.. code-block::
   :caption: system/scenes.kag
   
   @scene first = "first"
   @scene second = "second"

Jumping between scenes
++++++++++++++++++++++

The jump between scenes is a common method in branching visual novels, it allows you to travel between scenes.

.. py:function:: @jump_scene

   Jump between defined scenes

   :param scene: Required
   :type scene: tag
   :require: @scene
.. code-block::
   :caption: scenes/first.kag
   
   k: hello! my name is {k}
   @jump_scene second

Checkpoints
+++++++++++

Un checkpoint te permite establecer un punto de retorno, esto puede ser util si necesitas usar variables que cambian una accion en espesifico del juego.

.. py:function:: @checkpoint

   Saves a checkpoint with a label and the current script line.

   :param label: Required
   :type label: tag

   :type: Definition

   
.. code-block::
   :caption: scenes/first.kag
   
   k: hello! my name is {k}
   @checkpoint myNiceCheckPoint
   @jump_scene second

.. py:function:: @goto
    
    Jumps to a specific checkpoint in the script based on the given label.

   :param label: Required
   :type label: tag
   :require: @checkpoint
   :type: Event

.. code-block::
   :caption: scenes/second.kag
   
   Oh, i need go back!!
   @goto myNiceCheckPoint