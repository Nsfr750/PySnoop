'''
Security Module

Provides cryptographic utilities and secure storage for sensitive data.
'''
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

from .secure_storage import (
    SecureStorage,
    SecureStorageError,
    get_secure_storage
)

__all__ = [
    'generate_key_from_password',
    'encrypt_data',
    'decrypt_data',
    'hash_sensitive_data',
    'secure_compare',
    'CryptoError',
    'EncryptionError',
    'DecryptionError',
    'SecureStorage',
    'SecureStorageError',
    'get_secure_storage'
]
