# PEAS
** Python Extendable Assembler and Simulator **

## Idea
...

## Project structure
- **application.py** - Main module, puts everything together
- **simulators/**
    - **simulator.py** - Abstract base class for simulators
    - **frisc_simulator.py** - FRISC processor simulator
- **assemblers/**
    - **assembler.py** - Abstract base class for assemblers
    - **frisc_assembler.py** - FRISC processor assembler
- **utils/** - Utility functions and classes
    - **binary.py** - Implements binary arithmetic and display functions
    - **helpers.py** - Other, unsorted functions
- **gui_components/** - Separate GUI components
    - **simulator_comp.py** - Simulator state display component
    - **editor_comp.py** - Text editor component
    - **console_comp.py** - Message console component
    - **settings_comp.py** - Settings display components
    - **about_dialog.py** - Custom about dialog
    - **symbol_table_comp.py** - A symbol table / debugger component
- **config/** - Various definition files and app settings
- **resources/** - Styles and images, *perhaps a stylesheet for every component?*
    - **default.css** - Default stylesheet

## Active task list
- TODO: What's with exceptions?

## Ideas list
- ALL buttons state change function
- Breakpoints and pause/stop state inside simulator, no separate state kept in view
- Custom exceptions, better error messages

- **UI**:
    - Place Editor/Simulator tabs into the header bar
    - Use GtkInfoBar somewhere, instead of console perhaps?

## Most important files

### Application.py
...

### Simulator.py
...

### Assembler.py
...

### Binary.py
...

### SimulatorComp.py
...

### EditorComp.py
...

### ConsoleComp.py
...

###SettingsComp.py
...

### AboutDialog.py
...
