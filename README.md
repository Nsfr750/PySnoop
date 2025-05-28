# Stripe Snoop 2.0 - Python Implementation

A Python implementation of the Stripe Snoop magstripe card reading and analysis tool.

## Features

- Read and decode magstripe card data from various reader types
- Support for multiple tracks (1, 2, and 3)
- Configurable reader interfaces (direct hardware and serial)
- XML-based configuration
- Extensible architecture for adding new reader types

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stripesnoop-py.git
   cd stripesnoop-py
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python main.py [options]
```

### Options

- `-v, --verbose`: Enable verbose output
- `-l, --loop`: Enable loop mode (continuously read cards)
- `-c, --config`: Specify a custom config file (default: config.xml)
- `-i, --input`: Read from input file instead of hardware

### Configuration

Edit the `config.xml` file to configure your reader. Example configurations are provided for different reader types.

## Reader Types

### Direct Hardware Reader

For connecting directly to parallel ports or game ports. Configure the pins for each track in `config.xml`.

### Serial Reader

For connecting to serial port readers. Configure the device path and settings in `config.xml`.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

This project uses flake8 for code style checking:

```bash
flake8 .
```

### Type Checking

This project uses mypy for static type checking:

```bash
mypy .
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original C++ implementation: [Stripe Snoop](http://stripesnoop.sourceforge.net/)
- Inspired by the work of Acidus and the MSB Labs team
