"""Build a python script for the storyliner distribution.
        
In order to distribute a single script without dependencies, 
this script "inlines" all modules imported from the novxlib package.

The novxlib project (see see https://github.com/peter88213/novxlib)
must be located on the same directory level as the storyliner project. 

For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import sys
sys.path.insert(0, f'{os.getcwd()}/../../novxlib/src')
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE = f'{SRC}storyliner_.py'
TARGET_FILE = f'{BUILD}storyliner.py'

os.makedirs(BUILD, exist_ok=True)


def main():
    inliner.run(SOURCE_FILE, TARGET_FILE, 'storylinerlib', '../src/')
    inliner.run(TARGET_FILE, TARGET_FILE, 'novxlib', '../../novxlib/src/')
    print('Done.')


if __name__ == '__main__':
    main()
