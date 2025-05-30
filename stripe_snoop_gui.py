"""
Stripe Snoop 2.0 - GUI Implementation

A modern Tkinter-based GUI for the Stripe Snoop magstripe card reader application.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Dict, List, Optional, Any
import os
import sys
import threading
import queue
from pathlib import Path
from datetime import datetime

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
        
        # Print HID devices for debugging
        self.print_hid_devices()
        
        # Configure styles
        self._setup_styles()
        
        # Build the UI
        self._create_widgets()
        
        # Start the message pump
        self.after(100, self.process_messages)
    
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
            command=self.initialize_reader,
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
        
        # Reader settings
        ttk.Label(
            content,
            text="Reader Settings",
            style="Title.TLabel"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Auto-detect reader
        self.auto_detect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            content,
            text="Auto-detect reader on startup",
            variable=self.auto_detect_var
        ).pack(anchor=tk.W, pady=2)
        
        # Default reader type
        reader_frame = ttk.Frame(content)
        reader_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(reader_frame, text="Default reader:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.default_reader_var = tk.StringVar(value="MSR605")
        reader_combo = ttk.Combobox(
            reader_frame,
            textvariable=self.default_reader_var,
            values=["MSR605", "Serial", "Direct"],
            state="readonly",
            width=15
        )
        reader_combo.pack(side=tk.LEFT)
        
        # Database settings
        ttk.Label(
            content,
            text="\nDatabase Settings",
            style="Title.TLabel"
        ).pack(anchor=tk.W, pady=(10, 5))
        
        # Auto-load last database
        self.auto_load_db_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            content,
            text="Auto-load last used database on startup",
            variable=self.auto_load_db_var
        ).pack(anchor=tk.W, pady=2)
        
        # Auto-save on exit
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            content,
            text="Auto-save database on exit",
            variable=self.auto_save_var
        ).pack(anchor=tk.W, pady=2)
        
        # UI settings
        ttk.Label(
            content,
            text="\nUser Interface",
            style="Title.TLabel"
        ).pack(anchor=tk.W, pady=(10, 5))
        
        # Theme selection
        theme_frame = ttk.Frame(content)
        theme_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.theme_var = tk.StringVar(value="default")
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["default", "light", "dark", "classic"],
            state="readonly",
            width=15
        )
        theme_combo.pack(side=tk.LEFT)
        
        # Save settings button
        btn_frame = ttk.Frame(content)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        save_btn = ttk.Button(
            btn_frame,
            text="Save Settings",
            command=self.save_settings,
            style="Accent.TButton"
        )
        save_btn.pack(side=tk.RIGHT)
    
    def _create_about_tab(self):
        """Create the about tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="About")
        
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
        
        # About content
        content = ttk.Frame(scrollable_frame, padding=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            content,
            text="Stripe Snoop 2.0",
            font=('Helvetica', 18, 'bold')
        ).pack(pady=(0, 10))
        
        # Version
        ttk.Label(
            content,
            text="Version 2.0.0",
            font=('Helvetica', 10)
        ).pack(pady=(0, 20))
        
        # Description
        about_text = """
        Stripe Snoop is a suite of research tools that captures, modifies, 
        validates, generates, analyzes, and shares data from magstripe cards.
        
        This is a Python implementation of the original Stripe Snoop 
        application, providing a modern graphical user interface and 
        improved functionality.
        
        Features:
        • Read and write magstripe cards
        • Support for multiple card readers (MSR605, Serial, Direct)
        • Card database for storing and managing card data
        • Advanced card analysis and validation
        • Export/import functionality
        
        This software is intended for educational and research purposes only.
        Misuse of this software may be illegal in your jurisdiction.
        """
        
        about_label = ttk.Label(
            content,
            text=about_text,
            justify=tk.LEFT,
            wraplength=550
        )
        about_label.pack(anchor=tk.W, fill=tk.X, pady=5)
        
        # Credits
        ttk.Label(
            content,
            text="\nCredits:",
            font=('Helvetica', 10, 'bold')
        ).pack(anchor=tk.W, pady=(10, 0))
        
        credits_text = """
        • Original Concept: Acidus (acidus@msblabs.net)
        • Python Implementation: Your Name
        • Icons: Material Design Icons (https://material.io/resources/icons/)
        """
        
        credits_label = ttk.Label(
            content,
            text=credits_text,
            justify=tk.LEFT
        )
        credits_label.pack(anchor=tk.W, fill=tk.X, pady=5)
        
        # License
        ttk.Label(
            content,
            text="\nLicense:",
            font=('Helvetica', 10, 'bold')
        ).pack(anchor=tk.W, pady=(10, 0))
        
        license_text = """
        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.
        
        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.
        
        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <https://www.gnu.org/licenses/>.
        """
        
        license_label = ttk.Label(
            content,
            text=license_text,
            justify=tk.LEFT,
            font=('Courier', 8)
        )
        license_label.pack(anchor=tk.W, fill=tk.X, pady=5)
    
    def select_msr605_com_port(self):
        """Show an enhanced dialog to select and test COM port for MSR605 reader."""
        if not self.msr605_reader:
            self.status_var.set("MSR605 reader not available")
            return False
            
        def get_port_display_name(port):
            """Generate a display name with port details."""
            name = port['device']
            if port.get('description'):
                name += f" - {port['description']}"
            if port.get('vid') and port.get('pid'):
                name += f" (VID:{port['vid']:04X} PID:{port['pid']:04X})"
            return name
            
        def refresh_ports():
            """Refresh the list of available COM ports and select COM5 if available."""
            try:
                nonlocal com_ports
                com_ports = self.msr605_reader.list_serial_ports()
                if not com_ports:
                    status_label.config(text="No COM ports found", foreground="red")
                    com_combobox['values'] = []
                    com_combobox.set('')
                    return
                
                # Update combobox with available ports
                port_display_names = [get_port_display_name(port) for port in com_ports]
                com_combobox['values'] = port_display_names
                
                # Try to find and select COM5 by default
                com5_index = -1
                for i, port in enumerate(com_ports):
                    if port['device'].lower() == 'com5':
                        com5_index = i
                        break
                
                if com5_index >= 0:
                    com_combobox.current(com5_index)
                    status_label.config(text=f"Found {len(com_ports)} port(s) - COM5 selected", foreground="green")
                elif com_ports:
                    com_combobox.current(0)
                    status_label.config(text=f"Found {len(com_ports)} port(s)", foreground="green")
                else:
                    status_label.config(text="No COM ports found", foreground="red")
                    
            except Exception as e:
                status_label.config(text=f"Error: {str(e)}", foreground="red")
        
        def test_connection():
            """Test connection to the selected COM port."""
            if not com_ports or com_combobox.current() < 0:
                messagebox.showerror("Error", "No port selected")
                return False
                
            try:
                selected_port = com_ports[com_combobox.current()]['device']
                baud_rate = int(baud_var.get())
                
                test_btn.config(state=tk.DISABLED, text="Testing...")
                connect_btn.config(state=tk.DISABLED)
                refresh_btn.config(state=tk.DISABLED)
                dialog.update()
                
                # Create a temporary reader for testing
                temp_reader = MSR605Reader()
                temp_reader.set_serial_port(selected_port, baud_rate)
                
                if temp_reader.init_reader():
                    status_label.config(text=f"Successfully connected to {selected_port}", foreground="green")
                    test_btn.config(state=tk.NORMAL, text="Test Connection")
                    connect_btn.config(state=tk.NORMAL)
                    refresh_btn.config(state=tk.NORMAL)
                    return True
                else:
                    raise Exception("Failed to initialize reader")
                    
            except Exception as e:
                status_label.config(text=f"Connection failed: {str(e)}", foreground="red")
                test_btn.config(state=tk.NORMAL, text="Test Connection")
                refresh_btn.config(state=tk.NORMAL)
                return False
            finally:
                if 'temp_reader' in locals() and hasattr(temp_reader, 'close'):
                    temp_reader.close()
        
        def connect():
            """Connect to the selected COM port."""
            if not com_ports or com_combobox.current() < 0:
                messagebox.showerror("Error", "No port selected")
                return False
                
            try:
                selected_port = com_ports[com_combobox.current()]['device']
                baud_rate = int(baud_var.get())
                
                connect_btn.config(state=tk.DISABLED, text="Connecting...")
                test_btn.config(state=tk.DISABLED)
                refresh_btn.config(state=tk.DISABLED)
                dialog.update()
                
                # Set the selected COM port and baud rate
                self.msr605_reader.set_serial_port(selected_port, baud_rate)
                
                # Try to initialize the reader
                if self.msr605_reader.init_reader():
                    self.current_reader = self.msr605_reader
                    self.reader_initialized = True
                    self.status_var.set(f"MSR605 connected to {selected_port} at {baud_rate} baud")
                    dialog.destroy()
                    return True
                else:
                    raise Exception(f"Failed to initialize MSR605 on {selected_port}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to connect to {selected_port if 'selected_port' in locals() else 'selected port'}: {str(e)}")
                connect_btn.config(state=tk.NORMAL, text="Connect")
                test_btn.config(state=tk.NORMAL)
                refresh_btn.config(state=tk.NORMAL)
                return False
        
        # Main dialog setup
        dialog = tk.Toplevel(self.root)
        dialog.title("MSR605 Connection Settings")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Make dialog modal
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable close button
        
        # Set dialog size and position
        dialog_width = 500
        dialog_height = 300
        x = (self.root.winfo_screenwidth() // 2) - (dialog_width // 2)
        y = (self.root.winfo_screenheight() // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        dialog.minsize(dialog_width, dialog_height)
        dialog.resizable(True, False)
        
        # Main container
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            main_frame,
            text="MSR605 Reader Connection",
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 15), anchor=tk.W)
        
        # Port selection frame
        port_frame = ttk.LabelFrame(main_frame, text="Port Settings", padding=10)
        port_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Port selection row
        port_row = ttk.Frame(port_frame)
        port_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(port_row, text="COM Port:").pack(side=tk.LEFT, padx=(0, 5))
        
        com_ports = []
        com_var = tk.StringVar()
        com_combobox = ttk.Combobox(
            port_row,
            textvariable=com_var,
            state="readonly",
            width=40
        )
        com_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        refresh_btn = ttk.Button(
            port_row,
            text="🔄",
            width=3,
            command=refresh_ports
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Baud rate selection row
        baud_row = ttk.Frame(port_frame)
        baud_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(baud_row, text="Baud Rate:").pack(side=tk.LEFT, padx=(0, 5))
        
        baud_var = tk.StringVar(value="9600")
        baud_combobox = ttk.Combobox(
            baud_row,
            textvariable=baud_var,
            values=["9600", "19200", "38400", "57600", "115200"],
            state="readonly",
            width=10
        )
        baud_combobox.pack(side=tk.LEFT, padx=(0, 5))
        
        # Status label
        status_label = ttk.Label(
            port_frame,
            text="Select a COM port and click 'Test Connection'"
        )
        status_label.pack(fill=tk.X, pady=(10, 0))
        
        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        test_btn = ttk.Button(
            btn_frame,
            text="Test Connection",
            command=test_connection
        )
        test_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        connect_btn = ttk.Button(
            btn_frame,
            text="Connect",
            command=connect,
            style="Accent.TButton"
        )
        connect_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT)
        
        # Initial refresh of ports
        refresh_ports()
        
        # Set focus to the dialog
        dialog.focus_set()
        
        # Wait for dialog to close
        self.wait_window(dialog)
        
        return self.reader_initialized
    
    def on_reader_change(self, event=None):
        """Handle reader selection change."""
        reader_type = self.reader_var.get()
        self.status_var.set(f"Selected reader: {reader_type}")
        
        # Reset current reader
        self.current_reader = None
        self.reader_initialized = False
        
        # Handle MSR605 reader with COM port selection
        if reader_type == 'MSR605' and self.msr605_reader is not None:
            self.select_msr605_com_port()
        # For other readers, just set them as current
        elif reader_type in self.readers:
            self.current_reader = self.readers[reader_type]
            self.reader_initialized = True
            self.status_var.set(f"{reader_type} reader ready")
        else:
            self.status_var.set("Reader not available")

    def initialize_reader(self):
        """Initialize the selected card reader."""
        reader_type = self.reader_var.get()
        self.status_var.set(f"Initializing {reader_type} reader...")
        self.update()  # Force UI update
        
        try:
            # Update status in the UI
            self.status_var.set(f"Creating {reader_type} reader instance...")
            self.update()
            
            if reader_type == "MSR605":
                from msr605_reader import MSR605Reader, list_msr605_devices
                
                # List available MSR605 devices for debugging
                devices = list_msr605_devices()
                if not devices:
                    messagebox.showerror("Error", "No MSR605 devices found. Please ensure the device is connected and drivers are installed.")
                    self.status_var.set("No MSR605 devices found")
                    return
                    
                print(f"Found {len(devices)} MSR605 device(s):")
                for i, dev in enumerate(devices):
                    print(f"  {i+1}. Path: {dev.get('path', 'N/A')}, "
                          f"Serial: {dev.get('serial_number', 'N/A')}, "
                          f"Manufacturer: {dev.get('manufacturer_string', 'N/A')}")
                
                # Use the first device found
                self.reader = MSR605Reader()
                
                # Get available COM ports
                com_ports = self.reader.list_serial_ports()
                if com_ports:
                    self.com_port_combo['values'] = [port['device'] for port in com_ports]
                    self.com_port_combo.current(0)
                else:
                    messagebox.showerror("Error", "No serial ports found")
                    self.status_var.set("No serial ports found")
                    return
                
            elif reader_type == "Serial":
                from reader import SerialReader
                self.reader = SerialReader()
                # TODO: Configure serial reader with actual device path
                messagebox.showinfo("Info", "Please configure serial device path in settings")
                return
                
            elif reader_type == "Direct":
                from reader import DirectReader
                self.reader = DirectReader()
                # TODO: Configure direct reader with actual pin configuration
                messagebox.showinfo("Info", "Please configure direct reader pins in settings")
                return
                
            else:
                messagebox.showerror("Error", f"Unknown reader type: {reader_type}")
                self.status_var.set("Unknown reader type")
                return
            
            # Initialize the reader with detailed status updates
            self.status_var.set(f"Initializing {reader_type} hardware...")
            self.update()
            
            if self.reader.init_reader():
                self.status_var.set(f"{reader_type} reader initialized successfully")
                self.read_btn.config(state=tk.NORMAL)
                self.init_btn.config(state=tk.DISABLED)
                self.reader_combo.config(state=tk.DISABLED)
                
                # Set readable tracks if not already set
                if not self.reader.readable_tracks:
                    self.reader.readable_tracks = [1, 2, 3]  # Default to all tracks
                
                print(f"{reader_type} reader initialized successfully")
                print(f"Readable tracks: {self.reader.readable_tracks}")
                
            else:
                error_msg = f"Failed to initialize {reader_type} reader.\n\n"
                error_msg += "Possible causes:\n"
                error_msg += "1. Device not connected\n"
                error_msg += "2. Insufficient permissions (try running as administrator)\n"
                error_msg += "3. Driver not installed\n"
                error_msg += "4. Device in use by another application"
                
                messagebox.showerror("Initialization Failed", error_msg)
                self.status_var.set("Reader initialization failed")
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_msg = f"Failed to initialize {reader_type} reader: {str(e)}\n\n"
            error_msg += "Error details:\n"
            error_msg += error_details
            
            print(error_msg)  # Print to console for debugging
            messagebox.showerror("Error", error_msg)
            self.status_var.set(f"Error: {str(e)}")
            
            # Print available HID devices for debugging
            try:
                import hid
                print("\nAvailable HID devices:")
                for device in hid.enumerate():
                    print(f"- Vendor: 0x{device['vendor_id']:04x}, "
                          f"Product: 0x{device['product_id']:04x}, "
                          f"Manufacturer: {device.get('manufacturer_string', 'N/A')}, "
                          f"Product: {device.get('product_string', 'N/A')}")
            except Exception as hid_error:
                print(f"\nError listing HID devices: {hid_error}")
    
    def read_card(self):
        """Start reading a card in a separate thread."""
        if not self.reader:
            messagebox.showerror("Error", "Reader not initialized")
            return
        
        self.stop_event.clear()
        self.read_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("Reading card... (Swipe card now)")
        
        # Clear previous card data
        self.current_card = None
        self.track_text.delete(1.0, tk.END)
        self.card_type_var.set("Reading...")
        
        # Start reading in a separate thread
        self.reader_thread = threading.Thread(target=self._read_card_thread, daemon=True)
        self.reader_thread.start()
    
    def _read_card_thread(self):
        """Thread function for reading a card."""
        try:
            card = self.reader.read()
            self.message_queue.put(('card_read', card))
        except Exception as e:
            self.message_queue.put(('error', f"Error reading card: {str(e)}"))
    
    def stop_reading(self):
        """Stop the current card reading operation."""
        if self.reader_thread and self.reader_thread.is_alive():
            self.stop_event.set()
            # TODO: Implement proper reader cancellation
            self.reader_thread.join(timeout=1.0)
        
        self.read_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Reading stopped")
    
    def process_messages(self):
        """Process messages from worker threads."""
        try:
            while True:
                try:
                    msg_type, *args = self.message_queue.get_nowait()
                    
                    if msg_type == 'card_read':
                        self._handle_card_read(args[0])
                    elif msg_type == 'error':
                        messagebox.showerror("Error", args[0])
                        self.status_var.set(f"Error: {args[0]}")
                    
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"Error processing messages: {e}")
        
        # Schedule the next check
        self.after(100, self.process_messages)
    
    def _handle_card_read(self, card):
        """Handle a successfully read card."""
        self.current_card = card
        self.read_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Display track data
        self.track_text.delete(1.0, tk.END)
        
        for track_num, track in card.tracks.items():
            self.track_text.insert(tk.END, f"=== Track {track_num} ===\n")
            self.track_text.insert(tk.END, f"Raw: {track.get_raw_data()}\n")
            self.track_text.insert(tk.END, f"Decoded: {track.get_decoded_data()}\n\n")
        
        # Update card type
        # TODO: Implement card type detection
        self.card_type_var.set("Magnetic Stripe Card")
        
        # Enable save button if we have a database loaded
        # TODO: Implement database functionality
        
        self.status_var.set("Card read successfully")
    
    def browse_database(self):
        """Open a file dialog to select a database file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            title="Select Database File"
        )
        
        if file_path:
            self.db_path_var.set(file_path)
    
    def load_database(self):
        """Load a card database from file."""
        db_path = self.db_path_var.get().strip()
        
        if not db_path:
            messagebox.showwarning("Warning", "Please select a database file")
            return
        
        try:
            # TODO: Implement database loading
            messagebox.showinfo("Success", f"Database loaded from {db_path}")
            self.status_var.set(f"Database loaded: {os.path.basename(db_path)}")
            
            # Update card list
            self._update_card_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load database: {str(e)}")
            self.status_var.set("Error loading database")
    
    def _update_card_list(self):
        """Update the list of cards in the database."""
        # Clear existing items
        for item in self.card_tree.get_children():
            self.card_tree.delete(item)
        
        # TODO: Load cards from database and add to treeview
        # Example:
        # for card in self.db.get_all_cards():
        #     self.card_tree.insert("", tk.END, values=(
        #         card.id,
        #         card.type,
        #         card.number,
        #         card.name,
        #         card.date
        #     ))
        
        # For now, just add a placeholder
        self.card_tree.insert("", tk.END, values=(
            "1",
            "Credit",
            "************1234",
            "John Doe",
            "2023-01-01"
        ))
    
    def on_card_select(self, event):
        """Handle selection of a card in the treeview."""
        selected = self.card_tree.selection()
        if not selected:
            return
        
        # Get the selected item's values
        item = self.card_tree.item(selected[0])
        values = item['values']
        
        if not values:
            return
        
        # Display card details
        # TODO: Load full card details from database
        details = f"ID: {values[0]}\n"
        details += f"Type: {values[1]}\n"
        details += f"Number: {values[2]}\n"
        details += f"Name: {values[3]}\n"
        details += f"Date: {values[4]}"
        
        self.card_details.delete(1.0, tk.END)
        self.card_details.insert(tk.END, details)
    
    def save_settings(self):
        """Save application settings."""
        # TODO: Implement settings persistence
        messagebox.showinfo("Settings", "Settings saved successfully")
        self.status_var.set("Settings saved")
    
    def on_closing(self):
        """Handle application closing."""
        # Stop any running operations
        self.stop_reading()
        
        # Save settings if needed
        if hasattr(self, 'auto_save_var') and self.auto_save_var.get():
            self.save_settings()
        
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
