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
        self.root.title("Card Validator")
        
        # Set window size and position
        window_width = 700  # Slightly wider to accommodate both validators
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TNotebook.Tab', padding=[10, 5])
        
        # Create main container
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Setup tabs
        self.setup_validation_tab()
        self.setup_c10_tab()
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
        """Set up the MOD10 credit card validation tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="MOD10 Validator")
        
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
    
    def setup_c10_tab(self):
        """Set up the C10 validation tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="C10 Validator")
        
        # Main container with padding
        container = ttk.Frame(tab, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(
            container,
            text="C10 Validation",
            font=('Helvetica', 14, 'bold')
        )
        title.pack(pady=(0, 15))
        
        # Input frame
        input_frame = ttk.LabelFrame(container, text="Card Number", padding=10)
        input_frame.pack(fill=tk.X, pady=5)
        
        # Card number entry
        self.c10_card_var = tk.StringVar()
        self.c10_card_entry = ttk.Entry(
            input_frame,
            textvariable=self.c10_card_var,
            font=('Courier', 12),
            width=30
        )
        self.c10_card_entry.pack(fill=tk.X, padx=5, pady=5)
        self.c10_card_entry.bind('<KeyRelease>', self.on_c10_input_change)
        
        # Buttons frame
        btn_frame = ttk.Frame(container)
        btn_frame.pack(pady=10)
        
        # Validate button
        validate_btn = ttk.Button(
            btn_frame,
            text="Validate C10",
            command=self.validate_c10,
            style="Accent.TButton"
        )
        validate_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = ttk.Button(
            btn_frame,
            text="Clear",
            command=self.clear_c10_input
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(container, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Results text
        self.c10_results = scrolledtext.ScrolledText(
            results_frame,
            height=8,
            wrap=tk.WORD,
            font=('Consolas', 10),
            state='disabled'
        )
        self.c10_results.pack(fill=tk.BOTH, expand=True)
        
        # Add some padding at the bottom
        ttk.Frame(container, height=10).pack()
    
    def on_c10_input_change(self, event=None):
        """Handle changes in the C10 card number input."""
        # Remove any non-digit characters
        current = self.c10_card_var.get()
        digits = ''.join(filter(str.isdigit, current))
        if current != digits:
            self.c10_card_var.set(digits)
    
    def validate_c10(self):
        """Validate the card number using C10 algorithm."""
        card_number = self.c10_card_var.get().strip()
        
        if not card_number.isdigit():
            self.show_c10_result("Invalid input. Please enter numeric characters only.", is_error=True)
            return
            
        if len(card_number) < 1:
            self.show_c10_result("Please enter a card number.", is_error=True)
            return
            
        try:
            # Implement C10 validation logic here
            # For now, we'll just show a placeholder message
            is_valid = self.is_valid_c10(card_number)
            
            if is_valid:
                self.show_c10_result(f"✅ Valid C10 number: {card_number}")
            else:
                self.show_c10_result(f"❌ Invalid C10 number: {card_number}", is_error=True)
                
        except Exception as e:
            self.show_c10_result(f"Error during validation: {str(e)}", is_error=True)
    
    def is_valid_c10(self, number):
        """
        Validate a number using the C10 algorithm.
        
        Args:
            number (str): The number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Convert to list of integers
            digits = [int(d) for d in str(number)]
            
            # Double every second digit from the right
            for i in range(len(digits) - 2, -1, -2):
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] = (digits[i] // 10) + (digits[i] % 10)
            
            # Sum all digits
            total = sum(digits)
            
            # Check if total is a multiple of 10
            return total % 10 == 0
            
        except Exception as e:
            print(f"Error in C10 validation: {e}")
            return False
    
    def show_c10_result(self, message, is_error=False):
        """Display the validation result in the C10 results box."""
        self.c10_results.config(state='normal')
        self.c10_results.delete(1.0, tk.END)
        
        # Configure tags for styling
        self.c10_results.tag_configure('error', foreground='red')
        self.c10_results.tag_configure('success', foreground='green')
        
        # Insert the message with appropriate tags
        if is_error:
            self.c10_results.insert(tk.END, message, 'error')
        else:
            self.c10_results.insert(tk.END, message, 'success')
            
        self.c10_results.config(state='disabled')
    
    def clear_c10_input(self):
        """Clear the C10 input and results."""
        self.c10_card_var.set('')
        self.show_c10_result("")
        self.c10_card_entry.focus()
    
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
