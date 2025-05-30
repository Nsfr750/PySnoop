"""
Stripe Snoop 2.0 - GUI Implementation

A modern Tkinter-based GUI for the Stripe Snoop magstripe card reader application.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Dict, List, Optional, Any, Union
import os
import sys
import queue
import threading
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import appdirs
import serial.tools.list_ports

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
    
    def init_reader(self):
        """Initialize the selected card reader."""
        reader_type = self.reader_var.get()
        com_port = self.com_port_var.get()
        
        if not com_port:
            messagebox.showerror("Error", "Please select a COM port")
            return
            
        try:
            if reader_type == "MSR605":
                from msr605_serial import MSR605Reader
                self.reader = MSR605Reader(com_port=com_port)
                if self.reader.init_reader():
                    messagebox.showinfo("Success", f"Successfully initialized {reader_type} on {com_port}")
                    self.read_btn.config(state=tk.NORMAL)
                    self.stop_btn.config(state=tk.DISABLED)
                else:
                    messagebox.showerror("Error", f"Failed to initialize {reader_type} on {com_port}")
                    self.read_btn.config(state=tk.DISABLED)
                    self.stop_btn.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize reader: {str(e)}")
            self.read_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
    
    def read_card(self):
        """Read data from the card using the initialized reader."""
        if not self.reader or not hasattr(self.reader, 'read'):
            messagebox.showerror("Error", "Reader not properly initialized")
            return
            
        try:
            self.track_text.delete(1.0, tk.END)  # Clear previous data
            self.track_text.insert(tk.END, "Swipe card now...\n")
            self.read_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            # Read card data in a separate thread to avoid freezing the UI
            def read_thread():
                try:
                    card_data = self.reader.read()
                    if card_data:
                        self.message_queue.put(('data', card_data))
                    else:
                        self.message_queue.put(('error', "No data read from card"))
                except Exception as e:
                    self.message_queue.put(('error', f"Error reading card: {str(e)}"))
                finally:
                    self.message_queue.put(('done', None))
            
            threading.Thread(target=read_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read card: {str(e)}")
            self.read_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def stop_reading(self):
        """Stop the current card reading operation."""
        if hasattr(self.reader, 'cancel_read'):
            self.reader.cancel_read()
        self.read_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
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
        
        # Configure grid weights
        ctrl_frame.columnconfigure(1, weight=1)
        
        # Row 0: Reader selection
        ttk.Label(ctrl_frame, text="Reader:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.reader_var = tk.StringVar()
        self.reader_combo = ttk.Combobox(
            ctrl_frame,
            textvariable=self.reader_var,
            values=["MSR605"],  # Only MSR605 is supported for now
            state="readonly",
            width=15
        )
        self.reader_combo.set("MSR605")  # Default to MSR605
        self.reader_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Initialize button
        self.init_btn = ttk.Button(
            ctrl_frame,
            text="Initialize Reader",
            command=self.init_reader,
            style="Accent.TButton"
        )
        self.init_btn.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # Row 1: COM port selection
        ttk.Label(ctrl_frame, text="COM Port:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # COM port selection frame
        com_frame = ttk.Frame(ctrl_frame)
        com_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, pady=5)
        
        # COM port variable and combobox
        self.com_port_var = tk.StringVar()
        
        def get_available_ports():
            """Get a list of available COM ports."""
            ports = []
            try:
                # Try to get detailed port information
                ports = [port.device for port in serial.tools.list_ports.comports()]
                if not ports:  # If no ports found, try alternative method
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'HARDWARE\\DEVICEMAP\\SERIALCOMM') as key:
                        for i in range(1024):
                            try:
                                port = winreg.EnumValue(key, i)[1]
                                if port not in ports:
                                    ports.append(port)
                            except WindowsError:
                                break
            except Exception as e:
                print(f"Error detecting COM ports: {e}")
            return sorted(ports, key=lambda x: int(x[3:]) if x[3:].isdigit() else float('inf'))
        
        # Create COM port dropdown
        self.com_port_combo = ttk.Combobox(
            com_frame,
            textvariable=self.com_port_var,
            values=get_available_ports(),
            state="readonly",
            width=15
        )
        self.com_port_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        # Add refresh button
        def refresh_ports():
            ports = get_available_ports()
            self.com_port_combo['values'] = ports
            if ports and not self.com_port_var.get():
                self.com_port_var.set(ports[0])
        
        refresh_btn = ttk.Button(
            com_frame,
            text="🔄",
            width=3,
            command=refresh_ports
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Auto-refresh ports on tab open
        refresh_ports()
        
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
    
    def browse_database(self):
        """Open a file dialog to select a database file."""
        initial_dir = self.settings.get('last_directory', str(Path.home()))
        file_path = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("SQLite Database", "*.db"), ("JSON Database", "*.json"), ("All Files", "*.*")],
            initialdir=initial_dir
        )
        if file_path:
            self.db_path_var.set(file_path)
            self.settings['last_directory'] = str(Path(file_path).parent)
            self.save_settings()
    
    def load_database(self):
        """Load the selected database file."""
        db_path = self.db_path_var.get().strip()
        if not db_path:
            messagebox.showerror("Error", "Please select a database file")
            return
            
        try:
            if db_path.endswith('.json'):
                # Load JSON database
                with open(db_path, 'r') as f:
                    data = json.load(f)
                self.db.load_from_dict(data)
            else:
                # Load SQLite database
                self.db.load(db_path)
                
            self._populate_card_list()
            messagebox.showinfo("Success", f"Successfully loaded database from {db_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load database: {str(e)}")
    
    def _populate_card_list(self):
        """Populate the card list with data from the database."""
        # Clear existing items
        for item in self.card_tree.get_children():
            self.card_tree.delete(item)
            
        # Add cards from database
        for card in self.db.get_all_cards():
            self.card_tree.insert(
                "", "end",
                values=(
                    card.id,
                    card.card_type or "",
                    card.get_masked_number(),
                    card.cardholder_name or "",
                    card.expiration_date or ""
                )
            )
    
    def _create_database_tab(self):
        """Create the database management tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Database")
        
        # Main container with padding
        container = ttk.Frame(tab, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Controls frame
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
    
    def on_card_select(self, event):
        """Handle card selection in the database view."""
        selected_items = self.card_tree.selection()
        if not selected_items:
            return
            
        # Get the selected item's values
        item = selected_items[0]
        values = self.card_tree.item(item, 'values')
        
        if not values or len(values) < 5:
            return
            
        try:
            # Get the card ID from the first column
            card_id = int(values[0])
            
            # Get the card from the database
            card = self.db.get_card_by_id(card_id)
            if not card:
                return
                
            # Format and display the card details
            details = []
            details.append(f"Card Type: {card.card_type or 'Unknown'}")
            details.append(f"Card Number: {card.get_masked_number()}")
            details.append(f"Expiration: {card.expiration_date or 'N/A'}")
            details.append(f"Cardholder: {card.cardholder_name or 'N/A'}")
            details.append(f"Issuer: {card.issuer or 'Unknown'}")
            details.append("\nTrack 1 Data:")
            details.append(card.track1 or "No data")
            details.append("\nTrack 2 Data:")
            details.append(card.track2 or "No data")
            if card.track3:
                details.append("\nTrack 3 Data:")
                details.append(card.track3)
                
            self.card_details.config(state=tk.NORMAL)
            self.card_details.delete(1.0, tk.END)
            self.card_details.insert(tk.END, '\n'.join(details))
            self.card_details.config(state=tk.DISABLED)
            
        except Exception as e:
            self.card_details.config(state=tk.NORMAL)
            self.card_details.delete(1.0, tk.END)
            self.card_details.insert(tk.END, f"Error displaying card details: {str(e)}")
            self.card_details.config(state=tk.DISABLED)
    
    def _create_about_tab(self):
        """Create the about tab with application information."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="About")
        
        # Main container with padding
        container = ttk.Frame(tab, padding=20)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Application title
        title_label = ttk.Label(
            container,
            text="Stripe Snoop 2.0",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Version information
        version_label = ttk.Label(
            container,
            text="Version 2.0.0",
            font=('Helvetica', 10)
        )
        version_label.pack(pady=(0, 20))
        
        # Description
        desc_text = (
            "A modern application for reading and managing magnetic stripe card data.\n\n"
            "Features:\n"
            "• Read magnetic stripe cards using compatible readers\n"
            "• View and manage card data in a database\n"
            "• Export/Import card data in multiple formats\n"
            "• User-friendly interface with theming support"
        )
        desc_label = ttk.Label(
            container,
            text=desc_text,
            justify=tk.LEFT,
            wraplength=500
        )
        desc_label.pack(pady=(0, 20), anchor='w')
        
        # Copyright and license
        copyright_label = ttk.Label(
            container,
            text="© 2023 Stripe Snoop Project\nMIT License",
            font=('Helvetica', 8),
            foreground='gray'
        )
        copyright_label.pack(side=tk.BOTTOM, pady=(10, 0))
        
        # GitHub link
        github_btn = ttk.Button(
            container,
            text="View on GitHub",
            command=lambda: webbrowser.open("https://github.com/yourusername/stripe-snoop")
        )
        github_btn.pack(pady=(20, 0))
    
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
    
    def process_messages(self):
        """Process messages from the message queue."""
        try:
            while True:
                try:
                    # Get message from queue (non-blocking)
                    msg_type, data = self.message_queue.get_nowait()
                    
                    if msg_type == 'data':
                        # Handle card data
                        self._handle_card_data(data)
                    elif msg_type == 'error':
                        # Handle error message
                        messagebox.showerror("Error", data)
                    elif msg_type == 'done':
                        # Reading operation completed
                        self.read_btn.config(state=tk.NORMAL)
                        self.stop_btn.config(state=tk.DISABLED)
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error processing messages: {str(e)}")
            
        # Schedule the next check
        self.after(100, self.process_messages)
    
    def _handle_card_data(self, card_data):
        """Handle card data received from the reader."""
        try:
            # Update the UI with the card data
            self.track_text.delete(1.0, tk.END)
            
            # Display track data
            if 'track1' in card_data:
                self.track_text.insert(tk.END, "Track 1: " + card_data['track1'] + "\n\n")
            if 'track2' in card_data:
                self.track_text.insert(tk.END, "Track 2: " + card_data['track2'] + "\n\n")
            if 'track3' in card_data:
                self.track_text.insert(tk.END, "Track 3: " + card_data['track3'] + "\n\n")
                
            # Parse and display card information
            if 'track1' in card_data and card_data['track1']:
                # Try to parse track 1 data
                try:
                    # Format: %B1234567890123456^CARDHOLDER/NAME^YYMM...
                    track1 = card_data['track1']
                    if track1.startswith('%B'):
                        parts = track1.split('^')
                        if len(parts) >= 3:
                            card_number = parts[0][2:].strip()  # Remove %B
                            name_parts = parts[1].split('/')
                            last_name = name_parts[0].strip()
                            first_name = name_parts[1].strip() if len(name_parts) > 1 else ''
                            exp_date = parts[2][:4]  # YYMM format
                            
                            # Format the expiration date as MM/YY
                            exp_formatted = f"{exp_date[2:4]}/{exp_date[0:2]}"
                            
                            # Update the UI
                            self.card_number_var.set(f"**** **** **** {card_number[-4:]}" if len(card_number) > 4 else card_number)
                            self.card_holder_var.set(f"{first_name} {last_name}".strip())
                            self.expiry_var.set(exp_formatted)
                except Exception as e:
                    print(f"Error parsing track 1 data: {e}")
            
            # Enable save button
            self.save_btn.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing card data: {str(e)}")
    
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
