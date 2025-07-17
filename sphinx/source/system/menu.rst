Menus, Button and Events
------------------------

Menu & Button
+++++++++++++
.. py:function:: @mainMenu

   Starts a menu block.
   It is expected that, after this command, @button commands will be issued to define the options.

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

Events
+++++++++++++

.. py:function:: @Scene(scene)

   Start in a spesific scene

   :param scene: Required
   :type scene: string

   :require: @buttons
   :usage: Main Menu
   :type: Action Event

.. py:function:: @Set(variable, value)

   Update a @def variable.

   :param variable: Required
   :type variable: tag

   :param value: Required
   :type value: string

   :require: @buttons

   :type: Action Event

   :usage: Choice Menu, Menu

.. py:function:: @Quit()

   Close the game
   
   :require: @buttons
   :usage: Main Menu
   :type: Action Event