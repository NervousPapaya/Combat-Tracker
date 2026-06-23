# Combat Tracker

This program is intended to be used as a combat tracker for tabletop RPGs. 

## Description

The program allows one to track "combatants" in a table layout. Each combatants Initiative, AC, damage taken and HP total can be tracked.
You can add abilities or spells as checkboxes to each combatant once they have been added to the tracker. 
There is a "status" field intended for any free-text tracking not covered by the program.
Furthermore, the program can track conditions and the like on a round to round basis. 

Encounters can be saved and loaded. At present, they are saved in JSON format.

## Getting Started

### Dependencies
The program has been tested only on Windows, but should run on any OS. If you run the exe, you don't need anything else.

If running from a script, you need
* Python 3.13+ (the program might work on earlier, but has been developed using this version)
* Pyside 6


### Installing

You can grab any older versions from old_exe. These are .exe files that can be run directly.

If you wish to run from the script, do the following:
* Download the repo (or more specifically /commands, /filehandling, /models, /services, /ui and main.py)

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

Contributors names and contact info:

 [@NervousPapaya](https://github.com/NervousPapaya)

## Version History

* 0.2
    * Undo/redo
    * Condition functionality
    * Round counter
* 0.1
    * Basic table functionality
    * save/load
    * tracking abilities



## License

This project is licensed for non-commercial use only.
You may not use this software or derivatives for commercial purposes without explicit permission from the author.

<!--
## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)

-->
