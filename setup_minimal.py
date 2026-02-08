#!/usr/bin/env python3
from setuptools import setup
setup(
    app=['markdown_editor.py'],
    options={'py2app': {
        'argv_emulation': False,
        'includes': ['tkinter', '_tkinter'],
        'frameworks': [
            '/opt/homebrew/opt/tcl-tk/lib/libtcl9.0.dylib',
            '/opt/homebrew/opt/tcl-tk/lib/libtcl9tk9.0.dylib'
        ],
    }},
    setup_requires=['py2app'],
)
