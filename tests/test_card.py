"""
Tests for the Card class
"""
import pytest
from card import Card
from track import Track

def test_card_initialization():
    """Test Card initialization"""
    card = Card()
    assert len(card.tracks) == 0
    assert len(card.track_presence) == 0

def test_add_track():
    """Test adding tracks to a card"""
    card = Card()
    track1 = Track(b'%B1234567890123456^DOE/JOHN^25051010000000000000000000000000000?', 1)
    track2 = Track(b';1234567890123456=25051010000000000000?', 2)
    
    # Add tracks
    card.add_track(track1)
    card.add_track(track2)
    
    # Verify tracks were added
    assert len(card.tracks) == 2
    assert card.has_track(1) == Card.PRESENT
    assert card.has_track(2) == Card.PRESENT
    assert card.has_track(3) == Card.UNKNOWN  # Not added yet
    
    # Test getting tracks
    assert card.get_track(1) == track1
    assert card.get_track(2) == track2
    assert card.get_track(3) is None  # Doesn't exist

def test_add_missing_track():
    """Test marking tracks as missing"""
    card = Card()
    
    # Mark track 3 as missing
    card.add_missing_track(3)
    assert card.has_track(3) == Card.MISSING
    
    # Shouldn't be able to add a track that's marked as missing
    track3 = Track(b';1234567890123456=25051010000000000000?', 3)
    card.add_track(track3)
    assert card.has_track(3) == Card.PRESENT  # Should override missing

def test_decode_tracks():
    """Test decoding all tracks on a card"""
    card = Card()
    track1 = Track(b'%B1234567890123456^DOE/JOHN^25051010000000000000000000000000000?', 1)
    track2 = Track(b';1234567890123456=25051010000000000000?', 2)
    
    card.add_track(track1)
    card.add_track(track2)
    
    # Initially not decoded
    assert not track1.decoded
    assert not track2.decoded
    
    # Decode all tracks
    card.decode_tracks()
    
    # Should be decoded now
    assert track1.decoded
    assert track2.decoded

def test_to_dict():
    """Test converting card to dictionary"""
    card = Card()
    track1 = Track(b'%B1234567890123456^DOE/JOHN^25051010000000000000000000000000000?', 1)
    track2 = Track(b';1234567890123456=25051010000000000000?', 2)
    
    card.add_track(track1)
    card.add_track(track2)
    card.add_missing_track(3)  # Mark track 3 as missing
    
    card_dict = card.to_dict()
    
    assert 'tracks' in card_dict
    assert 'track_presence' in card_dict
    assert len(card_dict['tracks']) == 2
    assert card_dict['track_presence'] == {1: 1, 2: 1, 3: 2}  # 1=PRESENT, 2=MISSING
