"""
yt-dlp GUI - Interface gráfica para o yt-dlp

Este módulo fornece uma interface gráfica usando Tkinter para facilitar
o uso do yt-dlp sem necessidade de linha de comando.
"""

from .app import YTDLPApp


def launch():
    """Inicia a aplicação GUI do yt-dlp."""
    app = YTDLPApp()
    app.mainloop()


__all__ = ['launch', 'YTDLPApp']
