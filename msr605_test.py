#!/usr/bin/env python3
"""
MSR605 Test Script

This script tests the MSR605 reader/writer functionality.
"""

import sys
import time
import argparse
from msr605_reader import MSR605Reader, list_msr605_devices

def print_devices():
    """List all connected MSR605 devices"""
    print("\n=== Connected MSR605 Devices ===")
    devices = list_msr605_devices()
    if not devices:
        print("No MSR605 devices found")
        return []
    
    for i, device in enumerate(devices, 1):
        path = device.get('path', 'N/A')
        if isinstance(path, bytes):
            path = path.decode('utf-8', 'replace')
            
        print(f"{i}. Path: {path}")
        print(f"   Vendor ID: 0x{device.get('vendor_id', 0):04x}")
        print(f"   Product ID: 0x{device.get('product_id', 0):04x}")
        
        # Safely decode bytes to strings
        def safe_decode(value, default='N/A'):
            if value is None:
                return default
            if isinstance(value, str):
                return value
            try:
                return value.decode('utf-8', 'replace')
            except:
                return str(value)
        
        serial = safe_decode(device.get('serial_number'))
        manufacturer = safe_decode(device.get('manufacturer_string'))
        product = safe_decode(device.get('product_string'))
        
        print(f"   Serial: {serial}")
        print(f"   Manufacturer: {manufacturer}")
        print(f"   Product: {product}")
        print()  # Add an extra newline between devices
    
    return devices


def test_connection(device_path=None):
    """Test connection to the MSR605 device"""
    print("\n=== Testing MSR605 Connection ===")
    
    try:
        reader = MSR605Reader(device_path)
        if not reader.init_reader():
            print("Failed to initialize MSR605 reader")
            return None
        
        print("MSR605 connected successfully")
        return reader
        
    except Exception as e:
        print(f"Error connecting to MSR605: {e}")
        return None


def test_read_card(reader):
    """Test reading a card from the MSR605"""
    print("\n=== Testing Card Read ===")
    print("Please swipe a card...")
    
    try:
        # Try to read the card
        card = reader.read()
        if not card:
            print("No card data read or card read failed")
            return False
        
        print("\nCard read successfully!")
        
        # Print track data
        for track_num in [1, 2, 3]:
            track = card.get_track(track_num)
            if track:
                print(f"\nTrack {track_num}:")
                print(f"  Raw Data: {track.get_chars()}")
        
        return True
        
    except Exception as e:
        print(f"Error reading card: {e}")
        return False


