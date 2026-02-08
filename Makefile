# Makefile for Markdown Editor macOS App
# This Makefile provides an alternative to the Python build script

.PHONY: help build clean install dmg test run

# Default target
help:
	@echo "Markdown Editor macOS App Builder"
	@echo ""
	@echo "Available targets:"
	@echo "  build    - Build the macOS app (requires py2app)"
	@echo "  clean    - Clean build artifacts"
	@echo "  install  - Install app to Applications folder"
	@echo "  dmg      - Create DMG installer"
	@echo "  test     - Test the built app"
	@echo "  run      - Run the Python script directly"
	@echo "  deps     - Install required dependencies"
	@echo "  all      - Build, install, and create DMG"

# Find Python 3.12
PYTHON312 := $(shell which python3.12 2>/dev/null || which python312 2>/dev/null || echo python3)

# Install dependencies
deps:
	@echo "Installing required dependencies..."
	@echo "Using Python: $(PYTHON312)"
	@$(PYTHON312) -m pip install --user --break-system-packages py2app setuptools || \
	 $(PYTHON312) -m pip install --user py2app setuptools || \
	 $(PYTHON312) -m pip install py2app setuptools
	@echo "Dependencies installed!"

# Build the app
build:
	@echo "Building macOS app..."
	@echo "Using Python: $(PYTHON312)"
	@if [ ! -f "setup.py" ]; then \
		echo "Creating setup.py..."; \
		$(PYTHON312) build_macos_app.py --setup-only; \
	fi
	$(PYTHON312) setup.py py2app
	@echo "App built successfully at dist/Markdown Editor.app"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -f install.sh
	rm -f create_dmg.sh
	@echo "Clean complete!"

# Install to Applications folder
install: build
	@echo "Installing to Applications folder..."
	@if [ -d "/Applications/Markdown Editor.app" ]; then \
		echo "Removing existing installation..."; \
		rm -rf "/Applications/Markdown Editor.app"; \
	fi
	cp -R "dist/Markdown Editor.app" "/Applications/"
	@echo "Installation complete! You can find the app in Applications folder."

# Create DMG installer
dmg: build
	@echo "Creating DMG installer..."
	@if [ ! -f "create_dmg.sh" ]; then \
		echo "Creating DMG script..."; \
		python3 build_macos_app.py --dmg-only; \
	fi
	./create_dmg.sh
	@echo "DMG created: Markdown_Editor_Installer.dmg"

# Test the built app
test: build
	@echo "Testing the built app..."
	@if [ -d "dist/Markdown Editor.app" ]; then \
		echo "Launching app for testing..."; \
		open "dist/Markdown Editor.app"; \
	else \
		echo "Error: App not found. Run 'make build' first."; \
		exit 1; \
	fi

# Run the Python script directly
run:
	@echo "Running Markdown Editor directly..."
	@echo "Using Python: $(PYTHON312)"
	$(PYTHON312) markdown_editor.py

# Build everything
all: build install dmg
	@echo "Complete build process finished!"
	@echo "App installed to Applications folder"
	@echo "DMG installer created: Markdown_Editor_Installer.dmg"

# Development target - run with auto-reload (requires watchdog)
dev:
	@echo "Starting development mode..."
	@if ! python3 -c "import watchdog" 2>/dev/null; then \
		echo "Installing watchdog for development mode..."; \
		python3 -m pip install watchdog; \
	fi
	@echo "Starting auto-reload development server..."
	@echo "Press Ctrl+C to stop"
	@python3 -c "import time, subprocess; \
		while True: \
			try: \
				subprocess.run(['python3', 'markdown_editor.py'], check=True); \
			except KeyboardInterrupt: \
				break; \
			except: \
				time.sleep(1); \
				continue"

# Quick build (development version)
quick: deps
	@echo "Quick build (development version)..."
	python3 setup.py py2app -A
	@echo "Development app built at dist/Markdown Editor.app"

# Check system requirements
check:
	@echo "Checking system requirements..."
	@if [ "$$(uname)" != "Darwin" ]; then \
		echo "Error: This build system is designed for macOS only"; \
		exit 1; \
	fi
	@echo "✓ macOS detected"
	@python3 --version
	@echo "✓ Python available"
	@echo "System requirements met!"

# Show app info
info: build
	@echo "App Information:"
	@echo "Location: dist/Markdown Editor.app"
	@echo "Size: $$(du -sh dist/Markdown\ Editor.app | cut -f1)"
	@echo "Bundle ID: com.markdown.editor"
	@echo "Version: 1.0.0" 