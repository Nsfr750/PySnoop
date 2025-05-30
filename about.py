"""
About Tab Module for PySnoop

This module contains the About tab implementation for the PySnoop application.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser

# Import version information
from version import get_version_info, __version__


def create_about_tab(parent):
    """
    Create the about tab with application information.
    
    Args:
        parent: The parent widget (notebook) to add the tab to
        
    Returns:
        ttk.Frame: The created tab
    """
    tab = ttk.Frame(parent)
    
    # Main container with padding
    container = ttk.Frame(tab, padding=20)
    container.pack(fill=tk.BOTH, expand=True)
    
    # Application title
    title_label = ttk.Label(
        container,
        text="PySnoop",
        font=('Helvetica', 16, 'bold')
    )
    title_label.pack(pady=(0, 10))
    
    # Version information
    version_info = get_version_info()
    version_text = f"Version {__version__}"
    if version_info['qualifier']:
        version_text += f" ({version_info['qualifier']})"
    
    version_label = ttk.Label(
        container,
        text=version_text,
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
        text="© 2025 Nsfr750",
        font=('Helvetica', 8),
        foreground='gray'
    )
    copyright_label.pack(side=tk.BOTTOM, pady=(10, 0))
    
    # GitHub link
    github_btn = ttk.Button(
        container,
        text="View on GitHub",
        command=lambda: webbrowser.open("https://github.com/Nsfr750/pysnoop")
    )
    github_btn.pack(pady=(20, 0))
    
     # Sourceforge link
    sourceforge_btn = ttk.Button(
        container,
        text="Original Project",
        command=lambda: webbrowser.open("http://stripesnoop.sourceforge.net")
    )
    sourceforge_btn.pack(pady=(20, 0))
    return tab
