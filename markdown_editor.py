#!/usr/bin/env python3
"""
Markdown Editor with Dynamic Rendering and File Browser
A simple markdown editor that renders formatting in real-time as you type.
Supports: H1-H6 headers, bold, and italics.
Features: File browser sidebar for easy file navigation.
"""

import os
import sys
import traceback
import time

# Prevent Tkinter from creating console window and default menu bar on macOS
os.environ['TK_SILENCE_DEPRECATION'] = '1'
# Try to prevent Tkinter from creating default menu items with nil titles
os.environ['TK_MAC_USE_APP_MAIN_MENU'] = '0'

# Setup early logging to home directory (definitely writable)
DEBUG_LOG = os.path.expanduser("~/.markdown_editor_debug.log")
def log_debug(message):
    try:
        with open(DEBUG_LOG, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
            f.flush()
    except:
        pass

# Now import tkinter after environment is set up
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, filedialog, messagebox
except Exception as e:
    log_debug(f"Failed to import tkinter: {e}")
    sys.exit(1)
import re
from typing import List, Tuple
from pathlib import Path
import threading
import time
import json
from tkinter import font


class SettingsDialog:
    def __init__(self, parent, editor):
        self.parent = parent
        self.editor = editor
        self.settings = editor.settings
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Editor Settings", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Default Directory Section
        dir_frame = ttk.LabelFrame(main_frame, text="Default Directory", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.dir_var = tk.StringVar(value=self.settings.get('default_directory', os.path.expanduser("~")))
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=50)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        dir_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        dir_btn.pack(side=tk.RIGHT)
        
        # Font Settings Section
        font_frame = ttk.LabelFrame(main_frame, text="Font Settings", padding="10")
        font_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Font Family
        font_family_frame = ttk.Frame(font_frame)
        font_family_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(font_family_frame, text="Font Family:").pack(side=tk.LEFT)
        
        self.font_family_var = tk.StringVar(value=self.settings.get('font_family', 'Arial'))
        self.font_family_combo = ttk.Combobox(font_family_frame, textvariable=self.font_family_var, width=30)
        self.font_family_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Get available fonts
        available_fonts = self.get_available_fonts()
        self.font_family_combo['values'] = available_fonts
        
        # Font Size
        font_size_frame = ttk.Frame(font_frame)
        font_size_frame.pack(fill=tk.X)
        
        ttk.Label(font_size_frame, text="Font Size:").pack(side=tk.LEFT)
        
        self.font_size_var = tk.StringVar(value=str(self.settings.get('font_size', 12)))
        font_size_spinbox = ttk.Spinbox(font_size_frame, from_=8, to=72, textvariable=self.font_size_var, width=10)
        font_size_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Apply", command=self.apply_settings).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_to_defaults).pack(side=tk.LEFT)
        
        # Bind events
        self.dialog.protocol("WM_DELETE_WINDOW", self.dialog.destroy)
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy)
    
    def get_available_fonts(self):
        """Get list of available fonts on the system"""
        try:
            # Get all available font families
            font_families = list(font.families())
            # Sort alphabetically
            font_families.sort()
            return font_families
        except:
            # Fallback to common fonts if font.families() fails
            return ['Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana', 'Georgia', 'Palatino', 'Garamond', 'Bookman', 'Comic Sans MS', 'Trebuchet MS', 'Arial Black', 'Impact']
    
    def browse_directory(self):
        """Browse for default directory"""
        directory = filedialog.askdirectory(initialdir=self.dir_var.get())
        if directory:
            self.dir_var.set(directory)
    
    def apply_settings(self):
        """Apply the current settings"""
        try:
            # Validate font size
            font_size = int(self.font_size_var.get())
            if font_size < 8 or font_size > 72:
                messagebox.showerror("Error", "Font size must be between 8 and 72")
                return
            
            # Update settings
            self.settings['default_directory'] = self.dir_var.get()
            self.settings['font_family'] = self.font_family_var.get()
            self.settings['font_size'] = font_size
            
            # Save settings to file
            self.editor.save_settings()
            
            # Apply font changes to editor
            self.editor.apply_font_settings()
            
            # Update file browser default directory
            if hasattr(self.editor, 'file_browser'):
                self.editor.file_browser.current_path = self.settings['default_directory']
                self.editor.file_browser.load_directory()
            
            messagebox.showinfo("Success", "Settings applied successfully!")
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Font size must be a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Error applying settings: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset settings to default values"""
        self.dir_var.set(os.path.expanduser("~"))
        self.font_family_var.set("Arial")
        self.font_size_var.set("12")
    
    def center_dialog(self):
        """Center the dialog on the parent window"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")


