#!/usr/bin/env python3
"""
Generate a secure Django SECRET_KEY
Run this script to generate a new secret key for production use.
"""

from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    secret_key = get_random_secret_key()
    print("=" * 70)
    print("Generated Django SECRET_KEY:")
    print("=" * 70)
    print(secret_key)
    print("=" * 70)
    print("\nCopy this key to your .env file:")
    print(f"SECRET_KEY={secret_key}")
    print("=" * 70)
