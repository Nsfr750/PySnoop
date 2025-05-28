"""
MSR605 Reader/Writer Implementation

This module provides support for the MagTek MSR605 magnetic stripe card reader/writer.
"""

import hid
import time
import sys
from typing import Optional, List, Dict, Any, Type, TYPE_CHECKING

# Import Card and Track locally to avoid circular imports
if TYPE_CHECKING:
    from reader import Reader
    from card import Card
    from track import Track

# MSR605 USB Vendor and Product IDs
MSR605_VENDOR_ID = 0x0801
MSR605_PRODUCT_ID = 0x0001

# MSR605 Commands
MSR_CMD_RESET = b'\x1B\x61'  # Reset
MSR_CMD_READ_RAW = b'\x1B\x72'  # Read raw data
MSR_CMD_WRITE = b'\x1B\x77'  # Write data
MSR_CMD_ERASE = b'\x1B\x63'  # Erase card
MSR_CMD_SET_ISO = b'\x1B\x6F'  # Set ISO format
MSR_CMD_GET_DEVICE_MODEL = b'\x1B\x74'  # Get device model
MSR_CMD_GET_FIRMWARE = b'\x1B\x76'  # Get firmware version
MSR_CMD_GET_SERIAL = b'\x1B\x6A'  # Get serial number

# Track densities
TRACK_DENSITY_LOCO = 0  # 210 bpi
TRACK_DENSITY_HICO = 1  # 75 bpi

