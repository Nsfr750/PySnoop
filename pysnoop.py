"""
Stripe Snoop 2.0 - Python Implementation

Stripe Snoop is a suite of research tools that captures, modifies, 
validates, generates, analyzes, and shares data from magstripe cards.
"""

import sys
import os
import argparse
from pathlib import Path
from card import Card
from reader import load_config
from ssflags import SSFlags
from database import CardDatabase

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Stripe Snoop - Magstripe Card Reader')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose output')
    parser.add_argument('-l', '--loop', action='store_true', help='enable loop mode')
    parser.add_argument('-c', '--config', help='specify config file')
    parser.add_argument('-i', '--input', help='input file')
    parser.add_argument('--raw', action='store_true', help='raw mode (no database lookup)')
    parser.add_argument('--test-db', action='store_true', help='run database tests and exit')
    parser.add_argument('--msr605', action='store_true', help='use MSR605 reader')
    
    args = parser.parse_args()
    
    # Initialize flags
    ss_flags = SSFlags()
    ss_flags.VERBOSE = args.verbose
    ss_flags.LOOP = args.loop
    ss_flags.RAW = args.raw
    
    if args.config:
        ss_flags.CONFIG = True
        ss_flags.set_config_file(args.config)
    
    if args.input:
        ss_flags.INPUT = True
        ss_flags.set_file_input(args.input)
    
    # Run database tests if requested
    if args.test_db:
        from examples.test_database import main as test_db_main
        test_db_main()
        return 0
    
    if not ss_flags.RAW:
        print("Stripe Snoop Version 2.0 - Python Implementation")
        print("http://stripesnoop.sourceforge.net  Acidus@msblabs.net\n")
    
    # Initialize reader
    if args.msr605:
        # Use MSR605 with default settings
        from msr605_reader import MSR605Reader
        reader = MSR605Reader()
        if not reader.init_reader():
            print("Failed to initialize MSR605 reader", file=sys.stderr)
            return 1
    elif not ss_flags.CONFIG:
        # Default config location
        reader = load_config("config.xml")
    else:
        # User-defined config file
        reader = load_config(ss_flags.config)
    
    if not reader.init_reader():
        print("Failed to initialize reader", file=sys.stderr)
        return 1
    
    if ss_flags.RAW:
        reader.read_raw()
        return 0
    
    try:
        # Read the card
        card = reader.read()
        
        # Process the card with the database
        if not ss_flags.RAW:
            # Initialize the card database
            db = CardDatabase()
            
            # Run tests on the card
            result = db.run_tests(card)
            
            # Print the results
            if result.is_valid():
                print(f"\nCard type: {result.get_card_type()}")
                print("\nCard details:")
                for i in range(result.get_num_tags()):
                    print(f"  {result.get_name_tag(i)}: {result.get_data_tag(i)}")
                
                if result.get_notes():
                    print(f"\nNotes: {result.get_notes()}")
                    
                if result.get_unknowns():
                    print(f"\nUnknown fields: {result.get_unknowns()}")
            else:
                print("\nNo matching card type found in the database.")
            
            # Print the raw track data
            print("\nRaw track data:")
            for track_num in [1, 2, 3]:
                track = card.get_track(track_num)
                if track:
                    print(f"Track {track_num}: {track.get_chars()}")
            
            # Decode and print tracks
            card.decode_tracks()
            card.print_tracks()
            
            # TODO: Add more database functionality here
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
