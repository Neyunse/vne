Conditionals
-------------

.. py:function:: @if

   Evaluates the condition and marks the beginning of a conditional block.

   :param variable: Required
   :type variable: tag

   :type: Conditional
   :require: @def
   
.. code-block::
   :caption: scenes/first.kag
   
   @if flag
   Hola mundo
   @endif

.. py:function:: @else

   Reverses the condition in the current conditional block.

   :type: Conditional
   :require: @if
   :parent: @if
   
.. code-block::
   :caption: scenes/first.kag
   
   @if flag
   Hola mundo
   @else
   Hello world
   @endif

.. py:function:: @endif

   Closes the current conditional block.

   :type: Conditional
   :require: @if
   :parent: @if
   
.. code-block::
   :caption: scenes/first.kag
   
   @if flag
   Hello world
   @endif