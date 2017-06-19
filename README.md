# ARoboCar

Unreal Engine car simulator for training our self driving car. Includes a scene capture class.

This project requires UnrealEnginePython. There  should be a way to add this dependency to the build
system, but for now just run the following commands ONCE.
```
>cd Plugins
>git clone https://github.com/20tab/UnrealEnginePython.git
```

When the editor is first launched it will ask if the library should be rebuilt. Confirm 'yes' and it will build the editor.

The project will run the AIAgent.py from the Content/Scripts directory.