def test_write_card(reader, track1=None, track2=None, track3=None):
    """Test writing data to a card"""
    print("\n=== Testing Card Write ===")
    
    if not any([track1, track2, track3]):
        print("No track data provided for writing")
        return False
    
    try:
        from card import Card
        from track import Track
        
        # Create a card with the provided track data
        card = Card()
        
        if track1:
            track = Track(track1.encode('ascii'), len(track1), 1)
            card.add_track(track)
            print(f"Will write Track 1: {track1}")
            
        if track2:
            track = Track(track2.encode('ascii'), len(track2), 2)
            card.add_track(track)
            print(f"Will write Track 2: {track2}")
            
        if track3:
            track = Track(track3.encode('ascii'), len(track3), 3)
            card.add_track(track)
            print(f"Will write Track 3: {track3}")
        
        # Write the card
        tracks_to_write = []
        if track1: tracks_to_write.append(1)
        if track2: tracks_to_write.append(2)
        if track3: tracks_to_write.append(3)
        
        print("\nReady to write. Please insert a card to write to...")
        input("Press Enter when ready to write (or Ctrl+C to cancel)...")
        
        if not reader.write(card, tracks_to_write):
            print("Failed to write card")
            return False
            
        print("Card written successfully!")
        return True
        
    except KeyboardInterrupt:
        print("\nWrite operation cancelled")
        return False
    except Exception as e:
        print(f"Error writing card: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='MSR605 Test Utility')
    parser.add_argument('-d', '--device', help='Specify the device path')
    parser.add_argument('-r', '--read', action='store_true', help='Test reading a card')
    parser.add_argument('-w', '--write', action='store_true', help='Test writing a card')
    parser.add_argument('-t1', '--track1', help='Specify Track 1 data for writing')
    parser.add_argument('-t2', '--track2', help='Specify Track 2 data for writing')
    parser.add_argument('-t3', '--track3', help='Specify Track 3 data for writing')
    parser.add_argument('-l', '--list', action='store_true', help='List available MSR605 devices')
    args = parser.parse_args()

    print("MSR605 Test Utility")
    print("===================")
    
    # List available devices
    devices = list_msr605_devices()
    
    if args.list:
        print_devices()
        return 0
    
    if not devices:
        print("No MSR605 devices found. Please make sure the device is connected and drivers are installed.")
        return 1
    
    # Select device
    device = None
    if args.device:
        device = next((d for d in devices if d.get('path') == args.device), None)
        if not device:
            print(f"Device {args.device} not found")
            return 1
    else:
        device = devices[0]
    
    print(f"Using device: {device.get('path', 'N/A')} ({device.get('manufacturer_string', 'Unknown')} {device.get('product_string', 'Device')})")
    
    # Initialize reader
    try:
        reader = MSR605Reader(device.get('path'))
        if not reader.init_reader():
            print("Failed to initialize MSR605 reader")
            return 1
            
        # Parse track selection
        selected_tracks = [1, 2]  # Default tracks
        
        # Handle read/write operations
        if args.read:
            print(f"\nReading tracks {', '.join(map(str, selected_tracks))}...")
            print("Swipe a card when ready... (Press Ctrl+C to cancel)")
            
            try:
                card = reader.read()
                if card:
                    print("\nCard data read successfully!")
                    for track in card.get_tracks():
                        if track.number in selected_tracks:
                            print(f"Track {track.number}: {track.get_chars()}")
                else:
                    print("No card data detected or read failed.")
            except KeyboardInterrupt:
                print("\nRead operation cancelled.")
        
        elif args.write:
            print(f"\nWriting test data to tracks {', '.join(map(str, selected_tracks))}...")
            print("Insert a writable card when ready... (Press Ctrl+C to cancel)")
            
            # Create a test card with sample data
            from card import Card
            from track import Track
            
            test_card = Card()
            for track_num in selected_tracks:
                test_card.add_track(Track(f"Test Track {track_num}".encode('ascii'), 
                                        len(f"Test Track {track_num}"), 
                                        track_num))
            
            try:
                if reader.write(test_card, selected_tracks):
                    print("\nSuccessfully wrote test data to card!")
                    print("You can now read the card to verify the data.")
                else:
                    print("\nFailed to write to card.")
            except KeyboardInterrupt:
                print("\nWrite operation cancelled.")
        
        else:
            # Interactive mode
            while True:
                print("\nOptions:")
                print("1. Read card")
                print("2. Write test data to card")
                print("3. List devices")
                print("4. Exit")
                
                choice = input("\nSelect an option: ").strip()
                
                if choice == '1':
                    print("\nSwipe a card... (Press Ctrl+C to cancel)")
                    try:
                        card = reader.read()
                        if card:
                            print("\nCard data read successfully!")
                            for track in card.get_tracks():
                                if track.number in selected_tracks:
                                    print(f"Track {track.number}: {track.get_chars()}")
                        else:
                            print("No card data detected or read failed.")
                    except KeyboardInterrupt:
                        print("\nRead operation cancelled.")
                        
                elif choice == '2':
                    print("\nWriting test data to card... (Insert a writable card)")
                    try:
                        from card import Card
                        from track import Track
                        
                        test_card = Card()
                        for track_num in selected_tracks:
                            test_card.add_track(Track(f"Test Track {track_num}".encode('ascii'), 
                                                    len(f"Test Track {track_num}"), 
                                                    track_num))
                        
                        if reader.write(test_card, selected_tracks):
                            print("\nSuccessfully wrote test data to card!")
                        else:
                            print("\nFailed to write to card.")
                    except KeyboardInterrupt:
                        print("\nWrite operation cancelled.")
                    
                elif choice == '3':
                    print("\n=== Connected MSR605 Devices ===")
                    if not devices:
                        print("No MSR605 devices found")
                    else:
                        for i, dev in enumerate(devices, 1):
                            path = dev.get('path', 'N/A')
                            if isinstance(path, bytes):
                                path = path.decode('utf-8', 'replace')
                            print(f"{i}. {dev.get('manufacturer_string', 'Unknown')} {dev.get('product_string', 'Device')}")
                            print(f"   Path: {path}")
                            print(f"   Serial: {dev.get('serial_number', 'N/A')}\n")
                    
                elif choice == '4':
                    print("Goodbye!")
                    break
                    
                else:
                    print("Invalid option. Please try again.")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if 'reader' in locals() and reader:
            reader.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
