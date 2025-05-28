"""
Example script demonstrating the card database functionality with multiple card types.
"""

import sys
import os
from typing import Dict, Any, List, Tuple

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card import Card
from track import Track
from database import CardDatabase

def create_test_card(card_type: str) -> Tuple[Card, str]:
    """
    Create a test card with sample track data for the specified card type.
    
    Args:
        card_type: Type of card to create (visa, mastercard, amex, discover, jcb, diners)
        
    Returns:
        Tuple of (Card object, expected card type name)
    """
    from track import Track  # Import Track here to avoid circular imports
    
    # Sample test data for different card types
    test_data = {
        'visa': {
            'track1': "%B4111111111111111^CARDHOLDER/NAME^25121010000000000000?",
            'track2': ";4111111111111111=25121010000000000000?",
            'expected_type': 'Visa'
        },
        'mastercard': {
            'track1': "%B5555555555554444^CARDHOLDER/NAME^25121010000000000?",
            'track2': ";5555555555554444=25121010000000000?",
            'expected_type': 'Mastercard'
        },
        'amex': {
            'track1': "%B378282246310005^CARDHOLDER/NAME^25121010000000000000?",
            'track2': ";378282246310005=25121010000000000000?",
            'expected_type': 'American Express'
        },
        'discover': {
            'track1': "%B6011111111111117^CARDHOLDER/NAME^25121010000000000?",
            'track2': ";6011111111111117=25121010000000000?",
            'expected_type': 'Discover'
        },
        'jcb': {
            'track1': "%B3530111333300000^CARDHOLDER/NAME^25121010000000000?",
            'track2': ";3530111333300000=25121010000000000?",
            'expected_type': 'JCB'
        },
        'diners': {
            'track1': "%B30569309025904^CARDHOLDER/NAME^251210100000000?",
            'track2': ";30569309025904=251210100000000?",
            'expected_type': 'Diners Club'
        }
    }
    
    if card_type not in test_data:
        raise ValueError(f"Unsupported card type: {card_type}")
    
    card = Card()
    track1_data = test_data[card_type]['track1']
    track2_data = test_data[card_type]['track2']
    card_name = test_data[card_type]['expected_type']
    
    # Create Track objects for track1 and track2 with proper initialization
    # Note: The Track constructor expects (data, start_bit, track_number)
    track1 = Track(track1_data.encode('ascii'), 0, 1)  # Track 1
    track2 = Track(track2_data.encode('ascii'), 0, 2)  # Track 2
    
    # Manually set track number as it might be used in the Track class
    track1.track_number = 1
    track2.track_number = 2
    
    # Decode the tracks to extract fields
    track1.decode()
    track2.decode()
    
    # Add tracks to the card using direct dictionary access to ensure they're added correctly
    if not hasattr(card, 'tracks'):
        card.tracks = {}
    
    # Add tracks with their track numbers as keys
    card.tracks[1] = track1
    card.tracks[2] = track2
    
    # Also set track presence if the card class uses it
    if hasattr(card, 'track_presence'):
        card.track_presence = {1: 1, 2: 1}  # 1 means present
    
    # Print debug info
    print("\nCreated card with tracks:")
    print(f"  Track 1: {track1_data}")
    print(f"  Track 2: {track2_data}")
    
    return card, card_name

