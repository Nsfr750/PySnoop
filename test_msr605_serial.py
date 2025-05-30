"""
Test script for MSR605 serial reader/writer
"""

import time
from msr605_serial import MSR605Reader

def list_ports():
    """List all available serial ports"""
    print("\n=== Available Serial Ports ===")
    ports = MSR605Reader.list_serial_ports()
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port['device']} - {port['description']} (VID:{port['vid']:04X}, PID:{port['pid']:04X})")
    print("=" * 30 + "\n")

def test_connection(port=None, baud=9600):
    """Test connection to MSR605"""
    print(f"\n=== Testing connection to {port or 'auto-detect'} at {baud} baud ===")
    
    try:
        reader = MSR605Reader(com_port=port, baud_rate=baud)
        reader.verbose = True
        
        if reader.init_reader():
            print("✓ Successfully connected to MSR605")
            
            # Test reading
            print("\nPlace a card on the reader...")
            input("Press Enter when ready to read...")
            
            data = reader.read()
            if data:
                print("\nCard data read successfully:")
                for track, value in data.items():
                    print(f"  {track}: {value}")
            else:
                print("\nNo card data read or error occurred")
            
            # Test writing
            test_write = input("\nTest writing? (y/n): ").lower() == 'y'
            if test_write and data:
                print("\nWriting data back to card...")
                success = reader.write(data)
                print(f"Write {'succeeded' if success else 'failed'}")
            
        else:
            print("✗ Failed to connect to MSR605")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'reader' in locals():
            reader.close()
            print("\nConnection closed")

def main():
    """Main test function"""
    print("MSR605 Serial Tester")
    print("====================\n")
    
    while True:
        print("\nOptions:")
        print("1. List available serial ports")
        print("2. Test connection (auto-detect)")
        print("3. Test connection (specify port)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            list_ports()
        elif choice == '2':
            test_connection()
        elif choice == '3':
            port = input("Enter COM port (e.g., COM5): ").strip()
            baud = input(f"Enter baud rate [{MSR605Reader.DEFAULT_BAUD_RATE}]: ").strip()
            test_connection(port, int(baud) if baud else MSR605Reader.DEFAULT_BAUD_RATE)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
