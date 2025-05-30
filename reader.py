"""
Reader classes for different types of magstripe card readers
"""

import sys
import os
from typing import List, Optional, Dict, Any, Type
from abc import ABC, abstractmethod
from xml.etree import ElementTree as ET

# MSR605 reader will be imported dynamically to avoid circular imports
MSR605Reader = None
def import_msr605_reader():
    global MSR605Reader
    if MSR605Reader is None:
        from msr605_reader import MSR605Reader as MSR605
        MSR605Reader = MSR605
    return MSR605Reader

class Reader(ABC):
    """
    Abstract base class for all card readers
    """
    
    def __init__(self, name: str = ""):
        """
        Initialize a new Reader instance
        
        Args:
            name: Optional name for the reader
        """
        self.name = name
        self.interface = 0
        self.readable_tracks: List[int] = []
        self.initialized = False
        self.verbose = False
    
    def set_verbose(self, verbose: bool) -> None:
        """
        Set verbose output
        
        Args:
            verbose: Enable or disable verbose output
        """
        self.verbose = verbose
    
    def can_read_track(self, track_num: int) -> bool:
        """
        Check if this reader can read a specific track
        
        Args:
            track_num: Track number to check
            
        Returns:
            bool: True if the reader can read the specified track
        """
        return track_num in self.readable_tracks
    
    def set_can_read_track(self, track_num: int) -> None:
        """
        Set whether this reader can read a specific track
        
        Args:
            track_num: Track number to set
        """
        if track_num not in self.readable_tracks:
            self.readable_tracks.append(track_num)
    
    @abstractmethod
    def init_reader(self) -> bool:
        """
        Initialize the reader hardware
        
        Returns:
            bool: True if initialization was successful
        """
        pass
    
    @abstractmethod
    def read(self):
        """
        Read a card
        
        Returns:
            Card: The card that was read
        """
        pass
    
    @abstractmethod
    def read_raw(self) -> None:
        """
        Read raw data from the reader
        """
        pass
    
    @abstractmethod
    def write_xml(self, filename: str) -> bool:
        """
        Write reader configuration to XML
        
        Args:
            filename: Path to the XML file
            
        Returns:
            bool: True if write was successful
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert reader configuration to a dictionary
        
        Returns:
            dict: Dictionary representation of the reader
        """
        return {
            'name': self.name,
            'interface': self.interface,
            'readable_tracks': self.readable_tracks,
            'type': self.__class__.__name__
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create a reader from a dictionary
        
        Args:
            data: Dictionary containing reader configuration
            
        Returns:
            Reader: A new Reader instance
        """
        reader_class = globals().get(data['type'])
        if not reader_class:
            raise ValueError(f"Unknown reader type: {data['type']}")
            
        reader = reader_class()
        reader.name = data.get('name', '')
        reader.interface = data.get('interface', 0)
        reader.readable_tracks = data.get('readable_tracks', [])
        return reader


class DirectReader(Reader):
    """
    Direct hardware reader (parallel/gameport)
    """
    
    def __init__(self, port: int = 0, cp: int = 0, clk1: int = 0, data1: int = 0,
                 clk2: int = 0, data2: int = 0, clk3: int = 0, data3: int = 0):
        """
        Initialize a new DirectReader instance
        
        Args:
            port: Port number
            cp: Clock pin
            clk1: Clock pin for track 1
            data1: Data pin for track 1
            clk2: Clock pin for track 2
            data2: Data pin for track 2
            clk3: Clock pin for track 3
            data3: Data pin for track 3
        """
        # Initialize the parent class with a name
        super().__init__("DirectReader")
        self.port = port
        self.uses_cp = False
        self.cp = cp
        self.clk1 = clk1
        self.data1 = data1
        self.clk2 = clk2
        self.data2 = data2
        self.clk3 = clk3
        self.data3 = data3
    
    def init_reader(self) -> bool:
        """
        Initialize the direct reader hardware
        
        Returns:
            bool: True if initialization was successful
        """
        # Implementation would initialize the hardware here
        self.initialized = True
        return True
    
    def read(self):
        """
        Read a card using the direct reader
        
        Returns:
            Card: The card that was read
        """
        from card import Card
        from track import Track
        
        if not self.initialized and not self.init_reader():
            raise RuntimeError("Reader not initialized")
        
        # This is a placeholder - actual implementation would read from hardware
        card = Card()
        
        # Example: Simulate reading track 1
        if 1 in self.readable_tracks:
            track_data = b"%B1234567890123456^CARDHOLDER/NAME^25121010000000000000000000000000000?"
            track = Track(track_data, len(track_data), 1)
            card.add_track(track)
        
        return card
    
    def read_raw(self) -> None:
        """
        Read raw data from the direct reader
        """
        if not self.initialized and not self.init_reader():
            raise RuntimeError("Reader not initialized")
        
        # Implementation would read raw data from hardware
        print("Raw reading not implemented for DirectReader")
    
    def write_xml(self, filename: str) -> bool:
        """
        Write reader configuration to XML
        
        Args:
            filename: Path to the XML file
            
        Returns:
            bool: True if write was successful
        """
        root = ET.Element("reader")
        root.set("type", "direct")
        
        ET.SubElement(root, "port").text = str(self.port)
        ET.SubElement(root, "uses_cp").text = str(self.uses_cp).lower()
        
        # Add track configurations
        tracks = ET.SubElement(root, "tracks")
        for i, (clk, data) in enumerate([
            (self.clk1, self.data1),
            (self.clk2, self.data2),
            (self.clk3, self.data3)
        ], 1):
            track_elem = ET.SubElement(tracks, "track")
            track_elem.set("number", str(i))
            track_elem.set("clock_pin", str(clk))
            track_elem.set("data_pin", str(data))
        
        # Write to file
        tree = ET.ElementTree(root)
        try:
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            if self.verbose:
                print(f"Error writing XML: {e}", file=sys.stderr)
            return False


class SerialReader(Reader):
    """
    Serial port based card reader
    """
    
    def __init__(self, device: str = ""):
        """
        Initialize a new SerialReader instance
        
        Args:
            device: Path to the serial device (e.g., /dev/ttyS0 or COM1)
        """
        # Initialize the parent class with a name
        super().__init__("SerialReader")
        self.device = device
        self.file_handle = None
        self.flag_cr = False  # CR flag for some readers
    
    def set_device(self, device: str) -> None:
        """
        Set the serial device path
        
        Args:
            device: Path to the serial device
        """
        self.device = device
    
    def set_cr_flag(self, flag: bool) -> None:
        """
        Set the CR flag
        
        Args:
            flag: Value for the CR flag
        """
        self.flag_cr = flag
    
    def init_reader(self) -> bool:
        """
        Initialize the serial reader
        
        Returns:
            bool: True if initialization was successful
        """
        if not self.device:
            if self.verbose:
                print("No device specified", file=sys.stderr)
            return False
        
        try:
            # This would be implemented to open the serial port
            # For now, we'll just check if the device exists
            if not os.path.exists(self.device):
                if self.verbose:
                    print(f"Device {self.device} not found", file=sys.stderr)
                return False
                
            self.initialized = True
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Error initializing serial reader: {e}", file=sys.stderr)
            return False
    
    def read(self):
        """
        Read a card using the serial reader
        
        Returns:
            Card: The card that was read
        """
        from card import Card
        from track import Track
        
        if not self.initialized and not self.init_reader():
            raise RuntimeError("Reader not initialized")
        
        # This is a placeholder - actual implementation would read from serial port
        card = Card()
        
        # Example: Simulate reading track 2
        if 2 in self.readable_tracks:
            track_data = b";1234567890123456=25121010000000000?"
            track = Track(track_data, len(track_data), 2)
            card.add_track(track)
        
        return card
    
    def read_raw(self) -> None:
        """
        Read raw data from the serial reader
        """
        if not self.initialized and not self.init_reader():
            raise RuntimeError("Reader not initialized")
        
        # Implementation would read raw data from serial port
        print("Raw reading not implemented for SerialReader")
    
    def write_xml(self, filename: str) -> bool:
        """
        Write reader configuration to XML
        
        Args:
            filename: Path to the XML file
            
        Returns:
            bool: True if write was successful
        """
        root = ET.Element("reader")
        root.set("type", "serial")
        
        ET.SubElement(root, "device").text = self.device
        ET.SubElement(root, "flag_cr").text = str(self.flag_cr).lower()
        
        # Write to file
        tree = ET.ElementTree(root)
        try:
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            return True
        except Exception as e:
            if self.verbose:
                print(f"Error writing XML: {e}", file=sys.stderr)
            return False


def load_config(config_file: str) -> Reader:
    """
    Load a reader configuration from an XML file
    
    Args:
        config_file: Path to the XML configuration file
        
    Returns:
        Reader: A configured Reader instance
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
        ValueError: If the config file is invalid
    """
    if not os.path.exists(config_file):
        # Default configuration if file doesn't exist
        reader = DirectReader()
        reader.set_can_read_track(1)  # Default to track 1
        reader.set_can_read_track(2)  # and track 2
        return reader
    
    try:
        tree = ET.parse(config_file)
        root = tree.getroot()
        
        reader_type = root.get("type", "direct").lower()
        
        # Map of reader types to their factory functions
        reader_factories = {
            'direct': lambda c: _create_direct_reader(c, root),
            'serial': lambda c: _create_serial_reader(c, root),
            'msr605': lambda c: _create_msr605_reader(c, root)
        }
        
        if reader_type not in reader_factories:
            raise ValueError(f"Unknown reader type: {reader_type}")
            
        # Create the reader using the appropriate factory function
        if reader_type == 'msr605':
            reader = _create_msr605_reader(root.attrib, root)
        else:
            reader = reader_factories[reader_type](root.attrib)
        
        # Parse readable tracks if specified
        tracks_elem = root.find("tracks")
        if tracks_elem is not None:
            for track_elem in tracks_elem.findall("track"):
                track_num = int(track_elem.get("number", "1"))
                if track_elem.get("readable", "true").lower() == "true":
                    reader.set_can_read_track(track_num)
        
        return reader
                
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML in config file: {e}")
    except Exception as e:
        raise ValueError(f"Error loading config: {e}")


def _create_direct_reader(attrib: Dict[str, str], root: ET.Element) -> 'DirectReader':
    """Create a DirectReader instance from XML configuration"""
    reader = DirectReader()
    
    # Parse port and CP
    port_elem = root.find("port")
    if port_elem is not None and port_elem.text:
        port_str = port_elem.text.strip().lower()
        if port_str.startswith('0x'):
            # Handle hexadecimal port numbers
            reader.port = int(port_str, 16)
        else:
            # Handle decimal port numbers
            reader.port = int(port_str)
        
    uses_cp_elem = root.find("uses_cp")
    if uses_cp_elem is not None:
        reader.uses_cp = uses_cp_elem.text.lower() == "true"
    
    # Parse tracks
    tracks_elem = root.find("tracks")
    if tracks_elem is not None:
        for track_elem in tracks_elem.findall("track"):
            track_num = int(track_elem.get("number", "1"))
            clock_pin = int(track_elem.get("clock_pin", "0"))
            data_pin = int(track_elem.get("data_pin", "0"))
            
            # Set the appropriate pins based on track number
            if track_num == 1:
                reader.clk1 = clock_pin
                reader.data1 = data_pin
            elif track_num == 2:
                reader.clk2 = clock_pin
                reader.data2 = data_pin
            elif track_num == 3:
                reader.clk3 = clock_pin
                reader.data3 = data_pin
    
    return reader


def _create_serial_reader(attrib: Dict[str, str], root: ET.Element) -> 'SerialReader':
    """Create a SerialReader instance from XML configuration"""
    device = ""
    device_elem = root.find("device")
    if device_elem is not None:
        device = device_elem.text or ""
    
    reader = SerialReader(device)
    
    # Parse CR flag if specified
    flag_cr_elem = root.find("flag_cr")
    if flag_cr_elem is not None:
        reader.flag_cr = flag_cr_elem.text.lower() == "true"
    
    return reader


def _create_msr605_reader(attrib: Dict[str, str], root: ET.Element) -> 'MSR605Reader':
    """Create an MSR605Reader instance from XML configuration"""
    device_path = attrib.get('device_path', '')
    reader = MSR605Reader(device_path if device_path else None)
    return reader
