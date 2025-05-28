"""
Tests for the database and card type detection
"""
import pytest
from card import Card
from track import Track
from database import CardDatabase
from database.test_result import TestResult

def test_visa_detection():
    """Test detection of Visa cards"""
    db = CardDatabase()
    card = Card()
    
    # Create a track with Visa card data
    track_data = b';4123456789012345=25051010000000000000?'
    track = Track(track_data, 2)
    card.add_track(track)
    
    # Run tests
    result = db.run_tests(card)
    
    assert result.is_valid()
    assert "Visa" in result.card_type

def test_mastercard_detection():
    """Test detection of Mastercard cards"""
    db = CardDatabase()
    card = Card()
    
    # Create a track with Mastercard data
    track_data = b';5123456789012345=25051010000000000000?'
    track = Track(track_data, 2)
    card.add_track(track)
    
    # Run tests
    result = db.run_tests(card)
    
    assert result.is_valid()
    assert "Mastercard" in result.card_type

def test_amex_detection():
    """Test detection of American Express cards"""
    db = CardDatabase()
    card = Card()
    
    # Create a track with AmEx data
    track_data = b';341234567890123=250510100000000000000000000000000000?'
    track = Track(track_data, 2)
    card.add_track(track)
    
    # Run tests
    result = db.run_tests(card)
    
    assert result.is_valid()
    assert "American Express" in result.card_type

def test_discover_detection():
    """Test detection of Discover cards"""
    db = CardDatabase()
    card = Card()
    
    # Create a track with Discover data
    track_data = b';6011111111111117=25051010000000000000?'
    track = Track(track_data, 2)
    card.add_track(track)
    
    # Run tests
    result = db.run_tests(card)
    
    assert result.is_valid()
    assert "Discover" in result.card_type

def test_jcb_detection():
    """Test detection of JCB cards"""
    db = CardDatabase()
    card = Card()
    
    # Create a track with JCB data
    track_data = b';3530111333300000=25051010000000000000?'
    track = Track(track_data, 2)
    card.add_track(track)
    
    # Run tests
    result = db.run_tests(card)
    
    assert result.is_valid()
    assert "JCB" in result.card_type

def test_diners_club_detection():
    """Test detection of Diners Club cards"""
    db = CardDatabase()
    card = Card()
    
    # Create a track with Diners Club data
    track_data = b';30569309025904=25051010000000000000?'
    track = Track(track_data, 2)
    card.add_track(track)
    
    # Run tests
    result = db.run_tests(card)
    
    assert result.is_valid()
    assert "Diners Club" in result.card_type

def test_unknown_card():
    """Test with an unknown card type"""
    db = CardDatabase()
    card = Card()
    
    # Create a track with invalid card data
    track_data = b';9999999999999999=99123100000000000000?'
    track = Track(track_data, 2)
    card.add_track(track)
    
    # Run tests
    result = db.run_tests(card)
    
    # Should not be valid (no matching card type)
    assert not result.is_valid()

def test_card_with_multiple_tracks():
    """Test card with multiple tracks"""
    db = CardDatabase()
    card = Card()
    
    # Add track 1 and 2
    track1 = Track(b'%B4123456789012345^DOE/JOHN^25051010000000000000000000000000000?', 1)
    track2 = Track(b';4123456789012345=25051010000000000000?', 2)
    
    card.add_track(track1)
    card.add_track(track2)
    
    # Run tests
    result = db.run_tests(card)
    
    assert result.is_valid()
    assert "Visa" in result.card_type
