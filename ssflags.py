"""
SSFlags - Global configuration flags for Stripe Snoop
"""

class SSFlags:
    """Global flags for Stripe Snoop configuration"""
    
    def __init__(self):
        self.VERBOSE = False  # Enable verbose output
        self.LOOP = False     # Enable loop mode
        self.CONFIG = False   # Use custom config file
        self.RAW = False      # Raw mode
        self.INPUT = False    # Input from file
        self._config_file = ""
        self._input_file = ""
    
    @property
    def config(self) -> str:
        """Get the configuration file path"""
        return self._config_file
    
    def set_config_file(self, filename: str) -> None:
        """Set the configuration file path"""
        self._config_file = filename
    
    @property
    def input_file(self) -> str:
        """Get the input file path"""
        return self._input_file
    
    def set_file_input(self, filename: str) -> None:
        """Set the input file path"""
        self._input_file = filename
