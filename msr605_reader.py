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

# Track densities
TRACK_DENSITY_LOCO = 0  # 210 bpi
TRACK_DENSITY_HICO = 1  # 75 bpi

# Default settings
DEFAULT_BAUD_RATE = 9600
DEFAULT_PORT = 'COM5'

# Import Reader at the top level to avoid circular imports
from reader import Reader

class MSR605Reader(Reader):
    """
    Implementation of the MagTek MSR605 magnetic stripe card reader/writer
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
            # Close any existing connection
            self.close()
            
            print(f"Attempting to connect to MSR605 on {self.com_port} at {self.baud_rate} baud...")
            
            # Try to open the specified COM port
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
            
            # Reset the device
            self._send_command(MSR_CMD_RESET)
            time.sleep(0.5)
            
            # Set ISO format
            self._send_command(MSR_CMD_SET_ISO + b'1')
            time.sleep(0.1)
            
            # Try to get device model
            response = self._send_command(MSR_CMD_GET_DEVICE_MODEL, response=True)
            
            if response:
                print(f"Successfully connected to MSR605 on {self.com_port} at {self.baud_rate} baud")
                self.initialized = True
                return True
            
            print(f"No response from MSR605 on {self.com_port} at {self.baud_rate} baud")
            self.close()
            return False
            
        except serial.SerialException as e:
            print(f"Serial port error: {str(e)}")
            self.close()
            return False
            
        except Exception as e:
            import traceback
            print(f"Error initializing MSR605: {str(e)}")
            if self.verbose:
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
        
        # Convert to strings
        result = {}
        for track, data in tracks.items():
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
        config: Configuration dictionary with reader configuration
        
    Returns:
        MSR605Reader: Configured MSR605 reader instance
    """
    # Get device path from config or use default
    device_path = config.get('device_path')
    
    # Create and configure the reader
    reader = MSR605Reader(device_path)
    reader.set_verbose(config.get('verbose', False))
    
    # Set readable tracks if specified
    if 'readable_tracks' in config:
        reader.set_readable_tracks(config['readable_tracks'])
    
    return reader
