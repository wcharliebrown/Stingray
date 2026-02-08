# Markdown Editor

## A simple markdown editor built in Python with no external dependencies. The editor provides real-time formatting as you type, making it easy to see how your markdown will look while you're writing.

## Features

- **No Dependencies**: Uses only Python's built-in `tkinter` library
- **Real-time Formatting**: See formatting changes as you type
- **Supported Markdown Styles**:
  - Headers (H1-H6): `#`, `##`, `###`, `####`, `#####`, `######`
  - Bold text: `**bold text**`
  - Italic text: `*italic text*`

## Installation

No installation required! Just make sure you have Python 3.x installed on your system.

## Usage

1. Run the editor:
   ```bash
   python markdown_editor.py
   ```

2. Start typing markdown in the editor window
3. See formatting applied in real-time

## Supported Markdown Syntax

### Headers
```
# H1 Header
## H2 Header
### H3 Header
#### H4 Header
##### H5 Header
###### H6 Header
```

### Text Formatting
```
**This text will be bold**
*This text will be italic*
```

## How It Works

The editor uses Python's `tkinter` library to create a GUI with a text widget. As you type, the application:

1. Monitors text changes
2. Parses the content for markdown patterns
3. Applies appropriate styling tags to the text
4. Updates the display in real-time

## Visual Styling

- **H1-H6 Headers**: Different sizes and shades of blue
- **Bold Text**: Bold black text
- **Italic Text**: Italic gray text
- **Clean Interface**: Modern, readable design

## Requirements

- Python 3.x
- tkinter (included with Python)

## License

This project is open source and available under the MIT License. 
