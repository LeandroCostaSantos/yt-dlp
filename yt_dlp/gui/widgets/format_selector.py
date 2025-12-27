"""Widget de seleção de formato e qualidade."""

import tkinter as tk
from tkinter import ttk, filedialog

from ..styles import (
    FONTS, VIDEO_QUALITIES, AUDIO_QUALITIES,
    VIDEO_FORMATS, AUDIO_FORMATS, COUNTRIES, SUBTITLE_LANGUAGES
)


class FormatSelector(ttk.LabelFrame):
    """Frame para seleção de formato, qualidade e opções de download."""

    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, text='Opções de Download', **kwargs)

        self.config = config
        self._create_widgets()
        self._load_from_config()

    def _create_widgets(self):
        """Cria os widgets do frame."""
        # Frame principal com duas colunas
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Coluna esquerda - Formato e Qualidade
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Tipo de saída (Vídeo/Áudio)
        type_frame = ttk.Frame(left_frame)
        type_frame.pack(fill='x', pady=5)

        ttk.Label(type_frame, text='Tipo:', font=FONTS['normal']).pack(side='left')

        self.output_type = tk.StringVar(value='video')
        ttk.Radiobutton(
            type_frame, text='Vídeo', variable=self.output_type,
            value='video', command=self._on_type_change
        ).pack(side='left', padx=(10, 5))
        ttk.Radiobutton(
            type_frame, text='Apenas Áudio', variable=self.output_type,
            value='audio', command=self._on_type_change
        ).pack(side='left')

        # Qualidade de vídeo
        self.video_quality_frame = ttk.Frame(left_frame)
        self.video_quality_frame.pack(fill='x', pady=5)

        ttk.Label(
            self.video_quality_frame, text='Qualidade do vídeo:',
            font=FONTS['normal']
        ).pack(side='left')

        self.video_quality = tk.StringVar()
        self.video_quality_combo = ttk.Combobox(
            self.video_quality_frame,
            textvariable=self.video_quality,
            values=[q[0] for q in VIDEO_QUALITIES],
            state='readonly',
            width=25,
        )
        self.video_quality_combo.pack(side='left', padx=(10, 0))
        self.video_quality_combo.current(2)  # 1080p padrão

        # Formato de vídeo
        self.video_format_frame = ttk.Frame(left_frame)
        self.video_format_frame.pack(fill='x', pady=5)

        ttk.Label(
            self.video_format_frame, text='Formato do vídeo:',
            font=FONTS['normal']
        ).pack(side='left')

        self.video_format = tk.StringVar()
        self.video_format_combo = ttk.Combobox(
            self.video_format_frame,
            textvariable=self.video_format,
            values=[f[0] for f in VIDEO_FORMATS],
            state='readonly',
            width=25,
        )
        self.video_format_combo.pack(side='left', padx=(10, 0))
        self.video_format_combo.current(0)  # MP4 padrão

        # Qualidade de áudio
        audio_quality_frame = ttk.Frame(left_frame)
        audio_quality_frame.pack(fill='x', pady=5)

        ttk.Label(
            audio_quality_frame, text='Qualidade do áudio:',
            font=FONTS['normal']
        ).pack(side='left')

        self.audio_quality = tk.StringVar()
        self.audio_quality_combo = ttk.Combobox(
            audio_quality_frame,
            textvariable=self.audio_quality,
            values=[q[0] for q in AUDIO_QUALITIES],
            state='readonly',
            width=25,
        )
        self.audio_quality_combo.pack(side='left', padx=(10, 0))
        self.audio_quality_combo.current(2)  # 192kbps padrão

        # Formato de áudio (para modo áudio)
        self.audio_format_frame = ttk.Frame(left_frame)
        self.audio_format_frame.pack(fill='x', pady=5)
        self.audio_format_frame.pack_forget()  # Oculto inicialmente

        ttk.Label(
            self.audio_format_frame, text='Formato do áudio:',
            font=FONTS['normal']
        ).pack(side='left')

        self.audio_format = tk.StringVar()
        self.audio_format_combo = ttk.Combobox(
            self.audio_format_frame,
            textvariable=self.audio_format,
            values=[f[0] for f in AUDIO_FORMATS],
            state='readonly',
            width=25,
        )
        self.audio_format_combo.pack(side='left', padx=(10, 0))
        self.audio_format_combo.current(0)  # MP3 padrão

        # Coluna direita - Opções avançadas
        right_frame = ttk.LabelFrame(main_frame, text='Opções Avançadas')
        right_frame.pack(side='left', fill='both', padx=(10, 0))

        options_inner = ttk.Frame(right_frame)
        options_inner.pack(fill='both', padx=10, pady=5)

        # Geo-bypass
        geo_frame = ttk.Frame(options_inner)
        geo_frame.pack(fill='x', pady=2)

        self.geo_bypass = tk.BooleanVar()
        self.geo_check = ttk.Checkbutton(
            geo_frame, text='Geo-bypass',
            variable=self.geo_bypass,
            command=self._on_geo_toggle,
        )
        self.geo_check.pack(side='left')

        self.geo_country = tk.StringVar()
        self.geo_combo = ttk.Combobox(
            geo_frame,
            textvariable=self.geo_country,
            values=[c[0] for c in COUNTRIES],
            state='disabled',
            width=15,
        )
        self.geo_combo.pack(side='left', padx=(10, 0))
        self.geo_combo.current(0)  # Brasil padrão

        # Livestream
        self.livestream = tk.BooleanVar()
        ttk.Checkbutton(
            options_inner, text='Gravar livestream (do início)',
            variable=self.livestream,
        ).pack(anchor='w', pady=2)

        # Legendas
        sub_frame = ttk.Frame(options_inner)
        sub_frame.pack(fill='x', pady=2)

        self.download_subs = tk.BooleanVar()
        self.sub_check = ttk.Checkbutton(
            sub_frame, text='Baixar legendas',
            variable=self.download_subs,
            command=self._on_subs_toggle,
        )
        self.sub_check.pack(side='left')

        self.sub_language = tk.StringVar()
        self.sub_combo = ttk.Combobox(
            sub_frame,
            textvariable=self.sub_language,
            values=[l[0] for l in SUBTITLE_LANGUAGES],
            state='disabled',
            width=12,
        )
        self.sub_combo.pack(side='left', padx=(10, 0))
        self.sub_combo.current(0)  # Português padrão

        # Embutir thumbnail
        self.embed_thumb = tk.BooleanVar()
        ttk.Checkbutton(
            options_inner, text='Embutir thumbnail',
            variable=self.embed_thumb,
        ).pack(anchor='w', pady=2)

        # Pasta de destino
        dest_frame = ttk.Frame(self)
        dest_frame.pack(fill='x', padx=10, pady=(10, 5))

        ttk.Label(
            dest_frame, text='Pasta de destino:',
            font=FONTS['normal']
        ).pack(side='left')

        self.dest_path = tk.StringVar()
        self.dest_entry = ttk.Entry(
            dest_frame,
            textvariable=self.dest_path,
            width=40,
        )
        self.dest_entry.pack(side='left', padx=(10, 5), fill='x', expand=True)

        ttk.Button(
            dest_frame, text='Procurar...',
            command=self._browse_folder,
            width=10,
        ).pack(side='left')

    def _on_type_change(self):
        """Chamado quando o tipo de saída muda."""
        if self.output_type.get() == 'audio':
            self.video_quality_frame.pack_forget()
            self.video_format_frame.pack_forget()
            self.audio_format_frame.pack(fill='x', pady=5, after=self.video_quality_frame)
        else:
            self.audio_format_frame.pack_forget()
            self.video_quality_frame.pack(fill='x', pady=5)
            self.video_format_frame.pack(fill='x', pady=5, after=self.video_quality_frame)

    def _on_geo_toggle(self):
        """Chamado quando geo-bypass é alternado."""
        state = 'readonly' if self.geo_bypass.get() else 'disabled'
        self.geo_combo.configure(state=state)

    def _on_subs_toggle(self):
        """Chamado quando download de legendas é alternado."""
        state = 'readonly' if self.download_subs.get() else 'disabled'
        self.sub_combo.configure(state=state)

    def _browse_folder(self):
        """Abre diálogo para selecionar pasta de destino."""
        folder = filedialog.askdirectory(
            title='Selecionar pasta de destino',
            initialdir=self.dest_path.get() or None,
        )
        if folder:
            self.dest_path.set(folder)

    def _load_from_config(self):
        """Carrega valores do config."""
        self.dest_path.set(self.config.get('download_path', ''))
        self.output_type.set(self.config.get('output_format', 'video'))
        self.geo_bypass.set(self.config.get('geo_bypass', False))
        self.embed_thumb.set(self.config.get('embed_thumbnail', False))
        self.download_subs.set(self.config.get('download_subtitles', False))

        # Atualizar estados
        self._on_type_change()
        self._on_geo_toggle()
        self._on_subs_toggle()

    def save_to_config(self):
        """Salva valores atuais no config."""
        self.config['download_path'] = self.dest_path.get()
        self.config['output_format'] = self.output_type.get()
        self.config['video_quality'] = self._get_quality_value(
            VIDEO_QUALITIES, self.video_quality_combo.current()
        )
        self.config['audio_quality'] = self._get_quality_value(
            AUDIO_QUALITIES, self.audio_quality_combo.current()
        )
        self.config['video_format'] = self._get_quality_value(
            VIDEO_FORMATS, self.video_format_combo.current()
        )
        self.config['audio_format'] = self._get_quality_value(
            AUDIO_FORMATS, self.audio_format_combo.current()
        )
        self.config['geo_bypass'] = self.geo_bypass.get()
        self.config['geo_country'] = self._get_quality_value(
            COUNTRIES, self.geo_combo.current()
        )
        self.config['embed_thumbnail'] = self.embed_thumb.get()
        self.config['download_subtitles'] = self.download_subs.get()
        self.config['subtitle_language'] = self._get_quality_value(
            SUBTITLE_LANGUAGES, self.sub_combo.current()
        )
        self.config.save()

    def _get_quality_value(self, options_list, index):
        """Obtém o valor de uma opção pelo índice."""
        if 0 <= index < len(options_list):
            return options_list[index][1]
        return options_list[0][1]

    def get_options(self):
        """Retorna as opções selecionadas como dicionário."""
        return {
            'output_format': self.output_type.get(),
            'video_quality': self._get_quality_value(
                VIDEO_QUALITIES, self.video_quality_combo.current()
            ),
            'audio_quality': self._get_quality_value(
                AUDIO_QUALITIES, self.audio_quality_combo.current()
            ),
            'video_format': self._get_quality_value(
                VIDEO_FORMATS, self.video_format_combo.current()
            ),
            'audio_format': self._get_quality_value(
                AUDIO_FORMATS, self.audio_format_combo.current()
            ),
            'output_path': self.dest_path.get(),
            'geo_bypass': self.geo_bypass.get(),
            'geo_country': self._get_quality_value(
                COUNTRIES, self.geo_combo.current()
            ),
            'embed_thumbnail': self.embed_thumb.get(),
            'download_subtitles': self.download_subs.get(),
            'subtitle_language': self._get_quality_value(
                SUBTITLE_LANGUAGES, self.sub_combo.current()
            ),
            'is_livestream': self.livestream.get(),
        }

    def set_enabled(self, enabled):
        """Habilita ou desabilita todos os controles."""
        state = 'normal' if enabled else 'disabled'
        readonly_state = 'readonly' if enabled else 'disabled'

        for widget in self.winfo_children():
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass
