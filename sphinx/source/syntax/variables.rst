Variables
---------

Variables allow you to store a state or a specific value. Normally they can be used to define conditionals or store some kind of data.

Defining a Variable
++++++++++++++++++++

.. py:function:: @def
    
    Define a variable with a value

   :param variable: Required
   :type variable: tag

   :param value: Required
   :type value: string | bool

   :type: Definition

.. code-block::
   :caption: system/vars.kag
   
   @def helloWorld = "Hello World!!!"

Updating a Variable value
*************************

.. py:function:: @set
    
   Update a @def variable

   :param variable: Required
   :type variable: tag

   :param value: Required
   :type value: string | bool

   :type: Definition
   :require: @def

.. code-block::
   :caption: scenes/first.kag
   
   @set helloWorld = "¡Hello World! This is a vn engine variable!"