class MSR605Reader:
    """
    Implementation of the MagTek MSR605 magnetic stripe card reader/writer
    """
    
    def __init__(self, device_path: Optional[str] = None):
        """
        Initialize a new MSR605Reader instance
        
        Args:
            device_path: Optional path to the HID device
        """
        # Import Reader here to avoid circular imports
        from reader import Reader
        self.__class__.__bases__ = (Reader,)
        Reader.__init__(self, "MSR605")
        self.device_path = device_path
        self.device = None
        self.initialized = False
        self.readable_tracks = [1, 2, 3]  # MSR605 can read all 3 tracks
        self.writable_tracks = [1, 2, 3]   # MSR605 can write to all 3 tracks
        
    def init_reader(self) -> bool:
        """
        Initialize the MSR605 reader
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            # Try to find the MSR605 device
            if self.device_path:
                self.device = hid.device()
                self.device.open_path(self.device_path.encode('utf-8'))
            else:
                # Auto-detect MSR605
                devices = hid.enumerate(MSR605_VENDOR_ID, MSR605_PRODUCT_ID)
                if not devices:
                    print("MSR605 device not found", file=sys.stderr)
                    return False
                    
                self.device = hid.device()
                self.device.open(MSR605_VENDOR_ID, MSR605_PRODUCT_ID)
            
            # Set non-blocking mode
            self.device.set_nonblocking(1)
            
            # Reset the device
            self._send_command(MSR_CMD_RESET)
            time.sleep(0.5)  # Wait for reset
            
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"Error initializing MSR605: {e}", file=sys.stderr)
            self.initialized = False
            return False
    
    def _send_command(self, command: bytes, data: bytes = b'') -> Optional[bytes]:
        """
        Send a command to the MSR605 and read the response
        
        Args:
            command: Command to send
            data: Optional data to send with the command
            
        Returns:
            Optional[bytes]: Response data or None if no response
        """
        if not self.device:
            return None
            
        try:
            # Send the command
            self.device.write(command + data)
            
            # Read response
            response = self.device.read(64)  # Read up to 64 bytes
            return bytes(response) if response else None
            
        except Exception as e:
            print(f"Error sending command to MSR605: {e}", file=sys.stderr)
            return None
    

    
    def read(self):
        """
        Read a card from the MSR605
        
        Returns:
            Optional[Card]: The card that was read, or None if no card was read
        """
        if not self.initialized and not self.init_reader():
            return None
            
        # Import Card and Track here to avoid circular imports
        from card import Card
        from track import Track
            
        # Send read command
        response = self._send_command(MSR_CMD_READ_RAW)
        if not response:
            return None
            
        # Parse the response into tracks
        card = Card()
        
        # The response format depends on the card and tracks encoded
        # This is a simplified parser - you may need to adjust based on your needs
        try:
            # Split response into tracks (simplified)
            tracks_data = response.split(b'%')
            
            for track_data in tracks_data:
                if not track_data:
                    continue
                    
                # The first character indicates the track number
                track_num = int(track_data[0])
                if track_num not in [1, 2, 3]:
                    continue
                    
                # The rest is the track data
                data = track_data[1:].strip()
                if data:
                    track = Track(data, len(data), track_num)
                    card.add_track(track)
                    
        except Exception as e:
            print(f"Error parsing card data: {e}", file=sys.stderr)
            return None
            
        return card if card.get_tracks() else None
        

    
    def write(self, card, tracks=None):
        """
        Write data to a card using the MSR605
        
        Args:
            card: Card object containing track data
            tracks: List of track numbers to write (default: all tracks)
            
        Returns:
            bool: True if write was successful
        """
        if not self.initialized and not self.init_reader():
            return False
            
        if tracks is None:
            tracks = self.writable_tracks
            
        try:
            # Erase the card first
            self._send_command(MSR_CMD_ERASE)
            time.sleep(0.5)
            
            # Write each track
            for track_num in tracks:
                track = card.get_track(track_num)
                if not track:
                    continue
                    
                # Format the track data for writing
                # This is a simplified version - you'll need to adjust based on your needs
                track_data = f"{track_num}{track.get_chars()}".encode('ascii')
                self._send_command(MSR_CMD_WRITE, track_data)
                time.sleep(0.2)
                
            return True
            
        except Exception as e:
            print(f"Error writing to card: {e}", file=sys.stderr)
            return False
            
    def read_raw(self) -> None:
        """
        Read raw data from the MSR605
        """
        if not self.initialized and not self.init_reader():
            return
            
        try:
            response = self._send_command(MSR_CMD_READ_RAW)
            if response:
                print("Raw data:", response.hex(' '))
                
        except Exception as e:
            print(f"Error reading raw data: {e}", file=sys.stderr)
    
    def write_xml(self, filename: str) -> bool:
        """
        Write reader configuration to XML
        
        Args:
            filename: Path to the XML file
            
        Returns:
            bool: True if write was successful
        """
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.Element("reader")
            root.set("type", "msr605")
            
            if self.device_path:
                path_elem = ET.SubElement(root, "device_path")
                path_elem.text = self.device_path
                
            tree = ET.ElementTree(root)
            tree.write(filename, encoding='utf-8', xml_declaration=True)
            return True
            
        except Exception as e:
            print(f"Error writing XML configuration: {e}", file=sys.stderr)
            return False
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'device') and self.device:
            try:
                self.device.close()
            except:
                pass

# Helper function to list available MSR605 devices
def list_msr605_devices() -> List[Dict[str, Any]]:
    """
    List all connected MSR605 devices
    
    Returns:
        List[Dict[str, Any]]: List of device information dictionaries
    """
    try:
        devices = hid.enumerate(MSR605_VENDOR_ID, MSR605_PRODUCT_ID)
        return devices or []
    except:
        return []

# Add to the reader factory in reader.py
def create_msr605_reader(config):
    """
    Create an MSR605 reader from a configuration dictionary
    
    Args:
        config: Configuration dictionary
        
    Returns:
        MSR605Reader: Configured MSR605 reader instance
    """
    device_path = config.get('device_path')
    reader = MSR605Reader(device_path)
    
    # Set readable tracks if specified
    if 'readable_tracks' in config:
        reader.readable_tracks = [int(t) for t in config['readable_tracks']]
        
    return reader
