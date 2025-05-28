"""
Enhanced Card Database with Secure Storage

Provides a secure database for storing and managing card information
with encryption for sensitive data.
"""
import base64
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from security.secure_storage import get_secure_storage, SecureStorageError
from .card_utils import card_detector

class EnhancedCardDatabase:
    """
    Enhanced card database with secure storage capabilities.
    
    This class provides methods to manage a collection of card data
    with encryption for sensitive information like card numbers,
    expiration dates, and track data.
    """
    
    def __init__(self, file_path: str = None, password: str = None, salt: bytes = None):
        """
        Initialize the database.
        
        Args:
            file_path: Optional path to save/load the database
            password: Optional password for encryption
            salt: Optional salt for key derivation (must provide when loading an existing database)
        """
        self.file_path = file_path
        self.cards = []
        self.secure_storage = None
        self.modified = False  # Track if database has been modified
        self.salt = salt  # Store the salt for later use
        
        # Initialize secure storage if password is provided
        if password:
            self.secure_storage = get_secure_storage(password, salt)
    
    def add_card(self, card_data: Dict[str, Any]) -> bool:
        """
        Add a card to the database.
        
        Args:
            card_data: Dictionary containing card information
            
        Returns:
            bool: True if card was added successfully, False otherwise
        """
        if not card_data or not isinstance(card_data, dict):
            print("Error: Invalid card data")
            return False
            
        try:
            # Make a copy to avoid modifying the original
            card = {}
            
            # Copy all existing fields, ensuring they're strings
            for key, value in card_data.items():
                if value is not None:
                    if isinstance(value, (str, int, float, bool)):
                        card[key] = str(value).strip()
                    else:
                        card[key] = str(value)
            
            # Ensure required fields have at least empty string values
            required_fields = ['number', 'type', 'issuer', 'holder_name', 'expiration', 'notes']
            for field in required_fields:
                if field not in card:
                    card[field] = ''
            
            # Clean the card number (remove all non-digit characters)
            if 'number' in card and card['number']:
                card['number'] = ''.join(c for c in card['number'] if c.isdigit())
            
            # Auto-detect card type and issuer if not provided
            if card.get('number'):
                card_info = card_detector.get_card_type(card['number'])
                
                # Only update type if it's not set or empty
                if not card.get('type'):
                    card['type'] = card_info.get('type', 'Unknown')
                
                # Only update issuer if it's not set or empty
                if not card.get('issuer'):
                    card['issuer'] = card_info.get('issuer', 'Unknown')
                    
                    # If we still don't have an issuer, use the card type
                    if not card['issuer'] or card['issuer'] == 'Unknown':
                        card['issuer'] = card.get('type', 'Unknown')
            
            # Ensure we have at least a card number or holder name for display
            if not card.get('number') and not card.get('holder_name'):
                print("Error: Card must have at least a number or holder name")
                return False
            
            # Debug output
            print("Adding card with data:", {k: v for k, v in card.items() if k != 'number'})
            
            # Encrypt sensitive data if secure storage is available
            if self.secure_storage:
                card = self.secure_storage.encrypt_card(card)
                
            self.cards.append(card)
            self.modified = True
            return True
            
        except Exception as e:
            print(f"Error adding card: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_card(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get a card by index.
        
        Args:
            index: Index of the card to retrieve
            
        Returns:
            Optional[Dict]: The card data or None if not found
        """
        try:
            card = self.cards[index].copy()
            
            # Decrypt data if secure storage is available
            if self.secure_storage:
                card = self.secure_storage.decrypt_card(card)
                
            return card
            
        except (IndexError, KeyError):
            return None
    
    def remove_card(self, index: int) -> bool:
        """
        Remove a card from the database.
        
        Args:
            index: Index of the card to remove
            
        Returns:
            bool: True if card was removed, False otherwise
        """
        try:
            del self.cards[index]
            self.modified = True
            return True
        except IndexError:
            return False
    
    def search_cards(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for cards matching a search term.
        
        Args:
            search_term: Term to search for in card data
            
        Returns:
            List[Dict]: List of matching cards
        """
        results = []
        search_term = search_term.lower()
        
        for card in self.cards:
            # Decrypt card for searching if secure storage is available
            search_card = card
            if self.secure_storage:
                search_card = self.secure_storage.decrypt_card(card)
            
            # Search in relevant fields
            for field, value in search_card.items():
                if field.startswith('_') or not isinstance(value, (str, int, float)):
                    continue
                    
                if search_term in str(value).lower():
                    results.append(search_card)
                    break
        
        return results
    
    def save_to_file(self, file_path: str = None) -> bool:
        """
        Save the database to a file.
        
        Args:
            file_path: Optional path to save the file (uses instance path if not provided)
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        if not file_path and not self.file_path:
            print("Error: No file path provided for saving database")
            return False
            
        file_path = file_path or self.file_path
        
        try:
            # Ensure the directory exists
            try:
                os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            except Exception as e:
                print(f"Error creating directory: {str(e)}")
                return False
            
            # Prepare data for saving
            data = {
                'version': '1.1',  # Bump version to indicate new format with salt
                'secure': self.secure_storage is not None,
                'cards': self.cards
            }
            
            # Save the salt if we have secure storage
            if self.secure_storage and hasattr(self.secure_storage, 'salt'):
                data['salt'] = base64.b64encode(self.secure_storage.salt).decode('utf-8')
            
            # Save to file with error handling
            try:
                temp_file = file_path + '.tmp'
                with open(temp_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                # On Windows, we need to remove the destination file first if it exists
                if os.path.exists(file_path):
                    os.remove(file_path)
                os.rename(temp_file, file_path)
                
                # Reset modified flag after successful save
                self.modified = False
                self.file_path = file_path  # Update the file path in case it changed
                print(f"Successfully saved database to: {file_path}")
                return True
                
            except Exception as e:
                # Clean up temp file if it exists
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                raise  # Re-raise the exception to be caught by the outer try/except
            
        except Exception as e:
            error_msg = f"Error saving database to {file_path}: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str, password: str = None) -> 'EnhancedCardDatabase':
        """
        Load a database from a file.
        
        Args:
            file_path: Path to the database file
            password: Optional password if the database is encrypted
            
        Returns:
            EnhancedCardDatabase: A new instance with loaded data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Database file not found: {file_path}")
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            if not isinstance(data, dict) or 'cards' not in data:
                raise ValueError("Invalid database format")
            
            # Extract salt if it exists
            salt = None
            if 'salt' in data:
                try:
                    salt = base64.b64decode(data['salt'])
                except (ValueError, TypeError):
                    print("Warning: Invalid salt in database, generating new one")
            
            # Create a new instance with the salt
            db = cls(file_path=file_path, password=password, salt=salt)
            db.cards = data.get('cards', [])
            
            # Try to decrypt a card to verify the password
            if db.secure_storage and db.cards:
                try:
                    # Just try to decrypt the first card to verify the password
                    if db.cards[0].get('_secure', False):
                        db.secure_storage.decrypt_card(db.cards[0])
                except Exception as e:
                    raise ValueError("Incorrect password or corrupted database") from e
            
            return db
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in database file: {str(e)}")
    
    def export_to_json(self, file_path: str) -> bool:
        """
        Export the database to a JSON file.
        
        Args:
            file_path: Path to save the JSON file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            # Prepare data for export (decrypt if needed)
            export_data = []
            for card in self.cards:
                if self.secure_storage:
                    export_data.append(self.secure_storage.decrypt_card(card))
                else:
                    export_data.append(card)
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error exporting to JSON: {str(e)}")
            return False
    
    def export_to_csv(self, file_path: str) -> bool:
        """
        Export the database to a CSV file.
        
        Args:
            file_path: Path to save the CSV file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            import csv
            
            with open(file_path, 'w', newline='') as f:
                if not self.cards:
                    return True
                    
                # Get fieldnames from the first card
                fieldnames = list(self.cards[0].keys())
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for card in self.cards:
                    # Decrypt if needed
                    if self.secure_storage:
                        card = self.secure_storage.decrypt_card(card)
                    writer.writerow(card)
                    
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False
            
    def export_to_bytes(self) -> bytes:
        """
        Export the database to bytes.
        
        Returns:
            bytes: The serialized database data
        """
        try:
            # Prepare data for serialization
            data = {
                'version': '1.0',
                'secure': self.secure_storage is not None,
                'cards': self.cards
            }
            
            # Convert to JSON string and then to bytes
            data_str = json.dumps(data, indent=2)
            return data_str.encode('utf-8')
            
        except Exception as e:
            print(f"Error exporting database to bytes: {str(e)}")
            raise
            
    def import_from_bytes(self, data: bytes) -> bool:
        """
        Import database from bytes.
        
        Args:
            data: Bytes containing the database data
            
        Returns:
            bool: True if import was successful, False otherwise
        """
        try:
            # Decode the bytes to a string
            data_str = data.decode('utf-8')
            
            # Parse the JSON data
            db_data = json.loads(data_str)
            
            # Validate the data format
            if not isinstance(db_data, dict) or 'cards' not in db_data:
                raise ValueError("Invalid database format")
            
            # Update the cards
            self.cards = db_data.get('cards', [])
            self.modified = True
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {str(e)}")
            return False
        except Exception as e:
            print(f"Error importing database: {str(e)}")
            return False
