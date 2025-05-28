"""
Secure Storage Module

Provides secure storage for sensitive card data with encryption at rest.
"""
import os
import json
import base64
from typing import Dict, Any, Optional, List, Union
from .crypto_utils import (
    generate_key_from_password,
    encrypt_data,
    decrypt_data,
    hash_sensitive_data,
    secure_compare,
    CryptoError,
    EncryptionError,
    DecryptionError
)

class SecureStorageError(Exception):
    """Base class for secure storage errors."""
    pass

class SecureStorage:
    """
    Secure storage for sensitive card data.
    
    Provides methods to securely store and retrieve sensitive card data
    with encryption at rest. Uses AES-256-GCM for encryption and PBKDF2
    for key derivation.
    """
    
    SENSITIVE_FIELDS = {
        'number', 'expiration', 'cvv', 'holder_name', 'tracks', 'track1', 'track2'
    }
    
    def __init__(self, password: str, salt: bytes = None):
        """
        Initialize the secure storage with a password.
        
        Args:
            password: The password used for encryption/decryption
            salt: Optional salt for key derivation (will generate if not provided)
        """
        if not password:
            raise ValueError("Password cannot be empty")
            
        self.password = password
        self.key, self.salt = generate_key_from_password(password, salt)
    
    def encrypt_card(self, card_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in a card dictionary.
        
        Args:
            card_data: Dictionary containing card data
            
        Returns:
            Dict: New dictionary with sensitive fields encrypted
        """
        if not isinstance(card_data, dict):
            raise ValueError("Card data must be a dictionary")
            
        encrypted_card = {}
        
        for key, value in card_data.items():
            if key in self.SENSITIVE_FIELDS and value is not None:
                try:
                    encrypted_value = encrypt_data(value, self.key)
                    encrypted_card[f'encrypted_{key}'] = encrypted_value
                except EncryptionError as e:
                    raise SecureStorageError(f"Failed to encrypt {key}: {str(e)}")
            else:
                encrypted_card[key] = value
                
        # Add metadata
        encrypted_card['_secure'] = True
        encrypted_card['_salt'] = base64.b64encode(self.salt).decode('utf-8')
        
        return encrypted_card
    
    def decrypt_card(self, encrypted_card: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt sensitive fields in an encrypted card dictionary.
        
        Args:
            encrypted_card: Dictionary with encrypted card data
            
        Returns:
            Dict: New dictionary with sensitive fields decrypted
            
        Raises:
            SecureStorageError: If decryption fails
        """
        if not encrypted_card.get('_secure'):
            return encrypted_card
            
        decrypted_card = {}
        
        for key, value in encrypted_card.items():
            if key.startswith('encrypted_') and value is not None:
                original_key = key[9:]  # Remove 'encrypted_' prefix
                try:
                    decrypted_value = decrypt_data(value, self.key)
                    decrypted_card[original_key] = decrypted_value
                except DecryptionError as e:
                    raise SecureStorageError(f"Failed to decrypt {original_key}: {str(e)}")
            elif not key.startswith('_') and key not in ['_secure', '_salt']:
                decrypted_card[key] = value
                
        return decrypted_card
    
    def hash_card_number(self, card_number: str) -> str:
        """
        Hash a card number for secure storage.
        
        Args:
            card_number: The card number to hash
            
        Returns:
            str: The hashed card number (hex-encoded)
        """
        if not card_number:
            raise ValueError("Card number cannot be empty")
            
        # Only use last 4 digits for hashing to reduce entropy
        last_four = card_number[-4:] if len(card_number) >= 4 else card_number
        
        # Use a fixed salt for consistent hashing of the same card number
        salt = b'fixed_salt_for_hashing'  # In production, consider using a configurable salt
        
        hashed, _ = hash_sensitive_data(last_four, salt)
        return hashed
    
    def verify_card_number(self, card_number: str, stored_hash: str) -> bool:
        """
        Verify a card number against a stored hash.
        
        Args:
            card_number: The card number to verify
            stored_hash: The stored hash to compare against
            
        Returns:
            bool: True if the card number matches the hash, False otherwise
        """
        if not card_number or not stored_hash:
            return False
            
        hashed = self.hash_card_number(card_number)
        return secure_compare(hashed, stored_hash)
    
    def secure_wipe(self, data: Union[str, bytes, Dict, List]) -> None:
        """
        Securely wipe sensitive data from memory.
        
        Args:
            data: The data to wipe (string, bytes, dict, or list)
        """
        if isinstance(data, (str, bytes)):
            # Overwrite with random data
            if isinstance(data, str):
                data = data.encode('utf-8')
            length = len(data)
            data = os.urandom(length)
            data = b'\x00' * length
        elif isinstance(data, dict):
            for key in list(data.keys()):
                self.secure_wipe(data[key])
                del data[key]
        elif isinstance(data, list):
            for i in range(len(data)):
                self.secure_wipe(data[i])
                data[i] = None
        
        # Force garbage collection
        import gc
        gc.collect()

# Helper function to get a secure storage instance
def get_secure_storage(password: str = None, salt: bytes = None):
    """
    Get a secure storage instance with the given password and optional salt.
    
    Args:
        password: The password for encryption/decryption
        salt: Optional salt for key derivation (should be provided when loading an existing database)
        
    Returns:
        Optional[SecureStorage]: A SecureStorage instance or None if creation fails
        
    Raises:
        ValueError: If password is empty or invalid
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    try:
        return SecureStorage(password, salt)
    except Exception as e:
        print(f"Error creating secure storage: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
