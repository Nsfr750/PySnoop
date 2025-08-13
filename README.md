# PySnoop

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A modern Python-based application for reading, writing, and analyzing magnetic stripe card data. This project is a continuation of the original StripeSnoop project, rebuilt with modern Python and a user-friendly interface.

## ✨ Features

- **Card Reading**: Read magnetic stripe cards using compatible readers
- **Database Management**: Store and manage card data securely
- **Multiple Formats**: Export/Import card data in various formats
- **Modern GUI**: User-friendly interface with theming support
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Standalone Executable**: Build as a single executable file for easy distribution
- **Debug Builds**: Special debug configuration for troubleshooting
- **Security**: Secure storage for sensitive card data
- **Validation**: Built-in card number validation (C10/Luhn)
- **Documentation**: Comprehensive documentation and examples

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Git (optional, for development)

### Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/Nsfr750/PySnoop.git
   cd PySnoop
   ```

2. Create and activate a virtual environment:

   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## 🏗️ Building the Application

PySnoop can be built into a standalone executable using Nuitka. We provide two build scripts:

### Debug Build

```bash
.\snoop_debug.bat
```

This creates a debug version of the application with the console window enabled for troubleshooting.

### Release Build

```bash
.\snoop.bat
```

This creates an optimized release version of the application.

### Build Outputs

- Debug build: `build\PySnoop_debug.exe`
- Release build: `build\PySnoop.exe`

## 🛠️ Development
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

### GUI Mode (Recommended)

```bash
python pysnoop_gui.py
```

### Command Line Interface

```bash
python pysnoop.py [options]
```

### Available Options

```bash
-h, --help      Show help message and exit
-v, --verbose   Enable verbose output
--version       Show version information
```

## 🔌 Supported Devices

- MSR605 Magnetic Stripe Card Reader/Writer
- Other HID-compatible card readers (experimental)

## 📚 Documentation

For detailed documentation, including API reference and usage examples, please visit the [documentation](https://nsfr750.github.io/PySnoop/ "PySnoop Documentation").

## 🤝 Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) to get started.

## 📄 License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Support

If you find this project useful, consider supporting its development:

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://paypal.me/3dmega)
[![Become a Patron](https://img.shields.io/badge/Support-Patreon-orange.svg)](https://www.patreon.com/Nsfr750)

## 📧 Contact

For questions or support, please open an issue or contact [Nsfr750](mailto:nsfr750@yandex.com).

## Credits

- Based on the original StripeSnoop project (http://stripesnoop.sourceforge.net)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
