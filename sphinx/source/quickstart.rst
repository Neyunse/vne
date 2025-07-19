Quickstart
----------

To start download the |currentLink| 

The engine
++++++++++

The engine has an easy to understand and use UI, allows you to create, debug, edit scripts and build projects easily and quickly.



Folder Structure
++++++++++++++++++++
 
::

        ├── engine.exe        
        ├── projects
        │    ├── test-game/          
        │       ├── data/         
        │       ├── system/       
        │       ├── images/  
        │       ├── scenes/   
                ├── ui/   
                └── startup.script   
 

How to start
++++++++++++++++++++

To start creating a project, use the “New Project” button to create your project by choosing a title and the name of the directory to be used. remember to use the format XXX-XXX-XXX in the directory name if you decide to change it.

**Simple dialog**

to start writing your stories you must edit :file:`scenes/first.script`, this file is very easy to edit. No experience is required
programming experience is not required, as it is plain text.

.. code-block::
   :caption: scenes/first.script

   # This is a dialog without an assigned character.
   Hello world!

|product| is prepared to be easy to use, the :file:`*.script` files placed inside :file:`scene/**` are interpreted as labels or levels, so each file is unique.

**Add characters**

You can add your own characters easily, |product| use :file:`system/characters.script` as a starting point for you to define your characters.

.. code-block::
   :caption: scenes/first.script

   @char k as "Kuro"
 
then in your file :file:`scenes/first.script` you can use it in an easy way.

.. code-block::
   :caption: scenes/first.script

   k: Hello world!
 
**Adding Sprites & Backgrounds**

.. code-block::
   :caption: scenes/first.script

   @bg school
   @sprite kuro
   k: Hello world!
   k: This is my story...
 
Sprites and Backgrounds are a fundamental part of visual novels, to use your images place the files correctly in their respective folders.
|product| has predetermined formats, so you must use the images correctly.

- **Sprites**: :file:`*.png`
- **Backgrounds**: :file:`*.jpg`

|product| will look for the file in the corresponding folder with the name you are defining.

**Script comments**

If you want to write comments or prevent something from running by using "#" 

.. code-block::
   :caption: scenes/first.script

   # TODO: This is my comment for you!
   # @sprite sayuri_normal this line is excluded
   k: This is the beginning # TODO: Wow nice dialogue line!
 
**Jumping betwent scenes**

|product| adds the possibility to jump between scenes in an easy way using "jump_scene". 

.. code-block::
   :caption: scenes/first.script
   
   @bg school
   @sprite kuro
   k: Hello world!
   k: This is my story...
   @jump_scene second
 

However, you must keep in mind that you must define the scenes in :file:`system/scenes.script` in order to use them, since from the
new scenes you create are disconnected from the flow of your project.

**Test your game**

Once you have finished editing your project, you can use the play button from the toolbar menu in the editor view or from the start by clicking on the green button.

**Export your project**

To export your project, enter the editor and then click on the hammer emoji. This will generate a folder “/dist/*”.