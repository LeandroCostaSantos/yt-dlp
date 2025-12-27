#!/usr/bin/env python3
"""
Script para iniciar a GUI do yt-dlp.

Uso:
    python -m yt_dlp.gui_main

Ou diretamente:
    python yt_dlp/gui_main.py
"""

import sys
import os

# Adicionar diretório pai ao path para imports funcionarem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yt_dlp.gui import launch


def main():
    """Ponto de entrada principal."""
    try:
        launch()
    except ImportError as e:
        print(f'Erro ao importar dependências: {e}')
        print('\nCertifique-se de que o Pillow está instalado:')
        print('  pip install Pillow')
        sys.exit(1)
    except Exception as e:
        print(f'Erro ao iniciar a GUI: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
