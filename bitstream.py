"""
Bitstream class for handling bit-level operations on magstripe data
"""

from typing import List, Optional, Union, Tuple

class Bitstream:
    """
    A class for reading and manipulating bit-level data from a byte stream.
    """
    
    def __init__(self, data: bytes = b""):
        """
        Initialize a new Bitstream instance.
        
        Args:
            data: The binary data to work with
        """
        self.data = bytearray(data)
        self.position = 0  # Current bit position
        self.bit_order = 'msb'  # Default to most significant bit first
    
    def rewind(self) -> None:
        """Reset the bit position to the start of the stream."""
        self.position = 0
        
    def eof(self) -> bool:
        """Check if we've reached the end of the bitstream.
        
        Returns:
            bool: True if at end of stream, False otherwise
        """
        return self.position >= len(self.data) * 8
    
    def read_bit(self) -> int:
        """
        Read a single bit from the stream.
        
        Returns:
            int: The bit value (0 or 1)
        """
        if self.position >= len(self.data) * 8:
            raise IndexError("Attempt to read past end of bitstream")
            
        byte_pos = self.position // 8
        bit_pos = self.position % 8
        self.position += 1
        
        if self.bit_order == 'msb':
            return (self.data[byte_pos] >> (7 - bit_pos)) & 1
        else:  # lsb
            return (self.data[byte_pos] >> bit_pos) & 1
    
    def read_bits(self, count: int) -> int:
        """
        Read multiple bits from the stream.
        
        Args:
            count: Number of bits to read (up to 64)
            
        Returns:
            int: The bits read as an integer
        """
        if count > 64:
            raise ValueError("Cannot read more than 64 bits at once")
            
        result = 0
        for _ in range(count):
            result = (result << 1) | self.read_bit()
        return result
    
    def read_byte(self) -> int:
        """
        Read a single byte (8 bits) from the stream.
        
        Returns:
            int: The byte value (0-255)
        """
        return self.read_bits(8)
    
    def read_bytes(self, count: int) -> bytes:
        """
        Read multiple bytes from the stream.
        
        Args:
            count: Number of bytes to read
            
        Returns:
            bytes: The bytes read
        """
        return bytes(self.read_byte() for _ in range(count))
    
    def write_bit(self, bit: int) -> None:
        """
        Write a single bit to the stream.
        
        Args:
            bit: The bit value (0 or 1)
        """
        if bit not in (0, 1):
            raise ValueError("Bit must be 0 or 1")
            
        byte_pos = self.position // 8
        bit_pos = self.position % 8
        
        # Expand data if needed
        if byte_pos >= len(self.data):
            self.data.append(0)
        
        if self.bit_order == 'msb':
            mask = 1 << (7 - bit_pos)
            if bit:
                self.data[byte_pos] |= mask
            else:
                self.data[byte_pos] &= ~mask
        else:  # lsb
            mask = 1 << bit_pos
            if bit:
                self.data[byte_pos] |= mask
            else:
                self.data[byte_pos] &= ~mask
                
        self.position += 1
    
    def write_bits(self, value: int, count: int) -> None:
        """
        Write multiple bits to the stream.
        
        Args:
            value: The bits to write
            count: Number of bits to write
        """
        if count > 64:
            raise ValueError("Cannot write more than 64 bits at once")
            
        mask = 1 << (count - 1)
        for _ in range(count):
            self.write_bit(1 if (value & mask) else 0)
            value <<= 1
    
    def write_byte(self, value: int) -> None:
        """
        Write a single byte to the stream.
        
        Args:
            value: The byte value (0-255)
        """
        self.write_bits(value, 8)
    
    def write_bytes(self, data: bytes) -> None:
        """
        Write multiple bytes to the stream.
        
        Args:
            data: The bytes to write
        """
        for byte in data:
            self.write_byte(byte)
    
    def seek(self, position: int) -> None:
        """
        Move to a specific bit position in the stream.
        
        Args:
            position: The bit position to seek to
        """
        self.position = position
    
    def tell(self) -> int:
        """
        Get the current bit position in the stream.
        
        Returns:
            int: The current bit position
        """
        return self.position
    
    def remaining_bits(self) -> int:
        """
        Get the number of bits remaining in the stream.
        
        Returns:
            int: Number of bits remaining
        """
        return max(0, len(self.data) * 8 - self.position)
    
    def to_bytes(self) -> bytes:
        """
        Convert the bitstream to bytes.
        
        Returns:
            bytes: The bitstream as bytes
        """
        return bytes(self.data)
    
    def __len__(self) -> int:
        """
        Get the length of the bitstream in bits.
        
        Returns:
            int: Length in bits
        """
        return len(self.data) * 8
    
    def __str__(self) -> str:
        """
        Get a string representation of the bitstream.
        
        Returns:
            str: String representation
        """
        return ' '.join(f'{byte:08b}' for byte in self.data)
