Audio
--------

Supported files
*******************

- **BGM**: :file:`audio/bgm/**.mp3`
- **SFX**: :file:`audio/sfx/**.mp3`

Background Music
*******************

.. py:function:: @bgm
    
    Play a music in the bgm channel

   :param filename: Required
   :type filename: tag

   :type: Audio

.. code-block::
   :caption: scenes/first.script
   
   @bgm 70_love

.. admonition:: Note
   :class: tip

   If your music is located in a subdirectory you can define it as :file:`@bgm main/70_love`.


Background Music
*******************

.. py:function:: @sfx
    
    Play a music in the sfx channel

   :param filename: Required
   :type filename: tag

   :type: Audio

.. code-block::
   :caption: scenes/first.script
   
   @sfx phone

.. admonition:: Note
   :class: tip

   If your sfx is located in a subdirectory you can define it as :file:`@sfx phone_resources/phone`.
