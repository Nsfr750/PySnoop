# PySnoop

A modern Python-based application for reading, writing, and analyzing magnetic stripe card data. This project is a continuation of the original StripeSnoop project, rebuilt with modern Python and a user-friendly interface.

## Features

- Read magnetic stripe cards using compatible readers
- View and manage card data in a built-in database
- Support for MSR605 magnetic stripe card reader/writer
- Export/Import card data in multiple formats
- User-friendly GUI with theming support
- Cross-platform compatibility (Windows, macOS, Linux)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Nsfr750/PySnoop.git
   cd PySnoop
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode

```bash
python pysnoop_gui.py
```

### Command Line Mode

```bash
python main.py [options]
```

## Supported Devices

- MSR605 Magnetic Stripe Card Reader/Writer
- Other HID-compatible card readers (experimental)

## License

GNU GENERAL PUBLIC LICENSE

## Credits

- Based on the original StripeSnoop project (http://stripesnoop.sourceforge.net)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
