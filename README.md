# Project Title

This program is intended to be used as a combat tracker for tabletop RPGs. 

## Description

The program allows one to track "combatants" in a table layout. Each combatants Initiative, AC, damage taken and HP total can be tracked.
You can add abilities or spells as checkboxes to each combatant once they have been added to the tracker. 
There is a "status" field intended for any free-text tracking not covered by the program.
Furthermore, the program can track conditions and the like on a round to round basis. 

Encounters can be saved and loaded. At present, they are saved in JSON format.

## Technical Overview
The application is separated into UI, business logic, and data:

* **Entry point** (`main.py`): A minimal entry point that invokes `run_app()` in the UI layer to start the application.
* **UI layer** (`ui/`): `main_window.py` orchestrates the interface, with `table_mapper.py` handling the core combatant table and `abilitywidget.py` managing ability-specific widget behavior.
* **Data layer** (`combatant/`): Combatants are represented as dataclasses (`combatant.py`), keeping combat state explicit and type-safe.
* **Domain/service layer** (`models/`, `services/`): `combat_manager.py` (in `models/`) owns the combat state and logic, decoupled from the UI. Undo/redo is implemented via the command pattern in `services/command_manager.py`, with individual reversible actions defined in `commands/commands.py`.

## Getting Started

### Dependencies
The program has been tested only on Windows, but should run on any OS. If you run the exe, you don't need anything else.

If running from a script, you need
* Python 3.13+ (the program might work on earlier, but has been developed using this version)
* Pyside 6


### Installing

You can grab any older versions from old_exe. These are .exe files that can be run directly.

If you wish to run from the script, do the following:
* Download the repo (or more specifically `commands/`, `filehandling/`, `models/`, `/services`, `ui/` and `main.py`)

### Executing program

To run the program either run the exe, or run main.py in an IDE or console.
```
\main.py
```

The program should open.

<!--
## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```
-->

## Authors

Solo project, developed and maintained by [@NervousPapaya](https://github.com/NervousPapaya)

## Version History

* 0.2
    * Undo/redo
    * Condition functionality
    * Round counter
* 0.1
    * Basic table functionality
    * save/load
    * tracking abilities

## Known Bugs 
A limited list of known bugs:
* Clicking "Next Round" advances the round counter by 2 instead of 1; pressing undo once corrects it.
* HP edits require two undo actions to fully revert.

## License

This project is licensed for non-commercial use only.
You may not use this software or derivatives for commercial purposes without explicit permission from the author.

Feel free to otherwise browse, run, and evaluate the code, whether for your personal curiosity/use or as part of a technical review or hiring process.

<!--
## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)

-->