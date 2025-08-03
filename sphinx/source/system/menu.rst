Menus, Button and Events
------------------------

Menu & Button
+++++++++++++
.. py:function:: @mainMenu

   Starts a menu block.
   It is expected that, after this command, @button commands will be issued to define the options.

   :param position: Optional, default is "leftTop". Other options are "leftTop", "rightTop", "leftBottom", "rightBottom" and "centerBottom"

   :param layout: Optional, default is "vertical". Other options are "horizontal"

.. py:function:: @button

   Create a button with a label
   
   :param label: Required
   :type label: string

   :param event: Required
   :type event: Action Event
   
   :type: Event

   :require: @mainMenu 
   :parent: @mainMenu
   
.. py:function:: @endMainMenu

   Close and render the menu and buttons

   :require: @mainMenu, @buttons
   :parent: @mainMenu

.. code-block::
   :caption: system/main_menu.script
   
   @mainMenu
   @button "Start" event Scene("first")
   @endMainMenu

.. py:function:: @qm

   Starts a Quick menu block.
   It is expected that, after this command, @qmBtn commands will be issued to define the options.

.. py:function:: @qmBtn

   Create a button for the Quick Menu with a label and event
   
   :param label: Required
   :type label: string

   :param event: Required
   :type event: Action Event
   
   :type: Event

   :require: @qm
   :parent: @qm
   
.. py:function:: @qmEnd

   Close and render the menu and buttons

   :require: @qm, @qmBtn
   :parent: @qm

.. code-block::
   :caption: scenes/script.script
   
   # use qm at the top of the script to create a quick menu
   @qm
   @qmBtn "Save" event Save()
   @qmEnd

   k: hello world!


Events
+++++++++++++

.. py:function:: Scene(scene)

   Start in a spesific scene

   :param scene: Required
   :type scene: string

   :require: @buttons
   :usage: Main Menu
   :type: Action Event

.. py:function:: Set(variable, value)

   Update a @def variable.

   :param variable: Required
   :type variable: tag

   :param value: Required
   :type value: string

   :require: @buttons

   :type: Action Event

   :usage: Choice Menu, Menu

.. py:function:: Quit()

   Close the game
   
   :require: @buttons
   :usage: Main Menu
   :type: Action Event

.. py:function:: Continue()

   Continues the game from last quick save
   
   :require: @buttons, Save()
   :usage: Main Menu
   :type: Action Event


.. py:function:: Save(arg)

   Saves a game in a slot. If the slot is not passed it will use the quick save slot.
   
   :require: @qmBtn
   :usage: Quick Menu
   :type: Action Event