"""
Stripe Snoop 2.0 - GUI Implementation

A modern Tkinter-based GUI for the Stripe Snoop magstripe card reader application.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Dict, List, Optional, Any, Union
import os
import sys
import json
import threading
import queue
from pathlib import Path
from datetime import datetime
import appdirs

# Import core functionality
from card import Card
from reader import load_config, Reader
from database import CardDatabase
from ssflags import SSFlags

# Try to import ttkthemes for better looking UI
try:
    from ttkthemes import ThemedStyle
    THEMED_UI = True
except ImportError:
    THEMED_UI = False
    print("Note: ttkthemes not found, using default theme")

class StripeSnoopGUI(tk.Tk):
    """Main application window for Stripe Snoop GUI."""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        self.title("Stripe Snoop 2.0")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Initialize flags and state
        self.flags = SSFlags()
        self.reader = None
        self.db = CardDatabase()
        self.current_card = None
        self.reader_thread = None
        self.stop_event = threading.Event()
        self.message_queue = queue.Queue()
        
        # Default settings
        self.settings = {
            'window_geometry': '1000x700',
            'theme': 'default',
            'recent_files': [],
            'last_directory': str(Path.home()),
            'msr605_port': None,
            'msr605_baud': 9600,
            'auto_save': True,
            'auto_load': True,
            'check_updates': True,
            'max_recent_files': 10
        }
        
        # Load settings
        self.settings_file = Path(appdirs.user_config_dir('stripe_snoop')) / 'settings.json'
        self._load_settings()
        
        # Apply loaded geometry if available
        if 'window_geometry' in self.settings:
            self.geometry(self.settings['window_geometry'])
        
        # Print HID devices for debugging
        self.print_hid_devices()
        
        # Configure styles
        self._setup_styles()
        
        # Build the UI
        self._create_widgets()
        
        # Start the message pump
        self.after(100, self.process_messages)
        
        # Save settings on window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def print_hid_devices(self):
        """Print all connected HID devices for debugging."""
        try:
            import hid
            print("\n=== Connected HID Devices ===")
            devices = hid.enumerate()
            if not devices:
                print("No HID devices found")
            else:
                for i, device in enumerate(devices, 1):
                    print(f"\nDevice {i}:")
                    for key, value in device.items():
                        if isinstance(value, (str, int, float, bool)) or value is None:
                            print(f"  {key}: {value}")
                        elif isinstance(value, bytes):
                            try:
                                print(f"  {key}: {value.decode('utf-8', errors='replace')}")
                            except:
                                print(f"  {key}: <binary data>")
            print("\n" + "="*50 + "\n")
        except Exception as e:
            print(f"Error listing HID devices: {e}")
    
    def _setup_styles(self):
        """Configure application styles."""
        if THEMED_UI:
            self.style = ThemedStyle(self)
            self.style.set_theme("arc")  # Use a nice theme if available
        else:
            self.style = ttk.Style()
        
        # Configure custom styles
        self.style.configure("Card.TFrame", background="#f5f5f5")
        self.style.configure("Status.TLabel", padding=5, relief=tk.SUNKEN, anchor=tk.W)
        self.style.configure("Title.TLabel", font=('Helvetica', 12, 'bold'))
        self.style.configure("Subtitle.TLabel", font=('Helvetica', 10, 'bold'))
        self.style.map("Accent.TButton",
                      foreground=[('active', 'white'), ('!disabled', 'white')],
                      background=[('active', '#0052cc'), ('!disabled', '#0066ff')])
    
    def _create_widgets(self):
        """Create and arrange all UI widgets."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create tabs
        self._create_reader_tab()
        self._create_database_tab()
        self._create_settings_tab()
        self._create_about_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_container,
            textvariable=self.status_var,
            style="Status.TLabel"
        )
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def _create_reader_tab(self):
        """Create the card reader tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Card Reader")
        
        # Main container with padding
        container = ttk.Frame(tab, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Reader controls frame
        ctrl_frame = ttk.LabelFrame(container, text="Reader Controls", padding=10)
        ctrl_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Reader selection
        ttk.Label(ctrl_frame, text="Reader:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.reader_var = tk.StringVar()
        self.reader_combo = ttk.Combobox(
            ctrl_frame,
            textvariable=self.reader_var,
            values=["MSR605", "Serial", "Direct"],
            state="readonly",
            width=15
        )
        self.reader_combo.set("MSR605")  # Default to MSR605
        self.reader_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # COM port selection for MSR605
        self.com_port_var = tk.StringVar()
        self.com_port_combo = ttk.Combobox(
            ctrl_frame,
            textvariable=self.com_port_var,
            values=[],
            state="readonly",
            width=15
        )
        self.com_port_combo.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Initialize button
        self.init_btn = ttk.Button(
            ctrl_frame,
            text="Initialize Reader",
            command=self.init_reader,
            style="Accent.TButton"
        )
        self.init_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Read button
        self.read_btn = ttk.Button(
            ctrl_frame,
            text="Read Card",
            command=self.read_card,
            state=tk.DISABLED
        )
        self.read_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # Stop button
        self.stop_btn = ttk.Button(
            ctrl_frame,
            text="Stop",
            command=self.stop_reading,
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Card display area
        card_frame = ttk.LabelFrame(container, text="Card Data", padding=10)
        card_frame.pack(fill=tk.BOTH, expand=True)
        
        # Track data display
        self.track_text = scrolledtext.ScrolledText(
            card_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Consolas', 10)
        )
        self.track_text.pack(fill=tk.BOTH, expand=True)
        
        # Card info frame
        info_frame = ttk.Frame(card_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(info_frame, text="Card Type:").pack(side=tk.LEFT, padx=(0, 10))
        self.card_type_var = tk.StringVar(value="Unknown")
        ttk.Label(info_frame, textvariable=self.card_type_var, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
    
    def _create_database_tab(self):
        """Create the database management tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Database")
        
        # Main container with padding
        container = ttk.Frame(tab, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Database controls
        ctrl_frame = ttk.Frame(container)
        ctrl_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Database file path
        ttk.Label(ctrl_frame, text="Database:").pack(side=tk.LEFT, padx=(0, 5))
        self.db_path_var = tk.StringVar()
        db_entry = ttk.Entry(ctrl_frame, textvariable=self.db_path_var, width=40)
        db_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(
            ctrl_frame,
            text="Browse...",
            command=self.browse_database
        )
        browse_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        load_btn = ttk.Button(
            ctrl_frame,
            text="Load",
            command=self.load_database,
            style="Accent.TButton"
        )
        load_btn.pack(side=tk.LEFT)
        
        # Card list
        list_frame = ttk.LabelFrame(container, text="Cards in Database")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for card list
        columns = ("id", "type", "number", "name", "date")
        self.card_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Configure columns
        self.card_tree.heading("id", text="ID")
        self.card_tree.heading("type", text="Type")
        self.card_tree.heading("number", text="Number")
        self.card_tree.heading("name", text="Name")
        self.card_tree.heading("date", text="Date")
        
        self.card_tree.column("id", width=50, anchor=tk.CENTER)
        self.card_tree.column("type", width=100, anchor=tk.W)
        self.card_tree.column("number", width=150, anchor=tk.W)
        self.card_tree.column("name", width=200, anchor=tk.W)
        self.card_tree.column("date", width=150, anchor=tk.W)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.card_tree.yview
        )
        self.card_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.card_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Card details frame
        details_frame = ttk.LabelFrame(container, text="Card Details")
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        self.card_details = scrolledtext.ScrolledText(
            details_frame,
            wrap=tk.WORD,
            width=80,
            height=10,
            font=('Consolas', 9)
        )
        self.card_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind selection event
        self.card_tree.bind("<<TreeviewSelect>>", self.on_card_select)
    
    def _create_settings_tab(self):
        """Create the settings tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Settings")
        
        # Main container with padding and scrolling
        container = ttk.Frame(tab)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas and scrollbar for scrolling content
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Settings content
        content = ttk.Frame(scrollable_frame, padding=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Appearance section
        ttk.Label(
            content,
            text="Appearance",
            font=('Helvetica', 12, 'bold')
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Theme selection
        theme_frame = ttk.Frame(content)
        theme_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.theme_var = tk.StringVar(value=self.settings.get('theme', 'default'))
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["default", "light", "dark", "classic"],
            state="readonly",
            width=15
        )
        theme_combo.pack(side=tk.LEFT)
        
        # Application section
        ttk.Label(
            content,
            text="Application",
            font=('Helvetica', 12, 'bold')
        ).pack(anchor=tk.W, pady=(20, 10))
        
        # Auto-save settings
        auto_save_frame = ttk.Frame(content)
        auto_save_frame.pack(fill=tk.X, pady=5)
        
        self.auto_save_var = tk.BooleanVar(value=self.settings.get('auto_save', True))
        auto_save_cb = ttk.Checkbutton(
            auto_save_frame,
            text="Auto-save settings on exit",
            variable=self.auto_save_var
        )
        auto_save_cb.pack(anchor=tk.W)
        
        # Auto-load last file
        auto_load_frame = ttk.Frame(content)
        auto_load_frame.pack(fill=tk.X, pady=5)
        
        self.auto_load_var = tk.BooleanVar(value=self.settings.get('auto_load', True))
        auto_load_cb = ttk.Checkbutton(
            auto_load_frame,
            text="Auto-load last opened file",
            variable=self.auto_load_var
        )
        auto_load_cb.pack(anchor=tk.W)
        
        # Check for updates
        update_frame = ttk.Frame(content)
        update_frame.pack(fill=tk.X, pady=5)
        
        self.check_updates_var = tk.BooleanVar(value=self.settings.get('check_updates', True))
        update_cb = ttk.Checkbutton(
            update_frame,
            text="Check for updates on startup",
            variable=self.check_updates_var
        )
        update_cb.pack(anchor=tk.W)
        
        # MSR605 Settings
        ttk.Label(
            content,
            text="MSR605 Reader",
            font=('Helvetica', 12, 'bold')
        ).pack(anchor=tk.W, pady=(20, 10))
        
        # COM Port
        port_frame = ttk.Frame(content)
        port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(port_frame, text="Default COM Port:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.port_var = tk.StringVar(value=self.settings.get('msr605_port', ''))
        port_entry = ttk.Entry(port_frame, textvariable=self.port_var, width=15)
        port_entry.pack(side=tk.LEFT)
        
        # Baud Rate
        baud_frame = ttk.Frame(content)
        baud_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(baud_frame, text="Baud Rate:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.baud_var = tk.StringVar(value=str(self.settings.get('msr605_baud', 9600)))
        baud_combo = ttk.Combobox(
            baud_frame,
            textvariable=self.baud_var,
            values=["9600", "19200", "38400", "57600", "115200"],
            state="readonly",
            width=10
        )
        baud_combo.pack(side=tk.LEFT)
        
        # Save settings button
        btn_frame = ttk.Frame(content)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Reset to defaults button
        reset_btn = ttk.Button(
            btn_frame,
            text="Reset to Defaults",
            command=self._reset_settings
        )
        reset_btn.pack(side=tk.LEFT)
        
        # Save button
        save_btn = ttk.Button(
            btn_frame,
            text="Save Settings",
            command=self.save_settings,
            style="Accent.TButton"
        )
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
    def _load_settings(self):
        """Load settings from file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
                    
                    # Update window geometry if it was saved
                    if 'window_geometry' in self.settings:
                        self.geometry(self.settings['window_geometry'])
                        
        except Exception as e:
            print(f"Error loading settings: {e}")
            # If there's an error, continue with default settings
    
    def save_settings(self):
        """Save current settings to file."""
        try:
            # Update settings dictionary with current values
            self.settings.update({
                'window_geometry': self.geometry(),
                'theme': self.theme_var.get(),
                'msr605_port': self.port_var.get(),
                'msr605_baud': int(self.baud_var.get()),
                'auto_save': self.auto_save_var.get(),
                'auto_load': self.auto_load_var.get(),
                'check_updates': self.check_updates_var.get(),
                'last_directory': self.settings.get('last_directory', str(Path.home()))
            })
            
            # Ensure the settings directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
                
            messagebox.showinfo("Settings", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _reset_settings(self):
        """Reset settings to default values."""
        if messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to default values?"
        ):
            # Reset to default values
            self.theme_var.set('default')
            self.port_var.set('')
            self.baud_var.set('9600')
            self.auto_save_var.set(True)
            self.auto_load_var.set(True)
            self.check_updates_var.set(True)
            
            # Save the reset settings
            self.save_settings()
    
    def update_recent_files(self, file_path: Union[str, Path]):
        """Update the list of recently opened files."""
        if isinstance(file_path, Path):
            file_path = str(file_path)
            
        if 'recent_files' not in self.settings:
            self.settings['recent_files'] = []
            
        # Remove if already in the list
        if file_path in self.settings['recent_files']:
            self.settings['recent_files'].remove(file_path)
            
        # Add to the beginning of the list
        self.settings['recent_files'].insert(0, file_path)
        
        # Keep only the most recent files
        max_files = self.settings.get('max_recent_files', 10)
        self.settings['recent_files'] = self.settings['recent_files'][:max_files]
        
        # Save the updated settings
        self.save_settings()
    
    def on_closing(self):
        """Handle application closing."""
        # Stop any ongoing operations
        self.stop_reading()
        
        # Save settings if auto-save is enabled
        if self.auto_save_var.get():
            try:
                self.save_settings()
            except Exception as e:
                print(f"Error saving settings on exit: {e}")
        
        # Close any open files or connections
        if hasattr(self, 'reader') and self.reader:
            try:
                self.reader.close()
            except Exception as e:
                print(f"Error closing reader: {e}")
        
        # Close the application
        self.destroy()

def main():
    """Main entry point for the application."""
    try:
        app = StripeSnoopGUI()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
