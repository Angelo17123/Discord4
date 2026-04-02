#!/usr/bin/env python3
"""Script para verificar que las dependencias estan instaladas."""

import sys

def test_imports():
    """Probar importaciones criticas."""
    try:
        import discord
        print(f"[OK] discord.py-self version: {discord.__version__}")
    except ImportError as e:
        print(f"[ERROR] Error importando discord: {e}")
        return False

    try:
        from dotenv import load_dotenv
        print("[OK] python-dotenv instalado")
    except ImportError as e:
        print(f"[ERROR] Error importando dotenv: {e}")
        return False

    try:
        import nacl
        print("[OK] PyNaCl instalado (soporte de voz)")
    except ImportError as e:
        print(f"[WARN] PyNaCl no instalado (sin soporte de voz): {e}")

    print("\nTodas las importaciones criticas funcionan.")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
