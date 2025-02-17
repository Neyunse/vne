Dialogue
--------

Dialogs are used to tell or write a story in a visual novel. The way |product| writes dialogs may differ from other engines, however, it is easy to use. |product| uses as well as Ren'Py
say statements.

Say Statements
++++++++++++++

.. code-block::
   :caption: scenes/first.kag
   
   This is a dialog 
   k: hello!


Say Interpolation
******************

|product| supports the possibility of inserting variables in the dialogs. For example, to show the name of a character, "{}" is used.

.. code-block::
   :caption: scenes/first.kag
   
   k: hello! my name is {k}

|product| can insert variables defined with:

- @def
- @scene 
- @char

Creating a Character
++++++++++++++++++++

Characters are created by using "@char" to add it to a variable.

.. py:function:: @char

   Define a character to use in dialogues

   :param character: Required
   :type character: tag
   
   :param as: Optional
   :type as: modifier

   :type: Definition

   :return: The character name or variable instead

.. code-block::
   :caption: system/characters.kag
   
   @char k as "Kuro"

note that if you do not pass "as" and the display name, the variable name will be used instead.

.. code-block::
   :caption: system/characters.kag
   
   @char k


You can also use a character without defining it with "@char", however, you will not be able to access the character's name from another dialog line or outside the scene.

.. code-block::
   :caption: scenes/first.kag
   
   ayumi* Hello my name is {ayumi}


.. admonition:: Information
   :class: Important

   "*" invokes an exception to write a character without defining it, it may be valid in some cases but it is not recommended.

Rename Character
******************

You can rename an already defined character using "@rename", this can be useful if you use characters as npc or characters that do not have a name at the beginning.

.. py:function:: @rename

   Rename a character

   :param character: Required
   :type character: tag
   
   :param as: Optional
   :type as: modifier
   :require: @char
   :type: Event

.. code-block::
   :caption: scenes/first.kag
   
   @rename k as "Kuromi"

Choice Menu
+++++++++++++

.. py:function:: @choice

   Starts a choice block.
   It is expected that, after this command, @option commands will be issued to define the options.

.. py:function:: @option

   Create a button with a label
   
   :param label: Required
   :type label: string

   :param event: Required
   :type event: Action Event
   
   :type: Event

   :require: @choice, @end_choice, Set()
   :parent: @choice

.. py:function:: @end_choice

   Close and render the menu and buttons

   :require: @choice, @options
   :parent: @choice

.. code-block::
   :caption: scenes/first.kag
   
   @choice
   @option "Start" event Set(var, true)
   @end_choice

Primitive Say
++++++++++++++++

.. py:function:: @say

   Primitive say statement event 

   :param character: Optional
   :type character: tag
   
   :param dialog: Required
   :type dialog: string

   :type: primitive event

   :return: The dialog with the character or only the dialog

.. code-block::
   :caption: scenes/first.kag
   
   @say Hello World!
   @say k: Hello my name is {k}
   @say ayumi* Hi! {k} my name is {ayumi}
