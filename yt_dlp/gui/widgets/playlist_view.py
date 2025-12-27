"""Widget para visualização e seleção de itens de playlist."""

import tkinter as tk
from tkinter import ttk

from ..styles import FONTS, COLORS, format_duration


class PlaylistView(ttk.LabelFrame):
    """Frame para exibir e selecionar itens de uma playlist."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, text='Playlist', **kwargs)

        self.items = []
        self.checkboxes = []
        self._create_widgets()

    def _create_widgets(self):
        """Cria os widgets do frame."""
        # Frame de botões
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(
            button_frame,
            text='Selecionar Todos',
            command=self._select_all,
            width=15,
        ).pack(side='left', padx=(0, 5))

        ttk.Button(
            button_frame,
            text='Desmarcar Todos',
            command=self._deselect_all,
            width=15,
        ).pack(side='left')

        self.count_label = ttk.Label(
            button_frame,
            text='0 itens',
            font=FONTS['small'],
        )
        self.count_label.pack(side='right')

        # Frame com scrollbar para lista
        list_frame = ttk.Frame(self)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Canvas e scrollbar
        self.canvas = tk.Canvas(
            list_frame,
            highlightthickness=0,
            bg=COLORS['bg'],
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient='vertical',
            command=self.canvas.yview,
        )

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor='nw',
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Bind para redimensionar o frame interno
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        # Bind para scroll com mousewheel
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)

        scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

    def _on_canvas_configure(self, event):
        """Redimensiona o frame interno quando o canvas muda de tamanho."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """Scroll com mousewheel."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def _select_all(self):
        """Seleciona todos os itens."""
        for var, _ in self.checkboxes:
            var.set(True)
        self._update_count()

    def _deselect_all(self):
        """Desmarca todos os itens."""
        for var, _ in self.checkboxes:
            var.set(False)
        self._update_count()

    def _update_count(self):
        """Atualiza o contador de itens selecionados."""
        selected = sum(1 for var, _ in self.checkboxes if var.get())
        total = len(self.checkboxes)
        self.count_label.configure(text=f'{selected}/{total} selecionados')

    def set_items(self, entries):
        """
        Define os itens da playlist.

        Args:
            entries: Lista de dicionários com informações dos vídeos
                     Cada item deve ter: 'title', 'duration' (opcional), 'id'
        """
        # Limpar itens anteriores
        self.clear()

        self.items = entries or []

        for i, entry in enumerate(self.items, 1):
            item_frame = ttk.Frame(self.scrollable_frame)
            item_frame.pack(fill='x', pady=2)

            # Checkbox
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(
                item_frame,
                variable=var,
                command=self._update_count,
            )
            cb.pack(side='left')

            # Número
            ttk.Label(
                item_frame,
                text=f'{i}.',
                font=FONTS['small'],
                width=4,
            ).pack(side='left')

            # Título
            title = entry.get('title', 'Sem título')
            if len(title) > 60:
                title = title[:57] + '...'

            ttk.Label(
                item_frame,
                text=title,
                font=FONTS['normal'],
            ).pack(side='left', fill='x', expand=True)

            # Duração
            duration = entry.get('duration')
            duration_str = format_duration(duration) if duration else '--:--'

            ttk.Label(
                item_frame,
                text=duration_str,
                font=FONTS['small'],
                width=8,
            ).pack(side='right')

            self.checkboxes.append((var, entry))

        self._update_count()

        # Atualizar título do frame
        self.configure(text=f'Playlist ({len(self.items)} itens)')

    def clear(self):
        """Limpa todos os itens."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.checkboxes = []
        self.items = []
        self.configure(text='Playlist')
        self.count_label.configure(text='0 itens')

    def get_selected_items(self):
        """
        Retorna os itens selecionados.

        Returns:
            Lista de dicionários dos itens selecionados
        """
        return [entry for var, entry in self.checkboxes if var.get()]

    def get_selected_indices(self):
        """
        Retorna os índices (1-based) dos itens selecionados.

        Returns:
            Lista de índices
        """
        return [i + 1 for i, (var, _) in enumerate(self.checkboxes) if var.get()]

    def get_playlist_items_string(self):
        """
        Retorna string de itens selecionados para yt-dlp.

        Returns:
            String no formato '1,2,5-8' ou None se todos selecionados
        """
        selected = self.get_selected_indices()
        total = len(self.checkboxes)

        # Se todos selecionados, retorna None (baixar tudo)
        if len(selected) == total:
            return None

        # Se nenhum selecionado
        if not selected:
            return ''

        # Converter para ranges (ex: 1,2,3,5,6,7 -> 1-3,5-7)
        ranges = []
        start = selected[0]
        end = selected[0]

        for idx in selected[1:]:
            if idx == end + 1:
                end = idx
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f'{start}-{end}')
                start = end = idx

        # Adicionar último range
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f'{start}-{end}')

        return ','.join(ranges)

    def has_items(self):
        """Retorna True se há itens na playlist."""
        return len(self.items) > 0

    def get_selected_count(self):
        """Retorna o número de itens selecionados."""
        return sum(1 for var, _ in self.checkboxes if var.get())
