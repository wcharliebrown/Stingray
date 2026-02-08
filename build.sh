#!/bin/bash
# Simple build script for Markdown Editor macOS App
# This script provides a one-command build experience

set -e  # Exit on any error

echo "🚀 Markdown Editor macOS App Builder"
echo "====================================="
echo

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script is designed for macOS only"
    exit 1
fi

# Check for Python 3.12 (preferred) or Python 3
PYTHON312=""
if command -v python3.12 &> /dev/null; then
    PYTHON312="python3.12"
    echo "✅ macOS detected"
    echo "✅ Python 3.12 found: $(python3.12 --version)"
elif command -v python312 &> /dev/null; then
    PYTHON312="python312"
    echo "✅ macOS detected"
    echo "✅ Python 3.12 found: $(python312 --version)"
elif command -v python3 &> /dev/null; then
    PYTHON312="python3"
    VERSION=$(python3 --version)
    echo "✅ macOS detected"
    echo "⚠️  Python 3.12 not found, using: $VERSION"
    echo "   Note: Python 3.12 is recommended to avoid Tkinter menu bar crashes"
else
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi
echo

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if we should use make or python script
if command_exists make; then
    echo "🔧 Using Make build system..."
    echo
    
    # Check system requirements
    make check
    
    echo
    echo "📦 Building the app..."
    make build
    
    echo
    echo "🎉 Build completed successfully!"
    echo
    echo "📋 Available next steps:"
    echo "   • Install to Applications: make install"
    echo "   • Create DMG installer: make dmg"
    echo "   • Test the app: make test"
    echo "   • Run directly: make run"
    echo "   • Clean build artifacts: make clean"
    echo
    echo "📁 App location: ./dist/Markdown Editor.app"
    
else
    echo "🔧 Using Python build script..."
    echo
    
    # Run the Python build script
    python3 build_macos_app.py
    
    if [ $? -eq 0 ]; then
        echo
        echo "🎉 Build completed successfully!"
        echo
        echo "📋 Available next steps:"
        echo "   • Install to Applications: ./install.sh"
        echo "   • Create DMG installer: ./create_dmg.sh"
        echo "   • Run the app: open './dist/Markdown Editor.app'"
        echo
        echo "📁 App location: ./dist/Markdown Editor.app"
    else
        echo
        echo "❌ Build failed!"
        exit 1
    fi
fi

echo
echo "✨ Happy coding!" 