"""
Cryptographic Utilities for Card Data

Provides encryption and decryption functionality for sensitive card data.
Uses AES-256-GCM for authenticated encryption.
"""
import os
import base64
import json
from typing import Dict, Any, Optional, Union
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import secrets

class CryptoError(Exception):
    """Base class for crypto-related errors."""
    pass

class EncryptionError(CryptoError):
    """Raised when encryption fails."""
    pass

class DecryptionError(CryptoError):
    """Raised when decryption fails."""
    pass

def generate_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """
    Generate a secure encryption key from a password.
    
    Args:
        password: The password to derive the key from
        salt: Optional salt (will generate if not provided)
        
    Returns:
        tuple: (key, salt) where key is the derived key and salt is the used salt
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if not salt:
        salt = secrets.token_bytes(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256 bits for AES-256
        salt=salt,
        iterations=600000,  # High iteration count for security
        backend=default_backend()
    )
    
    key = kdf.derive(password.encode('utf-8'))
    return key, salt

def encrypt_data(data: Union[str, Dict[str, Any]], key: bytes) -> str:
    """
    Encrypt sensitive data.
    
    Args:
        data: The data to encrypt (string or dictionary)
        key: The encryption key (32 bytes for AES-256)
        
    Returns:
        str: Base64-encoded encrypted data with IV and auth tag
    """
    if isinstance(data, dict):
        data_str = json.dumps(data)
    else:
        data_str = str(data)
    
    # Generate a random IV
    iv = os.urandom(16)
    
    # Create cipher and encrypt
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Pad the data
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data_str.encode('utf-8')) + padder.finalize()
    
    # Encrypt and finalize
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Get the authentication tag
    auth_tag = encryptor.tag
    
    # Combine IV + auth_tag + ciphertext and encode as base64
    encrypted_data = iv + auth_tag + ciphertext
    return base64.b64encode(encrypted_data).decode('utf-8')

def decrypt_data(encrypted_data: str, key: bytes) -> Union[str, Dict[str, Any]]:
    """
    Decrypt data that was encrypted with encrypt_data.
    
    Args:
        encrypted_data: Base64-encoded encrypted data
        key: The encryption key (32 bytes for AES-256)
        
    Returns:
        Union[str, Dict]: The decrypted data (string or dictionary)
        
    Raises:
        DecryptionError: If decryption fails
    """
    try:
        # Decode base64
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # Extract IV, auth tag, and ciphertext
        iv = encrypted_bytes[:16]
        auth_tag = encrypted_bytes[16:32]
        ciphertext = encrypted_bytes[32:]
        
        # Create cipher and decrypt
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag=auth_tag),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad the data
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        # Try to parse as JSON, return as string if not valid JSON
        try:
            return json.loads(plaintext.decode('utf-8'))
        except json.JSONDecodeError:
            return plaintext.decode('utf-8')
            
    except Exception as e:
        raise DecryptionError(f"Decryption failed: {str(e)}")

def hash_sensitive_data(data: str, salt: bytes = None) -> tuple[str, bytes]:
    """
    Hash sensitive data using HMAC-SHA256.
    
    Args:
        data: The data to hash
        salt: Optional salt (will generate if not provided)
        
    Returns:
        tuple: (hash, salt) where hash is the hex-encoded hash and salt is the used salt
    """
    if not salt:
        salt = secrets.token_bytes(16)
    
    h = hmac.HMAC(salt, hashes.SHA256(), backend=default_backend())
    h.update(data.encode('utf-8'))
    return h.finalize().hex(), salt

def secure_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        bool: True if strings are equal, False otherwise
    """
    return secrets.compare_digest(a, b)
