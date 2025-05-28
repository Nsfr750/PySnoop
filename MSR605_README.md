# MSR605 Card Reader/Writer Integration

This document provides information on how to use the MSR605 magnetic stripe card reader/writer with the application.

## Prerequisites

1. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

2. On Windows, you may need to install the libusb driver for the MSR605:
   - Download Zadig from https://zadig.akeo.ie/
   - Connect your MSR605 device
   - Open Zadig and select the MSR605 device
   - Install the libusb-win32 driver

## Configuration

### Using the GUI

1. Go to `Tools` > `MSR605 Reader/Writer`
2. The application will automatically detect connected MSR605 devices
3. Select your device from the dropdown and click "Connect"
4. Use the interface to read from or write to magnetic stripe cards

### Using the Command Line

To use the MSR605 reader from the command line:

```
python main.py --msr605
```

This will start the application in MSR605 mode, automatically detecting and connecting to the first available MSR605 device.

### Configuration File

You can also create a configuration file for the MSR605 reader. Create a file named `config_msr605.xml` with the following content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<reader type="msr605">
    <!-- Optional: Specify the device path if you want to use a specific device -->
    <!-- <device_path>/dev/hidraw0</device_path> -->
    
    <!-- Configure which tracks to read/write -->
    <tracks>
        <track number="1" readable="true" writable="true" />
        <track number="2" readable="true" writable="true" />
        <track number="3" readable="true" writable="true" />
    </tracks>
</reader>
```

Then run the application with:

```
python main.py -c config_msr605.xml
```

## Troubleshooting

### Device Not Found
- Ensure the MSR605 is properly connected to your computer
- On Windows, make sure the libusb driver is installed (see Prerequisites)
- Try unplugging and reconnecting the device

### Permission Issues
On Linux, you may need to add a udev rule to allow access to the device:

1. Create a file at `/etc/udev/rules.d/99-msr605.rules` with the following content:
   ```
   SUBSYSTEM=="usb", ATTRS{idVendor}=="0801", ATTRS{idProduct}=="0001", MODE="0666"
   ```
2. Reload udev rules:
   ```
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

### Data Format Issues
- Ensure the card data is in the correct format:
  - Track 1: Starts with `%`
  - Track 2: Starts with `;`
  - Track 3: Starts with `;`

## Development

The MSR605 reader implementation is in `msr605_reader.py`. The code provides a high-level interface for interacting with the device, with support for:

- Reading raw track data
- Writing data to cards
- Erasing cards
- Device status monitoring

Refer to the code documentation for more details on the API.
