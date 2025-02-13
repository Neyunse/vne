# Quickstart


The engine
----------

The engine does not have a graphical interface, so most of the time it must be used from the CLI/Terminal.

**CLI**

- **-i**: If the engine will run in project creation mode, **-f** and **-p** are required.
- **-r**: If the engine will run in project execution mode, **-f** is required.
- **-d**: If the engine will run in distribution mode, **-f** is required.
- **-f**: If this is present, the engine expects you to provide the name of the folder where your project is located.
- **-p**: If this option is present, the engine expects you to provide the name of your project (different from **-f**), **-f** and **-i** are required.


Folder Structure
----------------
 
```
├── engine.exe        
├── test-game/          
│   ├── data/         
│   │   ├── system/       
│   │   ├── images/  
│   │   ├── scenes/   
        ├── ui/   
        └── startup.kag   
```

How to start
------------

To create your first project is to run the terminal and run the engine in project creation mode.

```
.\engine.exe -f test-game -p "My awasome game" -i
```

**Simple dialog**

to start writing your stories you must edit :file:`scenes/first.kag`, this file is very easy to edit. No experience is required
programming experience is not required, as it is plain text.

```
# This is a dialog without an assigned character.
Hello world!
```

|product| is prepared to be easy to use, the :file:`*.kag` files placed inside :file:`scene/**` are interpreted as labels or levels, so each file is unique.

**Add characters**

You can add your own characters easily, |product| use :file:`system/characters.kag` as a starting point for you to define your characters.

```
@char k as "Kuro"
```
then in your file :file:`scenes/first.kag` you can use it in an easy way.
```
k: Hello world!
```
**Adding Sprites & Backgrounds**

```
@bg school
@sprite kuro
k: Hello world!
k: This is my story...
```
Sprites and Backgrounds are a fundamental part of visual novels, to use your images place the files correctly in their respective folders.
|product| has predetermined formats, so you must use the images correctly.

- **Sprites**: :file:`*.png`
- **Backgrounds**: :file:`*.jpg`

|product| will look for the file in the corresponding folder with the name you are defining.

**Script comments**

If you want to write comments or prevent something from running by using "#" 

```
# TODO: This is my comment for you!
# @sprite sayuri_normal this line is excluded
k: This is the beginning # TODO: Wow nice dialogue line!
```
**Jumping betwent scenes**

|product| adds the possibility to jump between scenes in an easy way using "jump_scene". 

```
@bg school
@sprite kuro
k: Hello world!
k: This is my story...
@jump_scene second
```

However, you must keep in mind that you must define the scenes in :file:`system/scenes.kag` in order to use them, since from the
new scenes you create are disconnected from the flow of your project.

**Test your game**

Once you have finished editing to your liking you can preview your project using
``` 
.\engine.exe -f test-game -r
```
**Export your project**

To export your project you need to use the CLI/Terminal to distribute your game...
```
.\engine.exe -f test-game -d
```
