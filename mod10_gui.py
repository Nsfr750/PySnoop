#!/usr/bin/env python3
"""
mod10_gui.py - GUI for Luhn algorithm (mod 10) credit card validation and generation

This module provides a graphical user interface for the mod10.py module,
allowing users to validate credit card numbers and generate valid ones.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import re
from typing import Optional

# Import the mod10 module
from mod10 import mod10_check, generate_credit_card

class Mod10GUI:
    """Main application window for the Mod10 GUI."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Luhn Algorithm Tool")
        self.root.geometry("500x400")
        self.root.minsize(450, 350)
        
        # Set application icon if available
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass  # Use default icon if file not found
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.setup_validation_tab()
        self.setup_generation_tab()
        self.setup_about_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def setup_validation_tab(self):
        """Set up the credit card validation tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Validate Card")
        
        # Main container with padding
        container = ttk.Frame(tab, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(
            container, 
            text="Enter a credit card number to validate:",
            font=('Arial', 10, 'bold')
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Card number entry
        entry_frame = ttk.Frame(container)
        entry_frame.pack(fill=tk.X, pady=5)
        
        self.card_entry = ttk.Entry(entry_frame, font=('Arial', 12))
        self.card_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.card_entry.bind('<Return>', lambda e: self.validate_card())
        
        validate_btn = ttk.Button(
            entry_frame, 
            text="Validate", 
            command=self.validate_card,
            style="Accent.TButton"
        )
        validate_btn.pack(side=tk.RIGHT)
        
        # Result display
        self.result_frame = ttk.LabelFrame(container, text="Result", padding=10)
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.result_text = ttk.Label(
            self.result_frame, 
            text="Enter a card number and click 'Validate'",
            justify=tk.CENTER,
            font=('Arial', 12)
        )
        self.result_text.pack(expand=True)
    
    def setup_generation_tab(self):
        """Set up the credit card generation tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Generate Card")
        
        # Main container with padding
        container = ttk.Frame(tab, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Length selection
        length_frame = ttk.Frame(container)
        length_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(length_frame, text="Card length:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.length_var = tk.StringVar(value="16")
        length_combo = ttk.Combobox(
            length_frame, 
            textvariable=self.length_var,
            values=[str(i) for i in range(12, 21)],  # Common card lengths
            state='readonly',
            width=5
        )
        length_combo.pack(side=tk.LEFT)
        
        # Generate button
        generate_btn = ttk.Button(
            container, 
            text="Generate Card Number", 
            command=self.generate_card,
            style="Accent.TButton"
        )
        generate_btn.pack(pady=(0, 15))
        
        # Generated card display
        self.generated_card_var = tk.StringVar()
        
        card_frame = ttk.Frame(container, padding=10, style='Card.TFrame')
        card_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            card_frame, 
            text="Generated Card:",
            font=('Arial', 9, 'bold')
        ).pack(anchor=tk.W)
        
        self.generated_card_display = ttk.Label(
            card_frame, 
            textvariable=self.generated_card_var,
            font=('Consolas', 12, 'bold'),
            foreground='#0066cc'
        )
        self.generated_card_display.pack(anchor=tk.W, pady=(5, 0))
        
        # Copy button
        copy_btn = ttk.Button(
            container,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard,
            state=tk.DISABLED
        )
        copy_btn.pack(pady=(5, 0))
        self.copy_btn = copy_btn
    
    def setup_about_tab(self):
        """Set up the about tab with information about the Luhn algorithm."""
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
        content = ttk.Frame(scrollable_frame, padding=10)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            content, 
            text="Luhn Algorithm Tool",
            font=('Arial', 16, 'bold')
        ).pack(pady=(0, 10))
        
        # Description
        about_text = """
        This tool implements the Luhn algorithm (also known as the "modulus 10" or "mod 10" algorithm), 
        which is widely used to validate a variety of identification numbers, 
        especially credit card numbers.
        
        Features:
        • Validate credit card numbers
        • Generate valid credit card numbers
        • Simple, intuitive interface
        
        The Luhn algorithm works by processing the digits of a number in a specific way to determine 
        if it's a valid number according to the algorithm's rules. It's not a cryptographically 
        secure hash function, but it's useful for detecting common errors like single-digit errors 
        or simple transpositions of adjacent digits.
        
        Note: This tool is for educational purposes only. Generated card numbers are not real 
        and should not be used for any fraudulent activities.
        """
        
        about_label = ttk.Label(
            content,
            text=about_text,
            justify=tk.LEFT,
            wraplength=450
        )
        about_label.pack(anchor=tk.W, fill=tk.X, pady=5)
        
        # Version and author
        ttk.Label(
            content,
            text="\nVersion 1.0.0\n© 2023 Luhn Algorithm Tool",
            font=('Arial', 8),
            foreground='gray'
        ).pack(side=tk.BOTTOM, pady=10)
    
    def validate_card(self):
        """Validate the entered credit card number."""
        card_number = self.card_entry.get().strip()
        
        if not card_number:
            self.show_result("Please enter a credit card number", "warning")
            return
        
        # Remove any non-digit characters
        card_digits = ''.join(filter(str.isdigit, card_number))
        
        if not card_digits:
            self.show_result("Invalid card number format", "error")
            return
        
        # Format the card number with spaces for better readability
        formatted_number = ' '.join([card_digits[i:i+4] for i in range(0, len(card_digits), 4)])
        
        if mod10_check(card_digits):
            # Check card type based on first digits
            card_type = self.detect_card_type(card_digits)
            self.show_result(
                f"✓ Valid {card_type}\n{formatted_number}", 
                "success"
            )
        else:
            self.show_result(
                f"✗ Invalid card number\n{formatted_number}",
                "error"
            )
    
    def generate_card(self):
        """Generate a valid credit card number."""
        try:
            length = int(self.length_var.get())
            if length < 4 or length > 30:  # Reasonable limits
                raise ValueError("Card length must be between 4 and 30 digits")
                
            card_number = generate_credit_card(length)
            
            # Format with spaces for better readability
            formatted_number = ' '.join([card_number[i:i+4] for i in range(0, len(card_number), 4)])
            
            self.generated_card_var.set(formatted_number)
            self.copy_btn.config(state=tk.NORMAL)
            self.status_var.set(f"Generated {length}-digit card number")
            
            # Switch to the generation tab if not already there
            self.notebook.select(1)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def copy_to_clipboard(self):
        """Copy the generated card number to the clipboard."""
        card_number = self.generated_card_var.get()
        if card_number:
            # Remove spaces for the actual card number
            card_digits = card_number.replace(" ", "")
            self.root.clipboard_clear()
            self.root.clipboard_append(card_digits)
            self.status_var.set("Card number copied to clipboard")
    
    def show_result(self, message: str, result_type: str = "info"):
        """
        Display the validation result.
        
        Args:
            message: The message to display
            result_type: One of "success", "error", "warning", "info"
        """
        # Update status bar
        self.status_var.set("Validation complete")
        
        # Set colors based on result type
        colors = {
            "success": "#2e7d32",  # Dark green
            "error": "#c62828",    # Dark red
            "warning": "#f9a825",   # Dark yellow
            "info": "#1565c0"       # Dark blue
        }
        
        self.result_text.config(
            text=message,
            foreground=colors.get(result_type, "black")
        )
    
    @staticmethod
    def detect_card_type(card_number: str) -> str:
        """
        Detect the card type based on the card number.
        
        Args:
            card_number: The credit card number (digits only)
            
        Returns:
            str: The detected card type or "Credit/Debit Card" if unknown
        """
        card_types = {
            '4': 'Visa',
            '5[1-5]': 'Mastercard',
            '3[47]': 'American Express',
            '3(?:0[0-5]|[68]\d)': 'Diners Club',
            '6(?:011|5\d{2})': 'Discover',
            '35\d{2}': 'JCB',
            '22\d{2}': 'Mir',
            '62': 'UnionPay',
            '9792': 'Troy',
            '3(?:0[0-5]|3\d)': 'Diners Club',
        }
        
        for pattern, card_type in card_types.items():
            if re.match(f'^{pattern}', card_number):
                return card_type
        
        return "Credit/Debit Card"

def main():
    """Main entry point for the application."""
    root = tk.Tk()
    
    # Set a theme if available
    try:
        import ttkthemes
        style = ttkthemes.ThemedStyle(root)
        style.set_theme("arc")  # Try a nice theme if available
    except ImportError:
        # Fall back to default theme
        style = ttk.Style()
        style.configure("Accent.TButton", font=('Arial', 10, 'bold'))
    
    # Configure styles
    style.configure('Card.TFrame', background='#f5f5f5', relief=tk.SOLID, borderwidth=1)
    
    app = Mod10GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
