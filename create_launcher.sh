#!/bin/bash
# Create a launcher script for the Markdown Editor app
# This script sets environment variables before launching the app

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="$SCRIPT_DIR/dist/Markdown Editor.app"

# Set environment variables to prevent Tkinter console window issues
export TK_SILENCE_DEPRECATION=1
export TK_MAC_USE_APP_MAIN_MENU=0

# Launch the app
open "$APP_PATH"
