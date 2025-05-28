#!/usr/bin/env python3
"""
Test HID device detection
"""

import hid

def list_hid_devices():
    """List all HID devices"""
    print("\n=== All HID Devices ===")
    devices = []
    
    try:
        # List all HID devices
        for device in hid.enumerate():
            devices.append(device)
            
            print(f"\nDevice found:")
            print(f"  Path: {device.get('path', 'N/A')}")
            print(f"  Vendor ID: 0x{device.get('vendor_id', 0):04x}")
            print(f"  Product ID: 0x{device.get('product_id', 0):04x}")
            print(f"  Manufacturer: {device.get('manufacturer_string', 'N/A')}")
            print(f"  Product: {device.get('product_string', 'N/A')}")
            print(f"  Serial: {device.get('serial_number', 'N/A')}")
            
    except Exception as e:
        print(f"Error enumerating HID devices: {e}")
    
    return devices

if __name__ == "__main__":
    print("HID Device Detection Test")
    print("========================")
    list_hid_devices()
