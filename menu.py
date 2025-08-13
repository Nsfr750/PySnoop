"""
Menu system for PySnoop application.

This module provides a menu bar with File, Edit, View, and Help menus.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Callable, Dict, Optional
from pathlib import Path


class MenuBar(tk.Menu):
    """Main menu bar for the PySnoop application."""
    
    def __init__(self, parent, **kwargs):
        """Initialize the menu bar.
        
        Args:
            parent: The parent widget
            **kwargs: Additional arguments to pass to tk.Menu
        """
        super().__init__(parent, **kwargs)
        self.parent = parent
        
        # Menu callbacks
        self.callbacks = {
            'file': {
                'new': None,
                'open': None,
                'save': None,
                'save_as': None,
                'exit': None
            },
            'edit': {
                'preferences': None
            },
            'view': {
                'zoom_in': None,
                'zoom_out': None,
                'reset_zoom': None
            },
            'help': {
                'about': None,
                'documentation': None
            }
        }
        
        # Create menus
        self._create_file_menu()
        self._create_view_menu()
        self._create_help_menu()
    
    def set_callback(self, menu: str, item: str, callback: Callable):
        """Set a callback for a menu item.
        
        Args:
            menu: The menu name (e.g., 'file', 'edit')
            item: The menu item name (e.g., 'new', 'open')
            callback: The function to call when the menu item is selected
        """
        if menu in self.callbacks and item in self.callbacks[menu]:
            self.callbacks[menu][item] = callback
    
    def _create_file_menu(self):
        """Create the File menu."""
        file_menu = tk.Menu(self, tearoff=0)
        
        file_menu.add_command(
            label="New",
            accelerator="Ctrl+N",
            command=lambda: self._trigger_callback('file', 'new')
        )
        file_menu.add_command(
            label="Open...",
            accelerator="Ctrl+O",
            command=lambda: self._trigger_callback('file', 'open')
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Save",
            accelerator="Ctrl+S",
            command=lambda: self._trigger_callback('file', 'save')
        )
        file_menu.add_command(
            label="Save As...",
            accelerator="Ctrl+Shift+S",
            command=lambda: self._trigger_callback('file', 'save_as')
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit",
            accelerator="Alt+F4",
            command=lambda: self._trigger_callback('file', 'exit')
        )
        
        self.add_cascade(label="File", menu=file_menu)
    
    def _create_view_menu(self):
        """Create the View menu."""
        view_menu = tk.Menu(self, tearoff=0)
        
        view_menu.add_command(
            label="Zoom In",
            accelerator="Ctrl++",
            command=lambda: self._trigger_callback('view', 'zoom_in')
        )
        view_menu.add_command(
            label="Zoom Out",
            accelerator="Ctrl+-",
            command=lambda: self._trigger_callback('view', 'zoom_out')
        )
        view_menu.add_command(
            label="Reset Zoom",
            accelerator="Ctrl+0",
            command=lambda: self._trigger_callback('view', 'reset_zoom')
        )
        
        self.add_cascade(label="View", menu=view_menu)
    
    def _create_help_menu(self):
        """Create the Help menu."""
        help_menu = tk.Menu(self, tearoff=0)
        
        help_menu.add_command(
            label="Documentation",
            accelerator="F1",
            command=lambda: self._trigger_callback('help', 'documentation')
        )
        help_menu.add_separator()
        help_menu.add_command(
            label="About PySnoop",
            command=lambda: self._trigger_callback('help', 'about')
        )
        
        self.add_cascade(label="Help", menu=help_menu)
    
    def _trigger_callback(self, menu: str, item: str):
        """Trigger a menu item callback if it exists.
        
        Args:
            menu: The menu name
            item: The menu item name
        """
        callback = self.callbacks.get(menu, {}).get(item)
        if callback:
            callback()


def show_about():
    """Show the about dialog using the about module."""
    from about import create_about_tab
    import tkinter as tk
    from tkinter import ttk
    
    # Create a top-level window for the about dialog
    about_win = tk.Toplevel()
    about_win.title("About PySnoop")
    about_win.geometry("450x500")
    about_win.resizable(False, False)
    about_win.transient()  # Set to be on top of the main window
    about_win.grab_set()  # Modal
    
    # Center the window
    about_win.update_idletasks()
    width = about_win.winfo_width()
    height = about_win.winfo_height()
    x = (about_win.winfo_screenwidth() // 2) - (width // 2)
    y = (about_win.winfo_screenheight() // 2) - (height // 2)
    about_win.geometry(f'{width}x{height}+{x}+{y}')
    
    # Create the about tab content
    about_frame = create_about_tab(about_win)
    about_frame.pack(fill=tk.BOTH, expand=True)
    
    # Add a close button at the bottom
    button_frame = ttk.Frame(about_win, padding=(10, 5, 10, 10))
    button_frame.pack(fill=tk.X, side=tk.BOTTOM)
    
    close_btn = ttk.Button(
        button_frame,
        text="Close",
        command=about_win.destroy
    )
    close_btn.pack(side=tk.RIGHT)


def show_documentation():
    """Open the documentation in the default web browser."""
    import webbrowser
    webbrowser.open("http://github.com/Nsfr750/PySnoop/docs/")


def show_preferences():
    """Show the preferences dialog."""
    messagebox.showinfo("Preferences", "Preferences dialog will be implemented here.")
