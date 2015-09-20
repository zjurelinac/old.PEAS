# PEAS
** Python Extendable Assembler and Simulator **

## Idea
...

## Project structure
- **Application.py** - Main module, puts everything together
- **simulators/**
    - **Simulator.py** - Abstract base class for simulators
    - **FriscSimulator.py** - FRISC processor simulator
- **assemblers/**
    - **Assembler.py** - Abstract base class for assemblers
    - **FriscAssembler.py** - FRISC processor assembler
- **utils/** - Utility functions and classes
    - **Binary.py** - Implements binary arithmetic and display functions
    - **Helpers.py** - Other, unsorted functions
- **gui_components/** - Separate GUI components
    - **SimulatorComp.py** - Simulator state display component
    - **EditorComp.py** - Text editor component
    - **ConsoleComp.py** - Message console component
    - **SettingsComp.py** - Settings display components
- **config/** - Various definition files and app settings
- **resources/** - Styles and images, *perhaps a stylesheet for every component?*
    - **default.css** - Default stylesheet
