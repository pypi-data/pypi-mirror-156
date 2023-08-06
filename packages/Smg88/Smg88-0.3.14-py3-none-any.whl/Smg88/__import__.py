"""This file is used to manage which files can be imported.

If their is any static reference to any part of the Smg88 package (standalone file or full set of files), this file should be it

All files in Smg88 module is designed to be runnable in a standalone fashion, this file manages which files could be imported and which not to determine dynamic dependencies
"""

from types import ModuleType


print("Somebody ran __import__.py! Yay!")

__expand = True

if __name__ == "__main__":
    print("__import__.py is being run directly! Oh ooooh!")
    __expand = False

if __expand:
    __location__ = __file__

    ModuleType
