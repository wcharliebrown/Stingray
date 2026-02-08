#!/bin/bash
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
