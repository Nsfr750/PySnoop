"""
MSR605 Reader/Writer Implementation

This module provides support for the MagTek MSR605 magnetic stripe card reader/writer
using PySerial for communication.
"""

import time
import serial
import serial.tools.list_ports
from typing import Optional, List, Dict, Any, Type, TYPE_CHECKING

# Import Card and Track locally to avoid circular imports
if TYPE_CHECKING:
    from reader import Reader
    from card import Card
    from track import Track

# MSR605 Commands
MSR_CMD_RESET = b'\x1B\x61'  # Reset
MSR_CMD_READ_RAW = b'\x1B\x72'  # Read raw data
MSR_CMD_WRITE = b'\x1B\x77'  # Write data
MSR_CMD_ERASE = b'\x1B\x63'  # Erase card
MSR_CMD_SET_ISO = b'\x1B\x6F'  # Set ISO format
MSR_CMD_GET_DEVICE_MODEL = b'\x1B\x74'  # Get device model
MSR_CMD_GET_FIRMWARE = b'\x1B\x76'  # Get firmware version
MSR_CMD_GET_SERIAL = b'\x1B\x6A'  # Get serial number

# Default settings
DEFAULT_BAUD_RATE = 9600
DEFAULT_PORT = 'COM5'

# Import Reader at the top level to avoid circular imports
from reader import Reader

