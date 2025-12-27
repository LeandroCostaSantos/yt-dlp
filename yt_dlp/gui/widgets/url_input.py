"""Widget de entrada de URL."""

import tkinter as tk
from tkinter import ttk

from ..styles import COLORS, FONTS, DIMENSIONS


class URLInput(ttk.Frame):
    """Frame com campo de entrada de URL e botão de análise."""

    def __init__(self, parent, on_analyze_callback, **kwargs):
        super().__init__(parent, **kwargs)

        self.on_analyze = on_analyze_callback
        self._create_widgets()

    def _create_widgets(self):
        """Cria os widgets do frame."""
        # Label
        label = ttk.Label(
            self,
            text='URL do Vídeo ou Playlist:',
            font=FONTS['heading'],
        )
        label.pack(anchor='w', pady=(0, 5))

        # Frame para input e botões
        input_frame = ttk.Frame(self)
        input_frame.pack(fill='x')

        # Entry de URL
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(
            input_frame,
            textvariable=self.url_var,
            font=FONTS['normal'],
            width=DIMENSIONS['entry_width'],
        )
        self.url_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.url_entry.bind('<Return>', lambda e: self._on_analyze_click())

        # Botão colar
        self.paste_btn = ttk.Button(
            input_frame,
            text='Colar',
            width=8,
            command=self._paste_from_clipboard,
        )
        self.paste_btn.pack(side='left', padx=(0, 5))

        # Botão analisar
        self.analyze_btn = ttk.Button(
            input_frame,
            text='Analisar',
            width=10,
            command=self._on_analyze_click,
        )
        self.analyze_btn.pack(side='left')

    def _paste_from_clipboard(self):
        """Cola o conteúdo da área de transferência."""
        try:
            clipboard = self.clipboard_get()
            self.url_var.set(clipboard.strip())
            self.url_entry.focus_set()
        except tk.TclError:
            pass

    def _on_analyze_click(self):
        """Chamado quando o botão analisar é clicado."""
        url = self.url_var.get().strip()
        if url:
            self.on_analyze(url)

    def get_url(self):
        """Retorna a URL atual."""
        return self.url_var.get().strip()

    def set_url(self, url):
        """Define a URL."""
        self.url_var.set(url)

    def clear(self):
        """Limpa o campo."""
        self.url_var.set('')

    def set_analyzing(self, analyzing):
        """Define estado de análise (habilita/desabilita controles)."""
        state = 'disabled' if analyzing else 'normal'
        self.url_entry.configure(state=state)
        self.paste_btn.configure(state=state)
        self.analyze_btn.configure(
            state=state,
            text='Analisando...' if analyzing else 'Analisar'
        )

    def focus(self):
        """Dá foco ao campo de URL."""
        self.url_entry.focus_set()
