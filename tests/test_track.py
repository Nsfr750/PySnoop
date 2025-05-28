"""
Tests for the Track class
"""
import pytest
from track import Track

def test_track_initialization():
    """Test Track initialization with bytes"""
    track = Track(b'%B1234567890123456^DOE/JOHN^25051010000000000000000000000000000?', 1)
    assert track.number == 1
    assert not track.decoded
    assert track.char_set == Track.NONE
    assert track.characters == ""
    assert track.fields == []
    assert track.field_buffer == ""

def test_set_chars():
    """Test setting track characters directly"""
    track = Track(b'', 1)
    track.set_chars("TEST123", 7)
    assert track.characters == "TEST123"
    assert track.decoded

def test_decode_alpha():
    """Test decoding alphanumeric track data"""
    # Standard track 1 format: %B<pan>^<name>^<expiry>...
    track_data = b'%B1234567890123456^DOE/JOHN^25051010000000000000000000000000000?'
    track = Track(track_data, 1)
    track.decode()
    
    assert track.decoded
    assert track.char_set == Track.ALPHANUMERIC
    assert track.characters.startswith("%B1234567890123456^DOE/JOHN^2505")
    
    # Should have extracted fields
    assert track.get_num_fields() > 0
    assert track.get_field(0) == "B1234567890123456"  # PAN
    assert track.get_field(1) == "DOE/JOHN"  # Name
    assert track.get_field(2).startswith("2505")  # Expiry

def test_decode_bcd():
    """Test decoding BCD track data (typically track 2)"""
    # Standard track 2 format: ;<pan>=<expiry>...
    track_data = b';1234567890123456=25051010000000000000?'
    track = Track(track_data, 2)
    track.decode()
    
    assert track.decoded
    assert track.char_set == Track.NUMERIC
    assert track.characters.startswith(";1234567890123456=2505")
    
    # Should have extracted fields
    assert track.get_num_fields() > 0
    assert track.get_field(0) == "1234567890123456"  # PAN
    assert track.get_field(1).startswith("2505")  # Expiry

def test_extract_fields():
    """Test field extraction from track data"""
    track = Track(b'', 1)
    track.characters = "FIELD1^FIELD2^FIELD3"
    track._extract_fields()
    
    assert track.get_num_fields() == 3
    assert track.get_field(0) == "FIELD1"
    assert track.get_field(1) == "FIELD2"
    assert track.get_field(2) == "FIELD3"

def test_to_dict():
    """Test converting track to dictionary"""
    track = Track(b'%B1234567890123456^DOE/JOHN^25051010000000000000000000000000000?', 1)
    track.decode()
    
    track_dict = track.to_dict()
    
    assert track_dict['number'] == 1
    assert track_dict['char_set'] == Track.ALPHANUMERIC
    assert track_dict['characters'].startswith("%B1234567890123456^DOE/JOHN^2505")
    assert 'fields' in track_dict
    assert len(track_dict['fields']) > 0
