"""
Tests for the Bitstream class
"""
import pytest
from bitstream import Bitstream

def test_bitstream_initialization():
    """Test Bitstream initialization with bytes"""
    data = b'\x01\x02\x03\x04'
    bs = Bitstream(data)
    assert bs.data == bytearray(data)
    assert bs.position == 0

def test_read_bit():
    """Test reading individual bits"""
    # 0b10101010
    bs = Bitstream(b'\xAA')
    assert bs.read_bit() == 1
    assert bs.read_bit() == 0
    assert bs.read_bit() == 1
    assert bs.read_bit() == 0
    assert bs.position == 4

def test_read_bits():
    """Test reading multiple bits"""
    # 0b10101010 0b11001100
    bs = Bitstream(b'\xAA\xCC')
    assert bs.read_bits(4) == 0b1010
    assert bs.read_bits(4) == 0b1010
    assert bs.read_bits(8) == 0b11001100

def test_read_byte():
    """Test reading a full byte"""
    bs = Bitstream(b'ABC')
    assert bs.read_byte() == ord('A')
    assert bs.read_byte() == ord('B')
    assert bs.read_byte() == ord('C')

def test_write_bit():
    """Test writing individual bits"""
    bs = Bitstream()
    bs.write_bit(1)
    bs.write_bit(0)
    bs.write_bit(1)
    bs.write_bit(0)
    bs.position = 0
    assert bs.read_bit() == 1
    assert bs.read_bit() == 0
    assert bs.read_bit() == 1
    assert bs.read_bit() == 0

def test_write_bits():
    """Test writing multiple bits"""
    bs = Bitstream()
    bs.write_bits(0b1010, 4)
    bs.write_bits(0b1100, 4)
    bs.position = 0
    assert bs.read_byte() == 0b10101100

def test_lsb_bit_order():
    """Test LSB (Least Significant Bit) first mode"""
    bs = Bitstream()
    bs.bit_order = 'lsb'
    bs.write_bits(0b1010, 4)
    bs.position = 0
    assert bs.read_bits(4) == 0b1010  # In LSB, first bit is LSB

def test_peek_bit():
    """Test peeking at the next bit without advancing position"""
    bs = Bitstream(b'\xF0')  # 11110000
    assert bs.peek_bit() == 1
    assert bs.position == 0  # Position shouldn't change
    assert bs.read_bit() == 1  # Now actually read it
    assert bs.position == 1
