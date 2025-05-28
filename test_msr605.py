

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
    
    if args.list:
        print_devices()
        return
    
    # List available devices
    devices = print_devices()
    if not devices:
        print("\nNo MSR605 devices found. Please connect a device and try again.")
        return
    
    # Test connection to the first device
    device_path = args.device or devices[0].get('path').decode('utf-8', 'replace') if devices[0].get('path') else None
    reader = test_connection(device_path)
    if not reader:
        return
    
    try:
        if args.read:
            test_read_card(reader)
        elif args.write:
            test_write_card(reader, args.track1, args.track2, args.track3)
        else:
            while True:
                print("\n=== MSR605 Test Menu ===")
                print("1. Test Card Read")
                print("2. Test Card Write (Track 1 & 2)")
                print("3. Test Card Write (Custom Tracks)")
                print("4. Exit")
                
                choice = input("\nEnter your choice (1-4): ").strip()
                
                if choice == '1':
                    # Test reading a card
                    test_read_card(reader)
                    
                elif choice == '2':
                    # Test writing a sample card (Track 1 & 2)
                    track1 = "%B1234567890123456^CARDHOLDER/NAME^2512101000000000000000000000000?"
                    track2 = ";1234567890123456=25121010000000000000?"
                    test_write_card(reader, track1=track1, track2=track2)
                    
                elif choice == '3':
                    # Test writing custom track data
                    print("\nEnter track data (leave blank to skip):")
                    track1 = input("Track 1 (starts with %): ").strip()
                    track2 = input("Track 2 (starts with ;): ").strip()
                    track3 = input("Track 3 (starts with ;): ").strip()
                    
                    if not any([track1, track2, track3]):
                        print("No track data provided. Operation cancelled.")
                        continue
                        
                    test_write_card(reader, track1 or None, track2 or None, track3 or None)
                    
                elif choice == '4':
                    print("Exiting...")
                    break
                    
                else:
                    print("Invalid choice. Please try again.")
                    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        # Clean up
        if reader:
            reader = None
            print("\nDisconnected from MSR605")

if __name__ == "__main__":
    main()
