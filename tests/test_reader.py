"""
Tests for the Reader classes
"""
import pytest
from unittest.mock import patch, MagicMock
from reader import Reader, DirectReader, SerialReader, load_config
from card import Card
from track import Track
import os

# Sample XML configuration for testing
SAMPLE_CONFIG = """<?xml version="1.0"?>
<reader>
    <name>Test Reader</name>
    <type>direct</type>
    <port>0x378</port>
    <tracks>
        <track number="1">
            <clock>2</clock>
            <data>3</data>
        </track>
        <track number="2">
            <clock>4</clock>
            <data>5</data>
        </track>
    </tracks>
</reader>
"""

SAMPLE_SERIAL_CONFIG = """<?xml version="1.0"?>
<reader>
    <name>Test Serial Reader</name>
    <type>serial</type>
    <device>/dev/ttyUSB0</device>
    <tracks>
        <track number="1" start="%" end="?" />
        <track number="2" start=";" end="?" />
    </tracks>
</reader>
"""

class TestBaseReader:
    """Base test class for reader tests"""
    
    def test_reader_initialization(self):
        """Test base reader initialization"""
        reader = Reader("Test Reader")
        assert reader.name == "Test Reader"
        assert not reader.initialized
        assert not reader.verbose
        assert reader.readable_tracks == []
    
    def test_set_verbose(self):
        """Test setting verbose mode"""
        reader = Reader()
        reader.set_verbose(True)
        assert reader.verbose
        reader.set_verbose(False)
        assert not reader.verbose
    
    def test_track_management(self):
        """Test track management methods"""
        reader = Reader()
        
        # Test adding readable tracks
        reader.set_can_read_track(1)
        reader.set_can_read_track(2)
        assert reader.can_read_track(1)
        assert reader.can_read_track(2)
        assert not reader.can_read_track(3)
        
        # Test duplicate handling
        reader.set_can_read_track(1)  # Should not add duplicate
        assert len(reader.readable_tracks) == 2

class TestDirectReader:
    """Tests for DirectReader class"""
    
    def test_direct_reader_initialization(self):
        """Test direct reader initialization"""
        reader = DirectReader(port=0x378, cp=1, clk1=2, data1=3, 
                            clk2=4, data2=5, clk3=6, data3=7)
        
        assert reader.port == 0x378
        assert reader.cp == 1
        assert reader.clk1 == 2
        assert reader.data1 == 3
        assert reader.clk2 == 4
        assert reader.data2 == 5
        assert reader.clk3 == 6
        assert reader.data3 == 7
        assert reader.uses_cp
        
        # Should be able to read all tracks
        assert reader.can_read_track(1)
        assert reader.can_read_track(2)
        assert reader.can_read_track(3)
    
    @patch('reader.DirectReader.init_reader')
    def test_init_reader(self, mock_init):
        """Test reader initialization"""
        reader = DirectReader()
        reader.init_reader()
        assert mock_init.called
    
    @patch('reader.DirectReader.read')
    def test_read_card(self, mock_read):
        """Test reading a card"""
        # Setup mock
        mock_card = MagicMock(spec=Card)
        mock_read.return_value = mock_card
        
        # Test read
        reader = DirectReader()
        card = reader.read()
        
        assert card is mock_card
        mock_read.assert_called_once()

class TestSerialReader:
    """Tests for SerialReader class"""
    
    def test_serial_reader_initialization(self):
        """Test serial reader initialization"""
        reader = SerialReader("/dev/ttyUSB0")
        
        assert reader.device == "/dev/ttyUSB0"
        assert reader.file_handle is None
        assert not reader.flag_cr
        
        # No tracks readable by default
        assert not reader.can_read_track(1)
        assert not reader.can_read_track(2)
        assert not reader.can_read_track(3)
    
    @patch('serial.Serial')
    def test_init_reader(self, mock_serial):
        """Test serial reader initialization"""
        mock_port = MagicMock()
        mock_serial.return_value = mock_port
        
        reader = SerialReader("/dev/ttyUSB0")
        assert reader.init_reader()
        
        mock_serial.assert_called_once_with(
            port="/dev/ttyUSB0",
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=1
        )
    
    @patch('serial.Serial')
    def test_read_card(self, mock_serial):
        """Test reading a card from serial"""
        # Setup mock
        mock_port = MagicMock()
        mock_port.read_until.return_value = b";1234567890123456=25051010000000000000?"
        mock_serial.return_value = mock_port
        
        reader = SerialReader("/dev/ttyUSB0")
        reader.set_can_read_track(2)  # Mark track 2 as readable
        
        card = reader.read()
        
        assert card is not None
        track = card.get_track(2)
        assert track is not None
        assert ";1234567890123456=25051010000000000000?" in track.get_chars()

def test_load_config_direct(tmp_path):
    """Test loading a direct reader config from file"""
    # Create a temporary config file
    config_file = tmp_path / "test_config.xml"
    config_file.write_text(SAMPLE_CONFIG)
    
    # Load the config
    reader = load_config(str(config_file))
    
    # Verify the reader was created correctly
    assert reader is not None
    assert reader.name == "Test Reader"
    assert reader.port == 0x378
    assert reader.can_read_track(1)
    assert reader.can_read_track(2)
    assert not reader.can_read_track(3)

def test_load_config_serial(tmp_path):
    """Test loading a serial reader config from file"""
    # Create a temporary config file
    config_file = tmp_path / "test_serial_config.xml"
    config_file.write_text(SAMPLE_SERIAL_CONFIG)
    
    # Load the config
    reader = load_config(str(config_file))
    
    # Verify the reader was created correctly
    assert reader is not None
    assert reader.name == "Test Serial Reader"
    assert reader.device == "/dev/ttyUSB0"
    assert reader.can_read_track(1)
    assert reader.can_read_track(2)
    assert not reader.can_read_track(3)
