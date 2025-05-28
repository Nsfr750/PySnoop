#!/usr/bin/env python3
"""
Card Database Manager

A simple command-line interface for managing a card database.
"""
import os
import sys
from database.enhanced_database import EnhancedCardDatabase
from ui.card_ui import CardDatabaseUI

def main():
    """Main entry point for the Card Database Manager."""
    print("Starting Card Database Manager...")
    
    # Initialize the database
    db = EnhancedCardDatabase()
    
    # Initialize and run the UI
    ui = CardDatabaseUI(db)
    ui.run()
    
    print("Goodbye!")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
        sys.exit(1)