def test_card_type(db: CardDatabase, card: Card, expected_type: str) -> bool:
    """
    Test if a card is correctly identified by the database.
    
    Args:
        db: CardDatabase instance
        card: Card to test
        expected_type: Expected card type name
        
    Returns:
        bool: True if the card was correctly identified, False otherwise
    """
    # Print detailed card and track information
    print(f"\nTesting {expected_type}...")
    print(f"Card object: {card}")
    print(f"Card type: {type(card)}")
    
    # Print detailed card attributes
    print("\nCard attributes:")
    print("----------------")
    print(f"Tracks dict: {getattr(card, 'tracks', 'No tracks dict')}")
    print(f"Track presence: {getattr(card, 'track_presence', 'No track_presence')}")
    
    # Print track information
    print("\nTrack Information:")
    print("-----------------")
    
    # Check tracks using different methods
    for track_num in [1, 2, 3]:
        print(f"\n--- Track {track_num} ---")
        
        # Method 1: Direct dictionary access
        tracks_dict = getattr(card, 'tracks', {})
        print(f"  Tracks dict has track {track_num}: {track_num in tracks_dict}")
        
        # Method 2: Using get_track method
        track = card.get_track(track_num)
        print(f"  get_track({track_num}): {track is not None}")
        
        if track is not None:
            print(f"  Track type: {type(track)}")
            print(f"  Track attributes: {dir(track)}")
            
            # Try to get characters
            if hasattr(track, 'get_chars'):
                try:
                    chars = track.get_chars()
                    print(f"  get_chars(): {chars} (type: {type(chars)})")
                except Exception as e:
                    print(f"  Error in get_chars(): {str(e)}")
            
            # Check if decoded
            print(f"  Decoded: {getattr(track, 'decoded', 'No decoded attribute')}")
            
            # Try to get fields
            if hasattr(track, 'get_num_fields'):
                try:
                    num_fields = track.get_num_fields()
                    print(f"  Number of fields: {num_fields}")
                    for i in range(num_fields):
                        field = track.get_field(i)
                        print(f"    Field {i+1}: {field}")
                except Exception as e:
                    print(f"  Error getting fields: {str(e)}")
    
    # Run the database tests
    print("\nRunning database tests...")
    result = db.run_tests(card)
    
    if not result.is_valid():
        print(f"\n❌ Failed: No match found for {expected_type}")
        
        # Print debug info about why it might have failed
        print("\nDebug info:")
        print("-----------")
        
        # Check track presence
        print("Track presence:")
        for track_num in [1, 2, 3]:
            status = card.has_track(track_num)
            status_str = "Present" if status == Card.PRESENT else "Missing" if status == Card.MISSING else "Unknown"
            print(f"  Track {track_num}: {status_str}")
        
        # Check if any test matches the requirements
        print("\nAvailable tests and their requirements:")
        for test in db.tests:
            print(f"  - {test.__class__.__name__} requires tracks: {test.required_tracks}")
            
        return False
    
    actual_type = result.get_card_type()
    if actual_type != expected_type:
        print(f"❌ Failed: Expected {expected_type}, got {actual_type}")
        return False
    
    print(f"\n✅ Passed: Correctly identified as {expected_type}")
    print("\nCard details:")
    print("-------------")
    
    # Print card details from the test result
    for i in range(result.get_num_tags()):
        print(f"{result.get_name_tag(i)}: {result.get_data_tag(i)}")
    
    return True

def main():
    # Create a database with all available tests
    print("Initializing card database...")
    db = CardDatabase()
    
    # Test each card type
    print("\nTesting card types:")
    print("==================")
    
    test_cases = [
        ('visa', "Visa"),
        ('mastercard', "Mastercard"),
        ('amex', "American Express"),
        ('discover', "Discover"),
        ('jcb', "JCB"),
        ('diners', "Diners Club")
    ]
    
    results = []
    for card_type, expected_name in test_cases:
        try:
            card, _ = create_test_card(card_type)
            print(f"\nTesting {expected_name}...")
            success = test_card_type(db, card, expected_name)
            results.append((expected_name, success))
        except Exception as e:
            print(f"❌ Error testing {expected_name}: {e}")
            results.append((expected_name, False))
    
    # Print summary
    print("\nTest Summary:")
    print("============")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {name}")
    
    print(f"\n{passed} out of {total} tests passed ({passed/total*100:.1f}%)")
    
    # Print information about available tests
    print("\nAvailable card tests:")
    print("====================")
    for i, test in enumerate(db.get_available_tests(), 1):
        print(f"{i}. {test['name']} (Tracks: {test['required_tracks']})")

if __name__ == "__main__":
    main()
