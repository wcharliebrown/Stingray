#!/usr/bin/env python3
"""
Build script for packaging the Markdown Editor as a macOS app
Uses py2app to create a standalone macOS application bundle
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies(python_exe=None):
    """Check if required dependencies are installed"""
    if python_exe is None:
        python_exe = sys.executable
    
    required_packages = ['py2app']
    missing_packages = []
    
    # Check if packages are installed for the specified Python
    for package in required_packages:
        try:
            result = subprocess.run([python_exe, '-c', f'import {package}'],
                                  capture_output=True,
                                  timeout=5)
            if result.returncode != 0:
                missing_packages.append(package)
        except:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print(f"Installing missing packages for {python_exe}...")
        # Also ensure setuptools is installed
        packages_to_install = missing_packages + ['setuptools']
        for package in packages_to_install:
            # Try with --user and --break-system-packages first (for Homebrew Python)
            try:
                subprocess.check_call([python_exe, '-m', 'pip', 'install', '--user', '--break-system-packages', package])
            except subprocess.CalledProcessError:
                # Fall back to --user only
                try:
                    subprocess.check_call([python_exe, '-m', 'pip', 'install', '--user', package])
                except subprocess.CalledProcessError:
                    # Last resort: try without flags
                    subprocess.check_call([python_exe, '-m', 'pip', 'install', package])
        print("Dependencies installed successfully!")

def find_libffi():
    """Find libffi.8.dylib — required by _ctypes but not auto-bundled by py2app"""
    candidates = [
        '/opt/homebrew/opt/libffi/lib/libffi.8.dylib',  # Apple Silicon Homebrew
        '/usr/local/opt/libffi/lib/libffi.8.dylib',      # Intel Homebrew
        '/opt/homebrew/lib/libffi.8.dylib',
        '/usr/local/lib/libffi.8.dylib',
    ]
    for path in candidates:
        if os.path.exists(path):
            print(f"Found libffi: {path}")
            return path
    # Fallback: ask the system
    try:
        result = subprocess.run(
            ['find', '/opt/homebrew', '/usr/local', '-name', 'libffi.8.dylib', '-maxdepth', '6'],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.strip().splitlines():
            if line and os.path.exists(line):
                print(f"Found libffi: {line}")
                return line
    except Exception:
        pass
    print("Warning: libffi.8.dylib not found — the built app may fail to launch")
    return None


def find_tcltk(python_exe=None):
    """Find libtk8.6.dylib and libtcl8.6.dylib — required by _tkinter but not auto-bundled by py2app"""
    if python_exe is None:
        python_exe = sys.executable

    # Try to find where _tkinter lives and look in its parent lib dir first
    candidates_tk = []
    candidates_tcl = []
    try:
        result = subprocess.run(
            [python_exe, '-c', 'import _tkinter; print(_tkinter.__file__)'],
            capture_output=True, text=True, timeout=5
        )
        tkinter_path = result.stdout.strip()
        if tkinter_path:
            # lib-dynload/../.. → env lib dir
            lib_dir = os.path.dirname(os.path.dirname(tkinter_path))
            candidates_tk.append(os.path.join(lib_dir, 'libtk8.6.dylib'))
            candidates_tcl.append(os.path.join(lib_dir, 'libtcl8.6.dylib'))
    except Exception:
        pass

    candidates_tk += [
        '/opt/homebrew/anaconda3/lib/libtk8.6.dylib',
        '/opt/homebrew/opt/tcl-tk/lib/libtk8.6.dylib',
        '/usr/local/opt/tcl-tk/lib/libtk8.6.dylib',
        '/opt/homebrew/lib/libtk8.6.dylib',
        '/usr/local/lib/libtk8.6.dylib',
    ]
    candidates_tcl += [
        '/opt/homebrew/anaconda3/lib/libtcl8.6.dylib',
        '/opt/homebrew/opt/tcl-tk/lib/libtcl8.6.dylib',
        '/usr/local/opt/tcl-tk/lib/libtcl8.6.dylib',
        '/opt/homebrew/lib/libtcl8.6.dylib',
        '/usr/local/lib/libtcl8.6.dylib',
    ]

    libtk = next((p for p in candidates_tk if os.path.exists(p)), None)
    libtcl = next((p for p in candidates_tcl if os.path.exists(p)), None)

    if libtk:
        print(f"Found libtk: {libtk}")
    else:
        print("Warning: libtk8.6.dylib not found — the built app may fail to launch")
    if libtcl:
        print(f"Found libtcl: {libtcl}")
    else:
        print("Warning: libtcl8.6.dylib not found — the built app may fail to launch")

    return libtk, libtcl


def create_setup_py():
    """Create setup.py file for py2app"""
    libffi_path = find_libffi()
    libtk_path, libtcl_path = find_tcltk()
    frameworks = [p for p in [libffi_path, libtk_path, libtcl_path] if p]
    if frameworks:
        items = ',\n        '.join(repr(p) for p in frameworks)
        frameworks_line = f"    'frameworks': [\n        {items},\n    ],"
    else:
        frameworks_line = "    # 'frameworks': [],  # Required libs not found — install via: brew install libffi tcl-tk"

    setup_content = f'''#!/usr/bin/env python3
"""
Setup script for Markdown Editor macOS app
"""

from setuptools import setup

APP = ['markdown_editor.py']
DATA_FILES = []
OPTIONS = {{
    'argv_emulation': False,  # Avoid Tk console/menu crashes on recent macOS builds
    'plist': {{
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
        'LSEnvironment': {{
            'TK_SILENCE_DEPRECATION': '1',
            'TK_MAC_USE_APP_MAIN_MENU': '0',
        }},
    }},
{frameworks_line}
    'packages': ['tkinter'],
    'includes': ['tkinter.ttk', 'tkinter.scrolledtext', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.font'],
    'excludes': ['matplotlib', 'numpy', 'scipy', 'pandas', 'PIL', 'cv2', 'setuptools', 'pkg_resources', 'wheel'],
    'optimize': 2,
}}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={{'py2app': OPTIONS}},
    setup_requires=['py2app'],
)
'''

    with open('setup.py', 'w') as f:
        f.write(setup_content)
    print("Created setup.py")

def create_app_icon():
    """Create a simple app icon (optional)"""
    # This is a placeholder - you can replace this with your own icon creation
    # or download/create a proper .icns file
    print("Note: You can add an app_icon.icns file to customize the app icon")

def clean_build():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}/")

def find_python312():
    """Find Python 3.12 executable"""
    # Try common locations for Python 3.12
    python_commands = ['python3.12', 'python312', 'python3']
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if '3.12' in result.stdout or '3.12' in result.stderr:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    # If Python 3.12 not found, check current Python version
    try:
        result = subprocess.run([sys.executable, '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        version = result.stdout.strip() or result.stderr.strip()
        if '3.12' in version:
            return sys.executable
    except:
        pass
    
    return None

def build_app(python_exe=None):
    """Build the macOS app"""
    print("Building macOS app...")
    
    if python_exe is None:
        # Find Python 3.12
        python_exe = find_python312()
        if not python_exe:
            print("Warning: Python 3.12 not found. Trying to use current Python...")
            print(f"Current Python: {sys.executable}")
            python_exe = sys.executable
    
    print(f"Using Python: {python_exe}")
    
    # Clean previous builds
    clean_build()
    
    # Run py2app with Python 3.12
    try:
        subprocess.check_call([python_exe, 'setup.py', 'py2app'])
        print("App built successfully!")
        
        # Check if app was created
        app_path = Path('dist/Markdown Editor.app')
        if app_path.exists():
            print(f"App created at: {app_path.absolute()}")
            return True
        else:
            print("Error: App was not created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Error building app: {e}")
        return False

def create_installer_script():
    """Create a script to install the app to Applications folder"""
    installer_content = '''#!/bin/bash
# Install script for Markdown Editor

APP_NAME="Markdown Editor.app"
SOURCE_PATH="./dist/$APP_NAME"
TARGET_PATH="/Applications/$APP_NAME"

echo "Installing Markdown Editor..."

if [ ! -d "$SOURCE_PATH" ]; then
    echo "Error: App not found at $SOURCE_PATH"
    echo "Please run the build script first: python3 build_macos_app.py"
    exit 1
fi

# Remove existing installation if it exists
if [ -d "$TARGET_PATH" ]; then
    echo "Removing existing installation..."
    rm -rf "$TARGET_PATH"
fi

# Copy to Applications
echo "Installing to Applications folder..."
cp -R "$SOURCE_PATH" "$TARGET_PATH"

if [ $? -eq 0 ]; then
    echo "Installation successful!"
    echo "You can now find Markdown Editor in your Applications folder"
    echo "You can also launch it from Spotlight (Cmd+Space, then type 'Markdown Editor')"
else
    echo "Installation failed!"
    exit 1
fi
'''
    
    with open('install.sh', 'w') as f:
        f.write(installer_content)
    
    # Make it executable
    os.chmod('install.sh', 0o755)
    print("Created install.sh script")

def create_dmg_script():
    """Create a script to create a DMG installer"""
    dmg_script = '''#!/bin/bash
# Create DMG installer script

APP_NAME="Markdown Editor.app"
DMG_NAME="Markdown_Editor_Installer.dmg"
VOLUME_NAME="Markdown Editor Installer"

echo "Creating DMG installer..."

# Check if app exists
if [ ! -d "./dist/$APP_NAME" ]; then
    echo "Error: App not found. Please run the build script first."
    exit 1
fi

# Create temporary directory for DMG contents
TEMP_DIR=$(mktemp -d)
mkdir -p "$TEMP_DIR"

# Copy app to temp directory
cp -R "./dist/$APP_NAME" "$TEMP_DIR/"

# Create Applications folder symlink
ln -s /Applications "$TEMP_DIR/Applications"

# Create DMG
hdiutil create -volname "$VOLUME_NAME" -srcfolder "$TEMP_DIR" -ov -format UDZO "$DMG_NAME"

# Clean up
rm -rf "$TEMP_DIR"

if [ $? -eq 0 ]; then
    echo "DMG created successfully: $DMG_NAME"
else
    echo "Error creating DMG"
    exit 1
fi
'''
    
    with open('create_dmg.sh', 'w') as f:
        f.write(dmg_script)
    
    # Make it executable
    os.chmod('create_dmg.sh', 0o755)
    print("Created create_dmg.sh script")

def main():
    """Main build process"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--setup-only':
            print("Creating setup.py...")
            create_setup_py()
            return
        elif sys.argv[1] == '--dmg-only':
            print("Creating DMG script...")
            create_dmg_script()
            return
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("Usage: python3 build_macos_app.py [OPTION]")
            print("Options:")
            print("  --setup-only    Only create setup.py file")
            print("  --dmg-only      Only create DMG script")
            print("  --help, -h      Show this help message")
            return
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
            sys.exit(1)
    
    print("=== Markdown Editor macOS App Builder ===")
    print()
    
    # Check if we're on macOS
    if sys.platform != 'darwin':
        print("Error: This script is designed for macOS only")
        sys.exit(1)
    
    # Find Python 3.12
    print("1. Finding Python 3.12...")
    python312 = find_python312()
    if not python312:
        print("Warning: Python 3.12 not found. Trying to use current Python...")
        print(f"Current Python: {sys.executable}")
        python312 = sys.executable
    else:
        print(f"Found Python 3.12: {python312}")
        # Verify version
        try:
            result = subprocess.run([python312, '--version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            print(f"Python version: {result.stdout.strip() or result.stderr.strip()}")
        except:
            pass
    print()
    
    # Check dependencies
    print("2. Checking dependencies...")
    check_dependencies(python312)
    print()
    
    # Create setup.py
    print("3. Creating setup.py...")
    create_setup_py()
    print()
    
    # Create app icon placeholder
    print("4. Setting up app icon...")
    create_app_icon()
    print()
    
    # Build the app
    print("5. Building the app...")
    if build_app(python312):
        print()
        
        # Create installer script
        print("5. Creating installer script...")
        create_installer_script()
        print()
        
        # Create DMG script
        print("6. Creating DMG script...")
        create_dmg_script()
        print()
        
        print("=== Build Complete! ===")
        print()
        print("Next steps:")
        print("1. To install the app: ./install.sh")
        print("2. To create a DMG installer: ./create_dmg.sh")
        print("3. The app is located at: ./dist/Markdown Editor.app")
        print()
        print("You can also run the app directly from the dist folder:")
        print("open './dist/Markdown Editor.app'")
        
    else:
        print("Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
