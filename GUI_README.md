# Card Database Manager - GUI Application

A secure and user-friendly graphical interface for managing payment card information with strong encryption.

## Features

- **Secure Storage**: All card data is encrypted using strong encryption algorithms
- **Intuitive Interface**: Easy-to-use interface for managing your card database
- **Search & Filter**: Quickly find cards using the search functionality
- **Card Details**: View detailed information about each card
- **Secure Password Protection**: Protect your database with a strong password

## Requirements

- Python 3.8 or higher
- PyQt6
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SS-V2-py
   ```

2. Install the required dependencies:
   ```bash
   # Install core dependencies
   pip install -r requirements.txt
   
   # Install GUI-specific dependencies
   pip install -r requirements-gui.txt
   ```

## Usage

1. Run the GUI application:
   ```bash
   python gui_main.py
   ```

2. Create a new database or open an existing one
3. Add, edit, or delete cards as needed
4. Your data is automatically encrypted and saved

## Security

- All card data is encrypted before being stored
- Strong password protection for database files
- No card data is ever transmitted over the network

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
