"""
Card Utilities

This module provides utilities for working with payment cards,
including card type detection based on BIN/IIN ranges.
"""
import os
import csv
from typing import Dict, List, Optional

class CardTypeDetector:
    """Detects card types based on BIN/IIN ranges from CSV files."""
    
    def __init__(self, data_dir: str = None):
        """Initialize the card type detector with data directory."""
        # Try to find the data directory relative to the project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Look for data directory in several possible locations
        possible_paths = [
            os.path.join(project_root, 'data'),
            os.path.join(script_dir, 'data'),
            os.path.join(project_root, '..', 'data'),
            os.path.join(os.path.expanduser('~'), '.card_db_data')
        ]
        
        # Use the first existing path, or the provided data_dir
        self.data_dir = data_dir
        if not self.data_dir:
            for path in possible_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    self.data_dir = path
                    break
        
        if not self.data_dir or not os.path.exists(self.data_dir):
            self.data_dir = project_root  # Fallback to project root
            
        self.bin_ranges = {}
        self._load_bin_ranges()
    
    def _load_bin_ranges(self):
        """Load BIN ranges from CSV files in the data directory."""
        # Map of card type to their respective CSV files and expected columns
        card_type_files = {
            'Visa': {'file': 'visa-pre.csv', 'prefix_col': 0, 'issuer_col': 1},
            'Mastercard': {'file': 'mastercard-pre.csv', 'prefix_col': 0, 'issuer_col': 1},
            'American Express': {'file': 'amex-pre.csv', 'prefix_col': 0, 'issuer_col': 1},
            'Discover': {'file': 'discover-pre.csv', 'prefix_col': 0, 'issuer_col': 1},
        }
        
        total_loaded = 0
        
        for card_type, file_info in card_type_files.items():
            filename = file_info['file']
            prefix_col = file_info['prefix_col']
            issuer_col = file_info.get('issuer_col', -1)  # Default to -1 if not specified
            
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                print(f"Warning: Could not find {filename} in {self.data_dir}")
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    
                    # Skip header if it exists (assume first row is header if it contains non-numeric values)
                    try:
                        first_row = next(reader)
                        if not first_row[0].strip().isdigit():
                            print(f"Skipping header in {filename}")
                        else:
                            # If first row looks like data, rewind to process it
                            f.seek(0)
                            reader = csv.reader(f)
                    except StopIteration:
                        print(f"Warning: Empty file: {filename}")
                        continue
                    
                    file_loaded = 0
                    for row in reader:
                        if not row or not row[0].strip():
                            continue
                            
                        try:
                            # Get prefix and clean it (remove any non-digit characters)
                            prefix = ''.join(c for c in row[prefix_col].strip() if c.isdigit())
                            if not prefix:
                                continue
                                
                            # Get issuer if column exists
                            issuer = row[issuer_col].strip() if issuer_col < len(row) else ''
                            
                            # Store the mapping
                            self.bin_ranges[prefix] = {
                                'type': card_type,
                                'issuer': issuer
                            }
                            file_loaded += 1
                            
                        except IndexError as e:
                            print(f"Warning: Invalid row format in {filename}: {row}")
                            continue
                            
                    total_loaded += file_loaded
                    print(f"Loaded {file_loaded} entries from {filename}")
                    
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"Total BIN ranges loaded: {len(self.bin_ranges)}")
        if not self.bin_ranges:
            print("Warning: No BIN ranges were loaded. Card type detection will not work.")
            print(f"Searched in: {self.data_dir}")
    
    def get_card_type(self, card_number: str) -> Dict[str, str]:
        """
        Get card type and issuer information based on card number.
        
        Args:
            card_number: The card number (can include spaces/dashes)
            
        Returns:
            Dict with 'type' and 'issuer' keys
        """
        if not card_number or not isinstance(card_number, str):
            return {'type': 'Unknown', 'issuer': 'Invalid card number'}
            
        # Clean the card number (remove all non-digit characters)
        clean_number = ''.join(c for c in str(card_number) if c.isdigit())
        
        if not clean_number:
            return {'type': 'Unknown', 'issuer': 'No card number provided'}
            
        if len(clean_number) < 4:
            return {'type': 'Unknown', 'issuer': 'Card number too short'}
            
        # Check for matches with decreasing prefix lengths (from 6 digits down to 1)
        for prefix_length in range(min(6, len(clean_number)), 0, -1):
            prefix = clean_number[:prefix_length]
            if prefix in self.bin_ranges:
                result = self.bin_ranges[prefix].copy()
                # If we have a match but no issuer, try to find a better match
                if not result.get('issuer'):
                    # Look for a longer prefix with issuer info
                    for longer_length in range(prefix_length + 1, min(8, len(clean_number) + 1)):
                        longer_prefix = clean_number[:longer_length]
                        if longer_prefix in self.bin_ranges and self.bin_ranges[longer_prefix].get('issuer'):
                            result['issuer'] = self.bin_ranges[longer_prefix]['issuer']
                            break
                return result
                
        # If we get here, no match was found
        # Try to guess based on first digit (as a fallback)
        first_digit = clean_number[0]
        if first_digit == '4':
            return {'type': 'Visa', 'issuer': 'Unknown'}
        elif first_digit == '5':
            return {'type': 'Mastercard', 'issuer': 'Unknown'}
        elif first_digit == '3':
            if len(clean_number) >= 2 and clean_number[1] in ['4', '7']:
                return {'type': 'American Express', 'issuer': 'Unknown'}
            return {'type': 'Other', 'issuer': 'Unknown'}
        elif first_digit == '6':
            return {'type': 'Discover', 'issuer': 'Unknown'}
            
        return {'type': 'Unknown', 'issuer': 'Unknown'}
    
    def get_supported_card_types(self) -> List[str]:
        """Get a list of all supported card types."""
        return sorted({info['type'] for info in self.bin_ranges.values()})

# Singleton instance for convenience
card_detector = CardTypeDetector()

def detect_card_type(card_number: str) -> Dict[str, str]:
    """
    Detect card type and issuer for the given card number.
    
    Args:
        card_number: The card number to check
        
    Returns:
        Dict with 'type' and 'issuer' keys
    """
    return card_detector.get_card_type(card_number)
