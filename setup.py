#!/usr/bin/env python3
"""
Setup script for Markdown Editor macOS app
"""

from setuptools import setup

APP = ['markdown_editor.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,  # Avoid Tk console/menu crashes on recent macOS builds
    'plist': {
        'CFBundleName': 'Markdown Editor',
        'CFBundleDisplayName': 'Markdown Editor',
        'CFBundleGetInfoString': 'A simple markdown editor with live preview',
        'CFBundleIdentifier': 'com.markdown.editor',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright 2024',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
        'NSRequiresAquaSystemAppearance': False,
        'LSUIElement': False,
        'NSPrincipalClass': 'NSApplication',
        'LSEnvironment': {
            'TK_SILENCE_DEPRECATION': '1',
            'TK_MAC_USE_APP_MAIN_MENU': '0',
        },
    },
    'frameworks': [
        '/opt/homebrew/anaconda3/pkgs/libffi-3.4.4-hca03da5_1/lib/libffi.8.dylib',
        '/opt/homebrew/anaconda3/lib/libtk8.6.dylib',
        '/opt/homebrew/anaconda3/lib/libtcl8.6.dylib',
    ],
    'packages': ['tkinter'],
    'includes': ['tkinter.ttk', 'tkinter.scrolledtext', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.font'],
    'excludes': ['matplotlib', 'numpy', 'scipy', 'pandas', 'PIL', 'cv2', 'setuptools', 'pkg_resources', 'wheel'],
    'optimize': 2,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