class MSR605Reader(Reader):
    """
    Implementation of the MagTek MSR605 magnetic stripe card reader/writer
    using PySerial for communication.
    """
    
    def __init__(self, com_port: Optional[str] = None, baud_rate: int = DEFAULT_BAUD_RATE):
        """
        Initialize a new MSR605Reader instance
        
        Args:
            com_port: Optional COM port (e.g., 'COM5'). If None, will use DEFAULT_PORT
            baud_rate: Baud rate for serial communication (default: 9600)
        """
        super().__init__("MSR605")
        self.com_port = com_port or DEFAULT_PORT
        self.baud_rate = baud_rate
        self.serial = None
        self.initialized = False
        self.verbose = False
        self.readable_tracks = [1, 2, 3]  # All tracks readable
        self.writable_tracks = [1, 2, 3]  # All tracks writable
    
    def set_serial_port(self, com_port: str, baud_rate: int = None) -> None:
        """
        Set the serial port and optionally the baud rate for the MSR605
        
        Args:
            com_port: COM port (e.g., 'COM5')
            baud_rate: Optional baud rate (default: keep current)
        """
        self.com_port = com_port
        if baud_rate is not None:
            self.baud_rate = baud_rate
    
    @staticmethod
    def list_serial_ports() -> List[Dict[str, Any]]:
        """
        List all available serial ports with detailed information
        
        Returns:
            List of dictionaries containing port information
        """
        ports = []
        for port in serial.tools.list_ports.comports():
            port_info = {
                'device': port.device,
                'name': port.name,
                'description': port.description or 'N/A',
                'hwid': port.hwid or 'N/A',
                'vid': port.vid if port.vid is not None else 'N/A',
                'pid': port.pid if port.pid is not None else 'N/A',
                'serial_number': port.serial_number or 'N/A',
                'manufacturer': port.manufacturer or 'N/A',
                'product': port.product or 'N/A',
                'interface': port.interface or 'N/A'
            }
            ports.append(port_info)
        return ports
    
    def init_reader(self) -> bool:
        """
        Initialize the MSR605 reader
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            if self.verbose:
                print(f"Initializing MSR605 reader on {self.com_port} at {self.baud_rate} baud")
            
            # Close port if already open
            if hasattr(self, 'serial') and self.serial and self.serial.is_open:
                self.serial.close()
            
            # Open serial port
            self.serial = serial.Serial(
                port=self.com_port,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
                xonxoff=0,
                rtscts=0
            )
            
            # Reset the reader
            self.serial.write(MSR_CMD_RESET)
            time.sleep(0.1)  # Give it time to reset
            
            # Check if we can communicate with the reader
            self.serial.write(MSR_CMD_GET_DEVICE_MODEL)
            response = self.serial.read(16)
            
            if not response:
                if self.verbose:
                    print("No response from reader")
                self.close()
                return False
                
            # If we got here, initialization was successful
            self.initialized = True
            if self.verbose:
                print(f"Successfully initialized MSR605 on {self.com_port}")
            return True
            
        except serial.SerialException as e:
            if self.verbose:
                print(f"Serial port error: {str(e)}")
            self.close()
            return False
            
        except Exception as e:
            if self.verbose:
                print(f"Error initializing MSR605: {str(e)}")
                import traceback
                print(traceback.format_exc())
            self.close()
            return False
    
    def _auto_detect_serial_port(self) -> bool:
        """
        Try to auto-detect the MSR605 on available serial ports.
        
        Returns:
            bool: True if device was found and initialized, False otherwise
        """
        try:
            print("Auto-detecting MSR605 on available serial ports...")
            
            # Common baud rates to try (starting with the default)
            baud_rates = [self.baud_rate, 9600, 19200, 38400, 57600, 115200]
            
            # Get list of available ports
            ports = serial.tools.list_ports.comports()
            if not ports:
                print("No serial ports found")
                return False
                
            # Try each port with each baud rate
            for port in ports:
                port_name = port.device
                print(f"Trying port: {port_name} ({port.description or 'No description'})")
                
                for baud in baud_rates:
                    try:
                        print(f"  Trying baud rate: {baud}")
                        
                        # Save current settings
                        old_port = self.com_port
                        old_baud = self.baud_rate
                        
                        # Try to initialize with this port and baud rate
                        self.com_port = port_name
                        self.baud_rate = baud
                        
                        if self.init_reader():
                            print(f"  Found MSR605 on {port_name} at {baud} baud")
                            return True
                            
                        # Restore old settings if not successful
                        self.com_port = old_port
                        self.baud_rate = old_baud
                        
                    except Exception as e:
                        print(f"  Error trying {port_name} at {baud} baud: {str(e)}")
                        continue
            
            print("MSR605 not found on any serial ports")
            return False
            
        except Exception as e:
            print(f"Error in auto-detection: {str(e)}")
            if self.verbose:
                import traceback
                print(traceback.format_exc())
            return False
    
    def _send_command(self, command: bytes, response: bool = False, timeout: float = 1.0) -> Optional[bytes]:
        """
        Send a command to the MSR605 and optionally wait for a response
        
        Args:
            command: The command to send
            response: Whether to wait for and return a response
            timeout: Timeout in seconds
            
        Returns:
            Optional[bytes]: The response if response=True, None otherwise
        """
        if not self.initialized or not self.serial or not self.serial.is_open:
            if not self.init_reader():
                print("Error: Could not initialize MSR605")
                return None
        
        try:
            # Clear any pending input
            if self.serial.in_waiting > 0:
                self.serial.reset_input_buffer()
            
            # Send the command
            self.serial.write(command)
            
            if response:
                # Wait for response with timeout
                start_time = time.time()
                response_data = bytearray()
                
                while time.time() - start_time < timeout:
                    if self.serial.in_waiting > 0:
                        # Read all available data
                        chunk = self.serial.read(self.serial.in_waiting)
                        response_data.extend(chunk)
                        
                        # Check if we have a complete response
                        if len(response_data) >= 2 and response_data[-2:] == b'\r\n':
                            return bytes(response_data)
                    
                    # Small delay to prevent busy waiting
                    time.sleep(0.01)
                
                # Return whatever we have if we timed out
                return bytes(response_data) if response_data else None
                
            return None
            
        except serial.SerialException as e:
            print(f"Serial communication error: {str(e)}")
            self.initialized = False
            return None
            
        except Exception as e:
            print(f"Error sending command: {str(e)}")
            if self.verbose:
                import traceback
                print(traceback.format_exc())
            return None
    
    def read(self) -> Optional[Dict[str, str]]:
        """
        Read data from the MSR605
        
        Returns:
            Dict[str, str]: Dictionary containing track data if successful, None otherwise
        """
        if not self.initialized and not self.init_reader():
            print("Error: Could not initialize MSR605")
            return None
            
        try:
            # Send read command
            self._send_command(MSR_CMD_READ_RAW)
            time.sleep(0.1)  # Give the device time to respond
            
            # Read response with a longer timeout for reading
            response = self._send_command(b'', response=True, timeout=5.0)
            
            if not response:
                print("No response from MSR605")
                return None
                
            # Parse track data
            tracks = {}
            current_track = None
            
            for b in response:
                if b == 0x01:  # Start of track 1
                    current_track = 1
                    tracks[current_track] = bytearray()
                elif b == 0x02:  # Start of track 2
                    current_track = 2
                    tracks[current_track] = bytearray()
                elif b == 0x03:  # Start of track 3
                    current_track = 3
                    tracks[current_track] = bytearray()
                elif b == 0x0D:  # Carriage return
                    current_track = None
                elif current_track is not None:
                    tracks[current_track].append(b)
            
            # Convert to strings
            result = {}
            for track, data in tracks.items():
                try:
                    result[f'track{track}'] = data.decode('ascii', errors='replace').strip()
                except Exception as e:
                    print(f"Error decoding track {track}: {str(e)}")
                    result[f'track{track}'] = data.hex()
            
            return result if result else None
            
        except Exception as e:
            print(f"Error reading from MSR605: {str(e)}")
            if self.verbose:
                import traceback
                print(traceback.format_exc())
            return None
    
    def write(self, track_data: Dict[int, str]) -> bool:
        """
        Write data to a card using the MSR605
        
        Args:
            track_data: Dictionary mapping track numbers (1-3) to data strings
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        if not self.initialized and not self.init_reader():
            print("Error: Could not initialize MSR605")
            return False
            
        if not track_data or not isinstance(track_data, dict):
            print("Error: Invalid track data")
            return False
            
        try:
            # Prepare write command
            write_cmd = bytearray(MSR_CMD_WRITE)
            
            # Add track data
            for track_num, data in track_data.items():
                if track_num not in [1, 2, 3]:
                    print(f"Warning: Invalid track number {track_num}, skipping")
                    continue
                    
                if not isinstance(data, (str, bytes, bytearray)):
                    print(f"Warning: Invalid data type for track {track_num}, skipping")
                    continue
                    
                # Convert string to bytes if needed
                if isinstance(data, str):
                    try:
                        data = data.encode('ascii')
                    except UnicodeEncodeError:
                        print(f"Warning: Could not encode track {track_num} data to ASCII, skipping")
                        continue
                
                # Add track start marker and data
                write_cmd.append(track_num)  # Track start marker (0x01, 0x02, or 0x03)
                write_cmd.extend(data)      # Track data
            
            # Add end marker if we have any tracks to write
            if len(write_cmd) > len(MSR_CMD_WRITE):
                write_cmd.append(0x3F)  # '?' end marker
                
                # Send the write command
                print(f"Sending write command: {write_cmd.hex(' ')}")
                self._send_command(bytes(write_cmd))
                
                # Wait for the write to complete
                time.sleep(1.0)
                
                # Verify the write by reading back the data
                print("Verifying write...")
                read_data = self.read()
                
                if read_data:
                    print("Write verification results:")
                    for track, data in track_data.items():
                        track_key = f'track{track}'
                        if track_key in read_data:
                            match = read_data[track_key] == data
                            print(f"  Track {track}: {'OK' if match else 'MISMATCH'}")
                        else:
                            print(f"  Track {track}: MISSING")
                    
                    return all(
                        read_data.get(f'track{track}', '') == data 
                        for track, data in track_data.items()
                    )
                
                return False
            
            print("No valid track data to write")
            return False
            
        except Exception as e:
            print(f"Error writing to card: {str(e)}")
            if self.verbose:
                import traceback
                print(traceback.format_exc())
            return False
    
    def close(self):
        """Close the connection to the MSR605"""
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
                self.initialized = False
                if self.verbose:
                    print("Closed connection to MSR605")
            except Exception as e:
                if self.verbose:
                    print(f"Error closing connection: {str(e)}")
                    
    def read_raw(self) -> Dict[str, str]:
        """
        Read raw data from the MSR605 reader
        
        Returns:
            Dict[str, str]: Dictionary containing raw track data with keys 'track1', 'track2', 'track3'
        """
        if not self.initialized and not self.init_reader():
            raise RuntimeError("MSR605 reader not initialized")
            
        try:
            # Send read raw command
            self.serial.write(MSR_CMD_READ_RAW)
            
            # Read response (format: STX [track1 data] FS [track2 data] FS [track3 data] ETX)
            # FS = 0x1C, ETX = 0x03
            response = bytearray()
            while True:
                byte = self.serial.read(1)
                if not byte:
                    break
                response.extend(byte)
                if byte == b'\x03':  # ETX
                    break
            
            # Parse response
            tracks = response.split(b'\x1c')
            track_data = {}
            
            if len(tracks) >= 1 and len(tracks[0]) > 1:  # Track 1 (skip STX)
                track_data['track1'] = tracks[0][1:].decode('ascii', errors='replace')
            if len(tracks) >= 2:  # Track 2
                track_data['track2'] = tracks[1].decode('ascii', errors='replace')
            if len(tracks) >= 3:  # Track 3 (remove ETX)
                track_data['track3'] = tracks[2][:-1].decode('ascii', errors='replace')
                
            return track_data
            
        except Exception as e:
            if self.verbose:
                print(f"Error reading raw data: {str(e)}")
            raise
    
    def write_xml(self, filename: str) -> bool:
        """
        Write the MSR605 reader configuration to an XML file
        
        Args:
            filename: Path to the XML file
            
        Returns:
            bool: True if write was successful, False otherwise
        """
        try:
            import xml.etree.ElementTree as ET
            from xml.dom import minidom
            
            # Create root element
            root = ET.Element("reader")
            root.set("type", "msr605")
            
            # Add port information
            port_elem = ET.SubElement(root, "port")
            port_elem.text = self.com_port
            
            # Add baud rate
            baud_elem = ET.SubElement(root, "baudrate")
            baud_elem.text = str(self.baud_rate)
            
            # Create a pretty XML string
            rough_string = ET.tostring(root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            # Write to file
            with open(filename, 'w') as f:
                f.write(pretty_xml)
                
            if self.verbose:
                print(f"Configuration saved to {filename}")
                
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"Error writing XML configuration: {str(e)}")
            return False
    
    def __del__(self):
        """Destructor to ensure the serial connection is properly closed"""
        self.close()

def list_msr605_devices() -> List[Dict[str, Any]]:
    """
    List all connected MSR605 devices
    
    Returns:
        List[Dict[str, Any]]: List of device information dictionaries
    """
    # For serial devices, we can't reliably detect MSR605 without trying to communicate
    # So we'll just list all available serial ports
    return MSR605Reader.list_serial_ports()


def create_msr605_reader(config: Dict[str, Any]) -> 'MSR605Reader':
    """
    Create an MSR605 reader from a configuration dictionary
    
    Args:
        config: Configuration dictionary with reader configuration
        
    Returns:
        MSR605Reader: Configured MSR605 reader instance
    """
    com_port = config.get('com_port', DEFAULT_PORT)
    baud_rate = config.get('baud_rate', DEFAULT_BAUD_RATE)
    verbose = config.get('verbose', False)
    
    reader = MSR605Reader(com_port=com_port, baud_rate=baud_rate)
    reader.verbose = verbose
    
    return reader
