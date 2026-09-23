"""Human-readable, cryptographically random invitation codes (60 bits)."""

import secrets

ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_code():
    return ''.join(secrets.choice(ALPHABET) for _ in range(12))


def normalize_code(value):
    if not isinstance(value, str) or len(value) > 32:
        raise ValueError('Enter the 12-character room code, for example XXXX-XXXX-XXXX.')
    value = value.strip().upper().replace('-', '')
    if len(value) != 12 or any(char not in ALPHABET for char in value):
        raise ValueError('Enter the 12-character room code, for example XXXX-XXXX-XXXX.')
    return value


def display_code(value):
    value = normalize_code(value)
    return '-'.join(value[index:index + 4] for index in range(0, 12, 4))
