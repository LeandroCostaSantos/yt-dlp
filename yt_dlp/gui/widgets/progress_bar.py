"""Widget de barra de progresso para downloads."""

import tkinter as tk
from tkinter import ttk

from ..styles import FONTS, COLORS


class ProgressFrame(ttk.LabelFrame):
    """Frame com barra de progresso e informações de download."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, text='Progresso', **kwargs)

        self._create_widgets()
        self.reset()

    def _create_widgets(self):
        """Cria os widgets do frame."""
        inner_frame = ttk.Frame(self)
        inner_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Status do item atual
        self.status_label = ttk.Label(
            inner_frame,
            text='Aguardando...',
            font=FONTS['normal'],
        )
        self.status_label.pack(anchor='w')

        # Barra de progresso
        progress_frame = ttk.Frame(inner_frame)
        progress_frame.pack(fill='x', pady=5)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=400,
        )
        self.progress_bar.pack(side='left', fill='x', expand=True)

        self.percent_label = ttk.Label(
            progress_frame,
            text='0%',
            font=FONTS['normal'],
            width=6,
        )
        self.percent_label.pack(side='left', padx=(10, 0))

        # Frame de informações
        info_frame = ttk.Frame(inner_frame)
        info_frame.pack(fill='x')

        # Velocidade
        speed_frame = ttk.Frame(info_frame)
        speed_frame.pack(side='left', padx=(0, 20))

        ttk.Label(
            speed_frame, text='Velocidade:',
            font=FONTS['small'],
        ).pack(side='left')

        self.speed_label = ttk.Label(
            speed_frame, text='--',
            font=FONTS['small'],
        )
        self.speed_label.pack(side='left', padx=(5, 0))

        # Tamanho baixado
        size_frame = ttk.Frame(info_frame)
        size_frame.pack(side='left', padx=(0, 20))

        ttk.Label(
            size_frame, text='Baixado:',
            font=FONTS['small'],
        ).pack(side='left')

        self.size_label = ttk.Label(
            size_frame, text='--',
            font=FONTS['small'],
        )
        self.size_label.pack(side='left', padx=(5, 0))

        # ETA
        eta_frame = ttk.Frame(info_frame)
        eta_frame.pack(side='left')

        ttk.Label(
            eta_frame, text='Tempo restante:',
            font=FONTS['small'],
        ).pack(side='left')

        self.eta_label = ttk.Label(
            eta_frame, text='--',
            font=FONTS['small'],
        )
        self.eta_label.pack(side='left', padx=(5, 0))

        # Progresso da playlist (inicialmente oculto)
        self.playlist_frame = ttk.Frame(inner_frame)

        ttk.Label(
            self.playlist_frame, text='Playlist:',
            font=FONTS['small'],
        ).pack(side='left')

        self.playlist_label = ttk.Label(
            self.playlist_frame, text='',
            font=FONTS['small'],
        )
        self.playlist_label.pack(side='left', padx=(5, 0))

    def update_progress(self, data):
        """
        Atualiza a barra de progresso com dados do hook.

        Args:
            data: Dicionário do progress_hook do yt-dlp
        """
        status = data.get('status', '')

        if status == 'downloading':
            # Porcentagem
            percent_str = data.get('_percent_str', '0%').strip()
            try:
                percent = float(percent_str.replace('%', ''))
            except ValueError:
                percent = 0

            self.progress_var.set(percent)
            self.percent_label.configure(text=f'{percent:.1f}%')

            # Velocidade
            speed = data.get('_speed_str', '--')
            self.speed_label.configure(text=speed)

            # Tamanho
            downloaded = data.get('_downloaded_bytes_str', '--')
            total = data.get('_total_bytes_str') or data.get('_total_bytes_estimate_str', '')
            if total:
                self.size_label.configure(text=f'{downloaded} / {total}')
            else:
                self.size_label.configure(text=downloaded)

            # ETA
            eta = data.get('_eta_str', '--')
            self.eta_label.configure(text=eta)

            # Título
            info = data.get('info_dict', {})
            title = info.get('title', 'Baixando...')
            if len(title) > 50:
                title = title[:47] + '...'
            self.status_label.configure(text=f'Baixando: {title}')

        elif status == 'finished':
            self.progress_var.set(100)
            self.percent_label.configure(text='100%')
            self.status_label.configure(text='Download concluído, processando...')
            self.speed_label.configure(text='--')
            self.eta_label.configure(text='--')

        elif status == 'error':
            self.status_label.configure(text='Erro no download')

    def set_playlist_progress(self, current, total):
        """
        Atualiza o progresso da playlist.

        Args:
            current: Índice do item atual (1-based)
            total: Total de itens na playlist
        """
        if total > 1:
            self.playlist_frame.pack(fill='x', pady=(5, 0))
            self.playlist_label.configure(text=f'{current} de {total}')
        else:
            self.playlist_frame.pack_forget()

    def set_indeterminate(self, indeterminate=True):
        """Define modo indeterminado (para operações sem progresso conhecido)."""
        if indeterminate:
            self.progress_bar.configure(mode='indeterminate')
            self.progress_bar.start(10)
        else:
            self.progress_bar.stop()
            self.progress_bar.configure(mode='determinate')

    def set_status(self, message):
        """Define mensagem de status."""
        self.status_label.configure(text=message)

    def reset(self):
        """Reseta a barra de progresso para o estado inicial."""
        self.progress_var.set(0)
        self.percent_label.configure(text='0%')
        self.speed_label.configure(text='--')
        self.size_label.configure(text='--')
        self.eta_label.configure(text='--')
        self.status_label.configure(text='Aguardando...')
        self.playlist_frame.pack_forget()
        self.set_indeterminate(False)

    def set_complete(self, success=True, message=None):
        """Define estado de conclusão."""
        self.progress_var.set(100 if success else 0)
        self.percent_label.configure(text='100%' if success else '0%')
        self.speed_label.configure(text='--')
        self.eta_label.configure(text='--')

        if message:
            self.status_label.configure(text=message)
        else:
            self.status_label.configure(
                text='Download concluído!' if success else 'Download falhou'
            )
