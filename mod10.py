#!/usr/bin/env python3
"""
mod10.py - Luhn algorithm implementation for credit card validation and generation

This module provides functions to validate and generate credit card numbers
using the Luhn algorithm (mod 10).

Usage as a script:
    python mod10.py                  # Validate a credit card number
    python mod10.py -g [length]     # Generate a valid credit card number

This is a Python port of mod10.c from Stripe Snoop.
"""

import sys
import random

def mod10_check(card_number):
    """
    Check if a credit card number is valid using the Luhn algorithm.
    
    Args:
        card_number (str): The credit card number to validate
        
    Returns:
        bool: True if the number is valid, False otherwise
    """
    total = 0
    # Process digits from right to left
    for i in range(len(card_number)-1, -1, -1):
        digit = int(card_number[i])
        # Double every second digit from the right
        if (len(card_number) - i) % 2 == 0:
            digit *= 2
            if digit > 9:
                # Sum the digits of numbers > 9
                digit = (digit // 10) + (digit % 10)
        total += digit
    
    # Valid if total is a multiple of 10
    return total % 10 == 0

def generate_credit_card(length=16):
    """
    Generate a valid credit card number of the specified length.
    
    Args:
        length (int): Desired length of the credit card number (default: 16)
        
    Returns:
        str: A valid credit card number
    """
    if length < 4:  # Minimum length for most credit cards
        raise ValueError("Credit card number must be at least 4 digits long")
    
    while True:
        # Generate random digits for all but the last digit
        digits = [random.randint(0, 9) for _ in range(length - 1)]
        
        # Calculate the check digit that makes the number valid
        total = 0
        for i in range(length - 1):
            digit = digits[i]
            # Double every second digit from the right
            if (length - 1 - i) % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit = (digit // 10) + (digit % 10)
            total += digit
        
        # Calculate check digit that makes total + check_digit divisible by 10
        check_digit = (10 - (total % 10)) % 10
        
        # Create the full card number
        card_number = ''.join(map(str, digits)) + str(check_digit)
        
        # Verify the generated number is valid (should always be True)
        if mod10_check(card_number):
            return card_number

def main():
    """Command-line interface for the mod10 utility."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate or generate credit card numbers using the Luhn algorithm.')
    parser.add_argument('-g', '--generate', metavar='LENGTH', type=int, nargs='?', const=16,
                       help='Generate a valid credit card number (default: 16 digits)')
    args = parser.parse_args()
    
    if args.generate is not None:
        try:
            if args.generate < 4:
                print("Error: Credit card number must be at least 4 digits long", file=sys.stderr)
                sys.exit(1)
            print(generate_credit_card(args.generate))
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Validate mode
        print("Enter a credit card number to validate (or press Ctrl+C to exit):")
        try:
            while True:
                card_number = input().strip()
                if not card_number:
                    continue
                # Remove any non-digit characters
                card_digits = ''.join(filter(str.isdigit, card_number))
                if not card_digits:
                    print("Please enter a valid credit card number")
                    continue
                    
                if mod10_check(card_digits):
                    print("✓ Valid credit card number")
                else:
                    print("✗ Invalid credit card number")
                    
                print("\nEnter another number or press Ctrl+C to exit:")
                
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            sys.exit(0)

if __name__ == "__main__":
    main()
