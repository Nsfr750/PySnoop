"""
Card Storage Module

Provides functionality to store and retrieve card data from a persistent storage.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class CardStorage:
    """Handles persistent storage of card data."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the card storage.
        
        Args:
            db_path: Path to the database file. If None, uses default location.
        """
        if db_path is None:
            # Use default location in user's app data directory
            app_dir = Path(os.getenv('APPDATA') or os.path.expanduser('~')) / 'StripeSnoop'
            app_dir.mkdir(exist_ok=True)
            self.db_path = app_dir / 'cards.json'
        else:
            self.db_path = Path(db_path)
        
        self.cards: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self) -> None:
        """Load cards from the database file."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.cards = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.cards = []
        else:
            self.cards = []
    
    def _save(self) -> None:
        """Save cards to the database file."""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.cards, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving card database: {e}")
    
    def add_card(self, card_data: Dict[str, Any]) -> None:
        """
        Add a new card to the storage.
        
        Args:
            card_data: Dictionary containing card data
        """
        # Add timestamp if not present
        if 'timestamp' not in card_data:
            card_data['timestamp'] = datetime.now().isoformat()
        
        # Add the card to the in-memory list
        self.cards.append(card_data)
        
        # Save to disk
        self._save()
    
    def get_all_cards(self) -> List[Dict[str, Any]]:
        """
        Get all stored cards.
        
        Returns:
            List of card dictionaries
        """
        return self.cards
    
    def clear(self) -> None:
        """Clear all stored cards."""
        self.cards = []
        self._save()
