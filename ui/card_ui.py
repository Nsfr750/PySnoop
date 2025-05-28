"""
Card Database UI Module

Provides a text-based user interface for interacting with the card database.
"""
import os
import json
import csv
from typing import List, Dict, Optional, Any
from datetime import datetime

class CardDatabaseUI:
    """Text-based UI for card database operations."""
    
    def __init__(self, db):
        self.db = db
        self.running = True
        self.menu_options = {
            '1': ('View all cards', self.view_all_cards),
            '2': ('Add new card', self.add_card),
            '3': ('Search cards', self.search_cards),
            '4': ('Export cards', self.export_cards),
            '5': ('Import cards', self.import_cards),
            '6': ('Save database', self.save_database),
            '7': ('Load database', self.load_database),
            '0': ('Exit', self.exit_program)
        }
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_menu(self):
        """Display the main menu."""
        self.clear_screen()
        print("=== Card Database Manager ===\n")
        print(f"Database: {getattr(self.db, 'file_path', 'No file loaded')}")
        print(f"Cards in database: {len(getattr(self.db, 'cards', []))}\n")
        
        for key, (description, _) in sorted(self.menu_options.items()):
            print(f"{key}. {description}")
        print()
    
    def run(self):
        """Run the main UI loop."""
        while self.running:
            self.display_menu()
            choice = input("Enter your choice: ").strip()
            
            if choice in self.menu_options:
                self.menu_options[choice][1]()
            else:
                print("\nInvalid choice. Please try again.")
                input("\nPress Enter to continue...")
    
    def view_all_cards(self):
        """Display all cards in the database."""
        self.clear_screen()
        print("=== All Cards ===\n")
        
        cards = getattr(self.db, 'cards', [])
        if not cards:
            print("No cards in database.")
        else:
            for i, card in enumerate(cards, 1):
                card_num = card.get('number', 'N/A')
                card_type = card.get('card_type', 'Unknown')
                print(f"{i}. {card_num} - {card_type}")
        
        input("\nPress Enter to return to menu...")
    
    def add_card(self):
        """Add a new card to the database."""
        self.clear_screen()
        print("=== Add New Card ===\n")
        
        if not hasattr(self.db, 'cards'):
            self.db.cards = []
        
        card = {}
        card['number'] = input("Card number: ").strip()
        card['card_type'] = input("Card type (Visa/Mastercard/etc): ").strip()
        card['expiration'] = input("Expiration (MM/YY): ").strip()
        card['holder_name'] = input("Cardholder name: ").strip()
        card['tracks'] = {}
        
        # Add track data if available
        for track_num in [1, 2, 3]:
            track_data = input(f"Track {track_num} data (leave empty to skip): ").strip()
            if track_data:
                card['tracks'][str(track_num)] = track_data
        
        self.db.cards.append(card)
        print("\nCard added successfully!")
        input("\nPress Enter to return to menu...")
    
    def search_cards(self):
        """Search for cards in the database."""
        self.clear_screen()
        print("=== Search Cards ===\n")
        
        search_term = input("Enter search term: ").lower().strip()
        if not search_term:
            print("No search term provided.")
            input("\nPress Enter to return to menu...")
            return
        
        results = []
        for card in getattr(self.db, 'cards', []):
            if (search_term in card.get('number', '').lower() or
                search_term in card.get('holder_name', '').lower() or
                search_term in card.get('card_type', '').lower()):
                results.append(card)
        
        print(f"\nFound {len(results)} matching cards:")
        for i, card in enumerate(results, 1):
            print(f"{i}. {card.get('number', 'N/A')} - {card.get('holder_name', 'N/A')}")
        
        input("\nPress Enter to return to menu...")
    
    def export_cards(self):
        """Export cards to a file."""
        self.clear_screen()
        print("=== Export Cards ===\n")
        
        cards = getattr(self.db, 'cards', [])
        if not cards:
            print("No cards to export.")
            input("\nPress Enter to return to menu...")
            return
        
        print("Export format:")
        print("1. JSON")
        print("2. CSV")
        print("0. Cancel\n")
        
        choice = input("Select format (1-2, 0 to cancel): ").strip()
        
        if choice == '0':
            return
        elif choice not in ['1', '2']:
            print("Invalid choice.")
            input("\nPress Enter to return to menu...")
            return
        
        file_ext = '.json' if choice == '1' else '.csv'
        default_name = f"cards_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
        file_path = input(f"\nEnter output file path [{default_name}]: ").strip() or default_name
        
        try:
            if choice == '1':
                with open(file_path, 'w') as f:
                    json.dump(cards, f, indent=2)
            else:
                fieldnames = ['number', 'card_type', 'expiration', 'holder_name']
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                    writer.writeheader()
                    writer.writerows(cards)
            
            print(f"\nSuccessfully exported {len(cards)} cards to {file_path}")
        except Exception as e:
            print(f"\nExport failed: {e}")
        
        input("\nPress Enter to return to menu...")
    
    def import_cards(self):
        """Import cards from a file."""
        self.clear_screen()
        print("=== Import Cards ===\n")
        
        file_path = input("Enter file path to import from: ").strip()
        if not file_path or not os.path.exists(file_path):
            print("File not found.")
            input("\nPress Enter to return to menu...")
            return
        
        try:
            if file_path.lower().endswith('.json'):
                with open(file_path, 'r') as f:
                    imported_cards = json.load(f)
            elif file_path.lower().endswith('.csv'):
                with open(file_path, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    imported_cards = list(reader)
            else:
                print("Unsupported file format. Please use .json or .csv")
                input("\nPress Enter to return to menu...")
                return
            
            if not hasattr(self.db, 'cards'):
                self.db.cards = []
            
            self.db.cards.extend(imported_cards)
            print(f"\nSuccessfully imported {len(imported_cards)} cards.")
            
        except Exception as e:
            print(f"\nImport failed: {e}")
        
        input("\nPress Enter to return to menu...")
    
    def save_database(self):
        """Save the current database to a file."""
        self.clear_screen()
        print("=== Save Database ===\n")
        
        if not hasattr(self.db, 'file_path') or not self.db.file_path:
            self.db.file_path = input("Enter file path to save to: ").strip()
        
        try:
            with open(self.db.file_path, 'w') as f:
                json.dump({
                    'cards': getattr(self.db, 'cards', []),
                    'last_updated': datetime.now().isoformat(),
                    'version': '1.0'
                }, f, indent=2)
            
            print(f"\nDatabase saved to {self.db.file_path}")
        except Exception as e:
            print(f"\nSave failed: {e}")
        
        input("\nPress Enter to return to menu...")
    
    def load_database(self):
        """Load a database from a file."""
        self.clear_screen()
        print("=== Load Database ===\n")
        
        file_path = input("Enter file path to load: ").strip()
        if not file_path or not os.path.exists(file_path):
            print("File not found.")
            input("\nPress Enter to return to menu...")
            return
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, dict) or 'cards' not in data:
                print("Invalid database format.")
                input("\nPress Enter to return to menu...")
                return
            
            self.db.cards = data.get('cards', [])
            self.db.file_path = file_path
            
            print(f"\nDatabase loaded from {file_path}")
            print(f"Loaded {len(self.db.cards)} cards.")
            
        except Exception as e:
            print(f"\nLoad failed: {e}")
        
        input("\nPress Enter to return to menu...")
    
    def exit_program(self):
        """Exit the program."""
        self.clear_screen()
        print("Exiting Card Database Manager...")
        self.running = False