class FileBrowser:
    def __init__(self, parent, editor):
        self.parent = parent
        self.editor = editor
        # Use default directory from settings if available
        default_dir = editor.settings.get('default_directory', os.getcwd()) if hasattr(editor, 'settings') else os.getcwd()
        self.current_path = default_dir
        self.sort_column = "name"  # Default sort column
        self.sort_reverse = False  # Default sort order
        
        # Create file browser frame
        self.frame = ttk.Frame(parent, width=300)  # Increased width for two columns
        self.frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        self.frame.pack_propagate(False)
        
        # Create title
        self.title_label = ttk.Label(self.frame, text="File Browser", font=("Arial", 12, "bold"))
        self.title_label.pack(pady=(0, 10))
        
        # Create search frame
        self.search_frame = ttk.Frame(self.frame)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search label
        ttk.Label(self.search_frame, text="Search:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Clear search button
        self.clear_search_btn = ttk.Button(self.search_frame, text="✕", width=3, command=self.clear_search)
        self.clear_search_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Bind search entry to filter function
        self.search_var.trace_add('write', lambda *args: self.filter_items())
        
        # Store all items data for filtering (not tree IDs, but raw data)
        self.all_items_data = []
        
        # Create navigation frame
        self.nav_frame = ttk.Frame(self.frame)
        self.nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Parent directory button
        self.parent_btn = ttk.Button(self.nav_frame, text="..", width=3, command=self.go_to_parent)
        self.parent_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Current path label
        self.path_label = ttk.Label(self.nav_frame, text="", font=("Arial", 9))
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create treeview for files and directories with two columns
        self.tree = ttk.Treeview(self.frame, show="tree headings", selectmode="browse", columns=("mod_time",))
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure columns
        self.tree.heading("#0", text="Name", command=lambda: self.sort_by_column("name"))
        self.tree.heading("mod_time", text="Modified", command=lambda: self.sort_by_column("mod_time"))
        self.tree.column("#0", width=180, anchor=tk.W)
        self.tree.column("mod_time", width=100, anchor=tk.W)
        
        # Add scrollbar to treeview
        self.tree_scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Return>", self.on_item_double_click)
        
        # Load initial directory
        self.load_directory()
    
    def focus_search(self):
        """Focus the search entry box"""
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)
    
    def sort_by_column(self, column):
        """Sort the treeview by the specified column"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Reload directory with new sort order
        self.load_directory()
    
    def format_modification_time(self, timestamp):
        """Format modification time for display"""
        import datetime
        mod_time = datetime.datetime.fromtimestamp(timestamp)
        now = datetime.datetime.now()
        
        # If modified today, show time only
        if mod_time.date() == now.date():
            return mod_time.strftime("%H:%M")
        # If modified this year, show month and day
        elif mod_time.year == now.year:
            return mod_time.strftime("%b %d")
        # Otherwise show year
        else:
            return mod_time.strftime("%Y")
    
    def go_to_parent(self):
        """Navigate to parent directory"""
        parent_path = os.path.dirname(self.current_path)
        if parent_path != self.current_path:
            self.current_path = parent_path
            self.load_directory()
    
    def load_directory(self):
        """Load and display the current directory contents"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Update path label
        self.path_label.config(text=os.path.basename(self.current_path) or self.current_path)
        
        try:
            # Get directory contents
            items = os.listdir(self.current_path)
            
            # Separate directories and files with their modification times
            directories = []
            files = []
            
            for item in items:
                item_path = os.path.join(self.current_path, item)
                try:
                    mod_time = os.path.getmtime(item_path)
                    if os.path.isdir(item_path):
                        directories.append((item, mod_time))
                    else:
                        files.append((item, mod_time))
                except (OSError, FileNotFoundError):
                    # Skip items we can't access
                    continue
            
            # Sort based on current sort column and order
            if self.sort_column == "name":
                directories.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse)
                files.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse)
            else:  # mod_time
                directories.sort(key=lambda x: x[1], reverse=self.sort_reverse)
                files.sort(key=lambda x: x[1], reverse=self.sort_reverse)
            
            # Store all items data for filtering
            self.all_items_data = []
            
            # Add directories first
            for directory, mod_time in directories:
                formatted_time = self.format_modification_time(mod_time)
                item_text = f"📁 {directory}"
                self.all_items_data.append({
                    'name': directory,
                    'text': item_text,
                    'mod_time': formatted_time,
                    'tags': ("directory",)
                })
            
            # Add files
            for file, mod_time in files:
                # Add file icon based on extension
                icon = "📄"
                if file.lower().endswith(('.md', '.markdown')):
                    icon = "📝"
                elif file.lower().endswith(('.txt')):
                    icon = "📄"
                elif file.lower().endswith(('.py')):
                    icon = "🐍"
                elif file.lower().endswith(('.html', '.htm')):
                    icon = "🌐"
                elif file.lower().endswith(('.css')):
                    icon = "🎨"
                elif file.lower().endswith(('.js')):
                    icon = "⚡"
                
                formatted_time = self.format_modification_time(mod_time)
                item_text = f"{icon} {file}"
                self.all_items_data.append({
                    'name': file,
                    'text': item_text,
                    'mod_time': formatted_time,
                    'tags': ("file",)
                })
            
            # Apply current search filter if any
            self.filter_items()
        
        except PermissionError:
            messagebox.showerror("Error", f"Permission denied accessing {self.current_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading directory: {str(e)}")
    
    def filter_items(self):
        """Filter treeview items based on search query"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_query = self.search_var.get().lower().strip()
        
        # If search is empty, show all items
        if not search_query:
            items_to_show = self.all_items_data
        else:
            # Filter items based on search query
            items_to_show = [item for item in self.all_items_data 
                           if search_query in item['name'].lower()]
        
        # Add filtered items to tree
        for item in items_to_show:
            self.tree.insert("", tk.END, text=item['text'], 
                           values=(item['mod_time'],), 
                           tags=item['tags'])
    
    def clear_search(self):
        """Clear the search entry"""
        self.search_var.set("")
        self.search_entry.focus()
    
    def on_item_double_click(self, event):
        """Handle double-click on tree item"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        # Extract filename from the tree column text (remove icon and space)
        item_text = item['text']
        item_name = item_text.split(' ', 1)[1] if ' ' in item_text else item_text
        item_tags = item['tags']
        
        if "directory" in item_tags:
            # Navigate into directory
            new_path = os.path.join(self.current_path, item_name)
            self.current_path = new_path
            self.load_directory()
        elif "file" in item_tags:
            # Open file in editor
            file_path = os.path.join(self.current_path, item_name)
            self.editor.open_file(file_path)


class MarkdownEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Editor with File Browser")
        self.root.geometry("1200x700")
        
        # Configure the main window
        self.root.configure(bg='#f0f0f0')
        
        # Load settings
        self.settings = self.load_settings()
        
        # Auto-save variables
        self.auto_save_timer = None
        self.auto_save_delay = 2000  # 2 seconds in milliseconds
        self.last_save_time = time.time()
        
        # Create menu bar
        self.create_menu()
        
        # Create main container
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create file browser
        self.file_browser = FileBrowser(self.main_container, self)
        
        # Bind Ctrl+Shift+F / Cmd+Shift+F to focus file browser search box
        self.root.bind('<Control-Shift-f>', lambda e: self.file_browser.focus_search())
        self.root.bind('<Control-Shift-F>', lambda e: self.file_browser.focus_search())
        self.root.bind('<Command-Shift-f>', lambda e: self.file_browser.focus_search())
        self.root.bind('<Command-Shift-F>', lambda e: self.file_browser.focus_search())
        
        # Create main frame for editor
        self.main_frame = ttk.Frame(self.main_container)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create title label
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Markdown Editor - Type to see live formatting",
            font=("Arial", 14, "bold")
        )
        self.title_label.pack(pady=(0, 10))

        # Editor search controls
        self.search_frame = ttk.Frame(self.main_frame)
        self.search_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(self.search_frame, text="Find:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 6))
        self.editor_search_var = tk.StringVar()
        self.editor_search_entry = ttk.Entry(self.search_frame, textvariable=self.editor_search_var, width=30)
        self.editor_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_prev_btn = ttk.Button(self.search_frame, text="Prev", width=6, command=self.find_previous_match)
        self.search_prev_btn.pack(side=tk.LEFT, padx=(6, 0))
        self.search_next_btn = ttk.Button(self.search_frame, text="Next", width=6, command=self.find_next_match)
        self.search_next_btn.pack(side=tk.LEFT, padx=(4, 0))
        self.search_clear_btn = ttk.Button(self.search_frame, text="Clear", width=6, command=self.clear_editor_search)
        self.search_clear_btn.pack(side=tk.LEFT, padx=(4, 0))

        self.editor_search_var.trace_add('write', lambda *args: self.refresh_editor_search())
        
        # Create text area with custom styling
        font_family = self.settings.get('font_family', 'Arial')
        font_size = self.settings.get('font_size', 12)
        
        self.text_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            font=(font_family, font_size),
            bg='white',
            fg='black',
            insertbackground='black',
            selectbackground='#0078d4',
            selectforeground='white',
            relief=tk.SUNKEN,
            borderwidth=2,
            undo=True,
            autoseparators=True,
            maxundo=-1
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different markdown styles
        self.setup_text_tags()
        
        # Bind events
        self.text_area.bind('<KeyRelease>', self.on_text_change)
        self.text_area.bind('<KeyPress>', self.on_key_press)
        self.text_area.bind('<Command-z>', self.handle_undo)
        self.text_area.bind('<Control-z>', self.handle_undo)
        self.text_area.bind('<Command-Shift-z>', self.handle_redo)
        self.text_area.bind('<Command-Shift-Z>', self.handle_redo)
        self.text_area.bind('<Control-Shift-z>', self.handle_redo)
        self.text_area.bind('<Control-Shift-Z>', self.handle_redo)

        # Bind Ctrl+F / Cmd+F to focus editor search
        self.root.bind('<Control-f>', lambda e: self.focus_editor_search())
        self.root.bind('<Command-f>', lambda e: self.focus_editor_search())
        self.editor_search_entry.bind('<Return>', lambda e: self.find_next_match())
        self.editor_search_entry.bind('<Shift-Return>', lambda e: self.find_previous_match())
        
        # Current file path
        self.current_file = None
        
        # Add some initial content
        self.insert_sample_content()
        
        # Apply initial formatting
        self.apply_markdown_formatting()

        # Search state
        self.search_matches = []
        self.search_match_index = -1
        self.last_search_query = ""
        self.text_area.tag_configure("search_match", background="#fde68a", foreground="black")
        
        # Start undo history from the initial content so Cmd+Z doesn't clear it
        self.reset_undo_stack()
        
        # Store original cursor blink settings
        self.cursor_blink_on_time = self.text_area.cget('insertontime')
        self.cursor_blink_off_time = self.text_area.cget('insertofftime')
        self.app_is_active = True  # Track application active state
        
        # Get our process ID for reliable app detection
        try:
            import os
            self.our_pid = os.getpid()
        except:
            self.our_pid = None
        
        # Bind focus events to control cursor blinking
        self.root.bind('<FocusOut>', self.on_window_focus_out)
        self.root.bind('<FocusIn>', self.on_window_focus_in)
        
        # Bind to window state changes (for minimization, etc.)
        self.root.bind('<Unmap>', lambda e: self.set_app_inactive())
        self.root.bind('<Map>', lambda e: self.set_app_active())
        
        # Set up periodic check for application-level activation (for Cmd-Tab switching)
        self.check_app_active()
    
    def create_menu(self):
        """Create the application menu bar"""
        # Always create a fresh menu bar
        # (The menu created in main() is just a placeholder to prevent crashes)
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file_dialog, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file_dialog())
    
    def load_settings(self):
        """Load settings from file"""
        settings_file = os.path.join(os.path.expanduser("~"), ".markdown_editor_settings.json")
        default_settings = {
            'default_directory': os.path.expanduser("~"),
            'font_family': 'Arial',
            'font_size': 12
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            else:
                return default_settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return default_settings
    
    def save_settings(self):
        """Save settings to file"""
        settings_file = os.path.join(os.path.expanduser("~"), ".markdown_editor_settings.json")
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def open_settings(self):
        """Open the settings dialog"""
        SettingsDialog(self.root, self)
    
    def apply_font_settings(self):
        """Apply font settings to the text area and tags"""
        font_family = self.settings.get('font_family', 'Arial')
        font_size = self.settings.get('font_size', 12)
        
        # Update text area font
        self.text_area.configure(font=(font_family, font_size))
        
        # Update text tags with new font
        self.setup_text_tags()
        
        # Reapply formatting
        self.apply_markdown_formatting()
    
    def new_file(self):
        """Create a new file"""
        # Cancel any pending auto-save timer
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
            self.auto_save_timer = None
        
        # Clear current content
        self.text_area.delete("1.0", tk.END)
        self.reset_undo_stack()
        
        # Reset current file
        self.current_file = None
        
        # Update title
        self.title_label.config(text="Markdown Editor - New File")
        
        # Update status bar
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text="New file created")
    
    def open_file_dialog(self):
        """Open file dialog to select a file"""
        file_path = filedialog.askopenfilename(
            title="Open Markdown File",
            filetypes=[
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ],
            initialdir=self.settings.get('default_directory', os.path.expanduser("~"))
        )
        
        if file_path:
            self.open_file(file_path)
    
    def open_file(self, file_path):
        """Open a file in the editor"""
        try:
            # Cancel any pending auto-save timer
            if self.auto_save_timer:
                self.root.after_cancel(self.auto_save_timer)
                self.auto_save_timer = None
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Clear current content
            self.text_area.delete("1.0", tk.END)
            
            # Insert file content
            self.text_area.insert("1.0", content)
            
            # Update current file
            self.current_file = file_path
            
            # Update title
            filename = os.path.basename(file_path)
            self.title_label.config(text=f"Markdown Editor - {filename}")
            
            # Apply formatting
            self.apply_markdown_formatting()
            self.reset_undo_stack()
            
            # Update status bar
            if hasattr(self, 'status_bar'):
                self.status_bar.config(text=f"Opened: {filename}")
            
        except UnicodeDecodeError:
            messagebox.showerror("Error", "Cannot open file: Not a text file")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening file: {str(e)}")
    
    def schedule_auto_save(self):
        """Schedule an auto-save after the delay period"""
        # Cancel any existing timer
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        
        # Schedule new auto-save
        self.auto_save_timer = self.root.after(self.auto_save_delay, self.auto_save_file)
    
    def auto_save_file(self):
        """Auto-save the current file"""
        if self.current_file:
            try:
                content = self.text_area.get("1.0", tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                self.last_save_time = time.time()
                print(f"Auto-saved: {self.current_file}")
                
                # Update status bar if it exists
                if hasattr(self, 'status_bar'):
                    self.status_bar.config(text=f"Auto-saved: {os.path.basename(self.current_file)}")
                
            except Exception as e:
                print(f"Auto-save failed: {str(e)}")
                # Don't show error dialog for auto-save failures to avoid interrupting user
    
    def save_file(self):
        """Manually save the current file"""
        if self.current_file:
            try:
                content = self.text_area.get("1.0", tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                self.last_save_time = time.time()
                print(f"Saved: {self.current_file}")
                
                # Update status bar if it exists
                if hasattr(self, 'status_bar'):
                    self.status_bar.config(text=f"Saved: {os.path.basename(self.current_file)}")
                
                return True
                
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")
                return False
        else:
            # If no file is open, prompt for save as
            return self.save_file_as()
    
    def save_file_as(self):
        """Save file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=self.settings.get('default_directory', os.path.expanduser("~"))
        )
        
        if file_path:
            try:
                content = self.text_area.get("1.0", tk.END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                self.current_file = file_path
                self.last_save_time = time.time()
                
                # Update title
                filename = os.path.basename(file_path)
                self.title_label.config(text=f"Markdown Editor - {filename}")
                
                print(f"Saved as: {file_path}")
                
                # Update status bar if it exists
                if hasattr(self, 'status_bar'):
                    self.status_bar.config(text=f"Saved as: {filename}")
                
                return True
                
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")
                return False
        
        return False
    
    def setup_text_tags(self):
        """Configure text tags for different markdown styles"""
        font_family = self.settings.get('font_family', 'Arial')
        font_size = self.settings.get('font_size', 12)
        
        # H1 - Large, bold, blue
        self.text_area.tag_configure("h1", 
            font=(font_family, font_size + 12, "bold"), 
            foreground="#1e3a8a",
            spacing1=10, spacing3=10
        )
        
        # H2 - Large, bold, dark blue
        self.text_area.tag_configure("h2", 
            font=(font_family, font_size + 8, "bold"), 
            foreground="#1e40af",
            spacing1=8, spacing3=8
        )
        
        # H3 - Medium large, bold, blue
        self.text_area.tag_configure("h3", 
            font=(font_family, font_size + 6, "bold"), 
            foreground="#2563eb",
            spacing1=6, spacing3=6
        )
        
        # H4 - Medium, bold, lighter blue
        self.text_area.tag_configure("h4", 
            font=(font_family, font_size + 4, "bold"), 
            foreground="#3b82f6",
            spacing1=4, spacing3=4
        )
        
        # H5 - Small, bold, light blue
        self.text_area.tag_configure("h5", 
            font=(font_family, font_size + 2, "bold"), 
            foreground="#60a5fa",
            spacing1=2, spacing3=2
        )
        
        # H6 - Small, bold, very light blue
        self.text_area.tag_configure("h6", 
            font=(font_family, font_size, "bold"), 
            foreground="#93c5fd",
            spacing1=2, spacing3=2
        )
        
        # Bold - Bold black
        self.text_area.tag_configure("bold", 
            font=(font_family, font_size, "bold"), 
            foreground="black"
        )
        
        # Italic - Italic gray
        self.text_area.tag_configure("italic", 
            font=(font_family, font_size, "italic"), 
            foreground="#374151"
        )
    
    def insert_sample_content(self):
        """Insert sample markdown content"""
        sample_text = """# Welcome to Markdown Editor

## Features
This editor supports **bold text** and *italic text* formatting.

### Headers
You can use headers from H1 to H6:

#### H4 Header
##### H5 Header
###### H6 Header

### Try it yourself!
Type some **bold text** or *italic text* to see it formatted in real-time.

You can also create headers by typing:
- # for H1
- ## for H2
- ### for H3
- #### for H4
- ##### for H5
- ###### for H6

**Enjoy editing!**"""
        
        self.text_area.insert(tk.END, sample_text)
    
    def on_key_press(self, event):
        """Handle key press events"""
        # Allow the key to be processed normally
        return None
    
    def on_text_change(self, event):
        """Handle text change events"""
        # Apply formatting after a short delay to avoid lag
        self.root.after(50, self.apply_markdown_formatting)

        # Refresh search highlights if active
        if getattr(self, "editor_search_var", None) and self.editor_search_var.get().strip():
            self.root.after(60, self.refresh_editor_search)
        
        # Schedule auto-save
        self.schedule_auto_save()
    
    def on_window_focus_out(self, event):
        """Stop cursor blinking when window loses focus"""
        self.set_app_inactive()
    
    def on_window_focus_in(self, event):
        """Restore cursor blinking when window gains focus"""
        self.set_app_active()
    
    def set_app_active(self):
        """Mark app as active and update cursor"""
        if not self.app_is_active:
            self.app_is_active = True
            self.update_cursor_blink()
    
    def set_app_inactive(self):
        """Mark app as inactive and update cursor"""
        if self.app_is_active:
            self.app_is_active = False
            self.update_cursor_blink()
    
    def check_app_active(self):
        """Periodically check if the application is active (for Cmd-Tab detection)"""
        try:
            is_app_active = False
            
            # Method 1: Try macOS-specific check if available
            try:
                is_app_active = bool(self.root.tk.call('tk::mac::IsApplicationActive'))
            except:
                # Method 2: Use process ID comparison (most reliable)
                if self.our_pid is not None:
                    try:
                        import subprocess
                        # Get the PID of the frontmost application
                        result = subprocess.run(
                            ['osascript', '-e', 'tell application "System Events" to get unix id of first application process whose frontmost is true'],
                            capture_output=True,
                            text=True,
                            timeout=0.5
                        )
                        if result.returncode == 0:
                            try:
                                frontmost_pid = int(result.stdout.strip())
                                is_app_active = (frontmost_pid == self.our_pid)
                            except ValueError:
                                # Fallback to name-based check
                                is_app_active = self._check_name_based()
                        else:
                            # Fallback to name-based check
                            is_app_active = self._check_name_based()
                    except subprocess.TimeoutExpired:
                        # Fallback to name-based check
                        is_app_active = self._check_name_based()
                    except Exception:
                        # Fallback to name-based check
                        is_app_active = self._check_name_based()
                else:
                    # Fallback to name-based check
                    is_app_active = self._check_name_based()
            
            # Update state if it changed
            if is_app_active != self.app_is_active:
                self.app_is_active = is_app_active
                self.update_cursor_blink()
        except:
            # If all checks fail, assume inactive to stop blinking
            if self.app_is_active:
                self.app_is_active = False
                self.update_cursor_blink()
        
        # Schedule next check (every 5 seconds)
        self.root.after(5000, self.check_app_active)
    
    def _check_name_based(self):
        """Check if our app is frontmost by name"""
        try:
            import subprocess
            # Get the frontmost application's name
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to get name of first application process whose frontmost is true'],
                capture_output=True,
                text=True,
                timeout=0.5
            )
            if result.returncode == 0:
                frontmost_app = result.stdout.strip()
                # Check if it's our app (Markdown Editor)
                return ('Markdown Editor' in frontmost_app or 'Python' in frontmost_app)
            return self._check_focus_based()
        except:
            return self._check_focus_based()
    
    def _check_focus_based(self):
        """Fallback method using focus checks - unreliable but used as last resort"""
        # Note: Focus-based checks are unreliable because widgets can have focus even when app is inactive
        # This is only used when osascript completely fails
        try:
            # Check if display has focus
            displayof = self.root.focus_displayof()
            if displayof is None:
                return False
            
            # Check if window is actually visible and mapped (more reliable than just focus)
            is_mapped = True
            try:
                is_mapped = self.root.winfo_viewable()
                if not is_mapped:
                    return False
            except:
                pass
            
            # Check if any widget in our app has focus
            focused = self.root.focus_get()
            if focused is None:
                return False
            
            # Verify the focused widget belongs to our root window
            try:
                toplevel = focused.winfo_toplevel()
                is_match = (toplevel == self.root)
                # Even if match is True, be conservative - focus-based is unreliable
                # Only return True if window is viewable AND widget has focus AND it matches
                return is_match and is_mapped
            except:
                return False  # If we can't verify, assume inactive to be safe
        except:
            return False
    
    def update_cursor_blink(self):
        """Update cursor blink state based on application active status"""
        if self.app_is_active:
            # Restore original blink settings
            self.text_area.config(
                insertontime=self.cursor_blink_on_time,
                insertofftime=self.cursor_blink_off_time
            )
        else:
            # Set insertofftime to 0 to stop blinking
            self.text_area.config(insertofftime=0)
    
    def handle_undo(self, event=None):
        """Undo last edit and keep formatting/auto-save in sync."""
        try:
            self.text_area.edit_undo()
        except tk.TclError:
            return "break"
        
        # Refresh formatting after undo and keep autosave cadence
        self.root.after(10, self.apply_markdown_formatting)
        self.schedule_auto_save()
        return "break"
    
    def handle_redo(self, event=None):
        """Redo last undone edit and keep formatting/auto-save in sync."""
        try:
            self.text_area.edit_redo()
        except tk.TclError:
            return "break"
        
        # Refresh formatting after redo and keep autosave cadence
        self.root.after(10, self.apply_markdown_formatting)
        self.schedule_auto_save()
        return "break"
    
    def reset_undo_stack(self):
        """Reset undo history after programmatic content changes."""
        try:
            self.text_area.edit_reset()
            self.text_area.edit_modified(False)
        except tk.TclError:
            pass
    
    def apply_markdown_formatting(self):
        """Apply markdown formatting to the entire text"""
        # Get the current text content
        content = self.text_area.get("1.0", tk.END)
        
        # Remove all existing tags
        for tag in ["h1", "h2", "h3", "h4", "h5", "h6", "bold", "italic"]:
            self.text_area.tag_remove(tag, "1.0", tk.END)
        
        # Apply formatting patterns
        self.apply_header_formatting(content)
        self.apply_bold_formatting(content)
        self.apply_italic_formatting(content)

    def focus_editor_search(self):
        """Focus the editor search box"""
        self.editor_search_entry.focus_set()
        self.editor_search_entry.select_range(0, tk.END)

    def clear_editor_search(self):
        """Clear editor search and highlights"""
        self.editor_search_var.set("")
        self.text_area.tag_remove("search_match", "1.0", tk.END)
        self.search_matches = []
        self.search_match_index = -1
        self.last_search_query = ""
        self.text_area.focus_set()

    def refresh_editor_search(self):
        """Refresh all highlighted search matches"""
        query = self.editor_search_var.get().strip()
        if query == self.last_search_query and self.search_matches:
            return

        self.text_area.tag_remove("search_match", "1.0", tk.END)
        self.search_matches = []
        self.search_match_index = -1
        self.last_search_query = query

        if not query:
            return

        start = "1.0"
        while True:
            match_start = self.text_area.search(query, start, stopindex=tk.END, nocase=True)
            if not match_start:
                break
            match_end = f"{match_start}+{len(query)}c"
            self.search_matches.append((match_start, match_end))
            self.text_area.tag_add("search_match", match_start, match_end)
            start = match_end

        if self.search_matches:
            self.search_match_index = 0
            self._select_search_match(self.search_match_index)

    def _select_search_match(self, index):
        """Select a specific match by index and scroll into view"""
        if not self.search_matches:
            return
        index = index % len(self.search_matches)
        self.search_match_index = index
        start, end = self.search_matches[index]
        self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
        self.text_area.tag_add(tk.SEL, start, end)
        self.text_area.mark_set(tk.INSERT, end)
        self.text_area.see(start)

    def find_next_match(self):
        """Jump to the next search match"""
        if self.editor_search_var.get().strip() != self.last_search_query:
            self.refresh_editor_search()
        if not self.search_matches:
            return
        self._select_search_match(self.search_match_index + 1)

    def find_previous_match(self):
        """Jump to the previous search match"""
        if self.editor_search_var.get().strip() != self.last_search_query:
            self.refresh_editor_search()
        if not self.search_matches:
            return
        self._select_search_match(self.search_match_index - 1)
    
    def apply_header_formatting(self, content):
        """Apply header formatting"""
        lines = content.split('\n')
        line_start = 0
        
        for i, line in enumerate(lines):
            # Check for headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                tag_name = f"h{level}"
                
                # Calculate line positions
                start_pos = f"{i + 1}.0"
                end_pos = f"{i + 1}.{len(line)}"
                
                # Apply header tag
                self.text_area.tag_add(tag_name, start_pos, end_pos)
    
    def apply_bold_formatting(self, content):
        """Apply bold formatting"""
        # Find all bold patterns: **text**
        bold_pattern = r'\*\*(.*?)\*\*'
        self.apply_inline_formatting(bold_pattern, "bold")
    
    def apply_italic_formatting(self, content):
        """Apply italic formatting"""
        # Find all italic patterns: *text*
        italic_pattern = r'\*(.*?)\*'
        self.apply_inline_formatting(italic_pattern, "italic")
    
    def apply_inline_formatting(self, pattern, tag_name):
        """Apply inline formatting (bold/italic)"""
        content = self.text_area.get("1.0", tk.END)
        
        # Find all matches
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        
        for match in matches:
            start_pos = match.start()
            end_pos = match.end()
            
            # Convert character position to line.column format
            start_line_col = self.char_to_line_col(start_pos, content)
            end_line_col = self.char_to_line_col(end_pos, content)
            
            # Apply tag (excluding the markdown symbols)
            if tag_name == "bold":
                # For bold, exclude the ** symbols
                tag_start = f"{start_line_col[0]}.{start_line_col[1] + 2}"
                tag_end = f"{end_line_col[0]}.{end_line_col[1] - 2}"
            else:  # italic
                # For italic, exclude the * symbols
                tag_start = f"{start_line_col[0]}.{start_line_col[1] + 1}"
                tag_end = f"{end_line_col[0]}.{end_line_col[1] - 1}"
            
            self.text_area.tag_add(tag_name, tag_start, tag_end)
    
    def char_to_line_col(self, char_pos, content):
        """Convert character position to line and column"""
        lines = content[:char_pos].split('\n')
        line_num = len(lines)
        col_num = len(lines[-1])
        return (line_num, col_num)


def main():
    """Main function to run the markdown editor"""
    log_debug("Starting application main()...")
    
    root = None
    try:
        log_debug("Attempting to create tk.Tk()...")
        # Try to prevent the NSMenuItem crash by setting a dummy menu immediately
        # if tk.Tk() succeeds but before it does anything else.
        root = tk.Tk()
        log_debug("tk.Tk() instance created.")
    except Exception as e:
        log_debug(f"FATAL: tk.Tk() failed: {e}\n{traceback.format_exc()}")
        # If it fails here, we can't show a messagebox
        sys.exit(1)

    try:
        # Immediately create a valid menu bar to replace any default menu
        # This is the most common cause of crashes on macOS Sequoia
        try:
            log_debug("Setting up initial menu bar...")
            menubar = tk.Menu(root)
            root.config(menu=menubar)
            
            # File menu
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="Loading...", command=lambda: None)
            
            # This helps flush the menu commands
            root.update_idletasks()
            log_debug("Initial menu bar setup complete.")
        except Exception as e:
            log_debug(f"Warning: Could not create initial menu bar: {e}")
            try:
                # Try empty menu as fallback
                root.config(menu=tk.Menu(root))
            except:
                pass
        
        # Set up macOS-specific commands to prevent default menu creation
        try:
            log_debug("Setting up macOS app commands...")
            def do_nothing(): pass
            root.createcommand('tk::mac::ReopenApplication', do_nothing)
            root.createcommand('tk::mac::ShowPreferences', do_nothing)
            root.createcommand('tk::mac::ShowAbout', do_nothing)
            root.createcommand('tk::mac::Quit', lambda: root.quit())
        except Exception as e:
            log_debug(f"Warning: Could not set macOS commands: {e}")
        
        # Initialize the app
        log_debug("Initializing MarkdownEditor class...")
        app = MarkdownEditor(root)
        
        # Add a status bar
        status_bar = ttk.Label(
            root, 
            text="Ready - Use the file browser to navigate and open files", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        app.status_bar = status_bar
        
        log_debug("Entering mainloop...")
        root.mainloop()
        log_debug("Mainloop exited.")
        
    except Exception as e:
        error_msg = f"Fatal error during application execution: {e}\n{traceback.format_exc()}"
        log_debug(error_msg)
        try:
            messagebox.showerror("Application Error", f"A fatal error occurred:\n{e}")
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main() 
