 
Nerve is a web-based integration framework with a similar MVC architecture to CodeIgniter, but implemented in python3.  It's primarily used as a home automation server and media player/media library.  Nerve has a modular structure, which makes it easy to extend and customize, and a generic widgets and devices system which makes it easier to tie together different hardware devices, sensors, and internet information sources into one place (or across distributed servers).

## Installation

Unpack the source code where ever is most convenient.  Check out dependencies.txt for a list of the Debian packages required for various features.  Most Debian/Ubuntu based distros will likely have the same package names.  The code has been run in Windows 7, with python and the necessary python libraries installed manually, although I no longer test the code on Windows.

To run the code, while in the source directory, use the command:
```
python3 nerve.py
```

The default configuration directory is ~/.nerve, however it can be set on the command line:
```
python3 nerve.py -c config/panther
```
The configuration for a particular instance is stored entirely in the configuration directory.  Different instances can be run on the same computer by simply specifying a different configuration directory to use.

## Configuration

To configure an instance of nerve, you might want to start with one of the example configurations included in the config/ directory of the source code.  The settings.json file is the main config file.  It describes the structure of the internal object file system thing.

At the heart of each instance is a filesystem-like heirarchy of objects, referenced by a path.  The three top level 'directories' are '/modules', '/devices', and '/servers'.  

