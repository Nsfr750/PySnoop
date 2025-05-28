"""
Card Database Module

This module provides functionality to save and load card databases to/from files
in various formats (CSV, JSON). It also includes enhanced card validation.
"""
import os
import json
import csv
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

class CardDatabaseExporter:
    """Handles exporting and importing card data to/from different formats."""
    
    @staticmethod
    def to_dict(card) -> Dict[str, Any]:
        """Convert a card object to a dictionary."""
        return {
            'card_type': card.get('card_type', ''),
            'number': card.get('number', ''),
            'expiration': card.get('expiration', ''),
            'holder_name': card.get('holder_name', ''),
            'tracks': {
                str(track_num): track.get_chars() 
                for track_num, track in card.get('tracks', {}).items()
                if hasattr(track, 'get_chars')
            },
            'last_updated': datetime.now().isoformat(),
            'metadata': card.get('metadata', {})
        }
    
    @staticmethod
    def to_csv(cards: List[Dict], file_path: str) -> bool:
        """Export cards to a CSV file."""
        if not cards:
            return False
            
        try:
            fieldnames = ['card_type', 'number', 'expiration', 'holder_name', 'last_updated']
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(cards)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def to_json(cards: List[Dict], file_path: str) -> bool:
        """Export cards to a JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cards, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    @classmethod
    def from_file(cls, file_path: str) -> Optional[List[Dict]]:
        """Import cards from a file (CSV or JSON)."""
        if not os.path.exists(file_path):
            return None
            
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.json':
                return cls._from_json(file_path)
            elif ext == '.csv':
                return cls._from_csv(file_path)
            else:
                print(f"Unsupported file format: {ext}")
                return None
        except Exception as e:
            print(f"Error importing from {file_path}: {e}")
            return None
    
    @staticmethod
    def _from_json(file_path: str) -> List[Dict]:
        """Import cards from a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def _from_csv(file_path: str) -> List[Dict]:
        """Import cards from a CSV file."""
        cards = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cards.append(dict(row))
        return cards
