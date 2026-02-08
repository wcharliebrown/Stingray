#!/bin/bash
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
