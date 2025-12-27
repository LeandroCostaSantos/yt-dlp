"""Estilos e tema visual para a GUI do yt-dlp."""

# Cores do tema - Paleta 2025 Color Trends
# Quietude (Sherwin Williams), Rumors (Behr), Encore (Valspar), Cinnamon Slate (Benjamin Moore)
COLORS = {
    'bg': '#1a1a1a',           # Fundo principal (escuro)
    'bg_light': '#2a2a2a',     # Fundo de elementos
    'bg_input': '#3a3a3a',     # Fundo de inputs
    'fg': '#f5f5f5',           # Texto principal
    'fg_secondary': '#a8b5a0', # Texto secundário (Quietude claro)
    'accent': '#0d5c75',       # Cor de destaque (Encore - azul profundo)
    'accent_hover': '#094a5e', # Hover do destaque
    'success': '#a8b5a0',      # Quietude (verde suave)
    'warning': '#9a8478',      # Cinnamon Slate (marrom rosado)
    'error': '#7a3b4a',        # Rumors (bordô/marsala)
    'border': '#5a5a5a',       # Bordas
    'quietude': '#a8b5a0',     # Verde suave
    'rumors': '#7a3b4a',       # Bordô/Marsala
    'encore': '#0d5c75',       # Azul profundo
    'cinnamon': '#9a8478',     # Marrom rosado
}

# Fontes
FONTS = {
    'title': ('Segoe UI', 16, 'bold'),
    'heading': ('Segoe UI', 12, 'bold'),
    'normal': ('Segoe UI', 10),
    'small': ('Segoe UI', 9),
    'mono': ('Consolas', 9),
}

# Dimensões
DIMENSIONS = {
    'padding': 10,
    'padding_small': 5,
    'border_radius': 5,
    'button_width': 12,
    'entry_width': 50,
}

# Países para geo-bypass
COUNTRIES = [
    ('Brasil', 'BR'),
    ('Estados Unidos', 'US'),
    ('Reino Unido', 'GB'),
    ('Alemanha', 'DE'),
    ('França', 'FR'),
    ('Japão', 'JP'),
    ('Canadá', 'CA'),
    ('Austrália', 'AU'),
    ('Espanha', 'ES'),
    ('Itália', 'IT'),
    ('México', 'MX'),
    ('Argentina', 'AR'),
    ('Portugal', 'PT'),
    ('Índia', 'IN'),
    ('Coreia do Sul', 'KR'),
]

# Qualidades de vídeo disponíveis
VIDEO_QUALITIES = [
    ('Melhor disponível', 'best'),
    ('4K (2160p)', '2160'),
    ('Full HD (1080p)', '1080'),
    ('HD (720p)', '720'),
    ('SD (480p)', '480'),
    ('Baixa (360p)', '360'),
    ('Mínima (240p)', '240'),
]

# Qualidades de áudio disponíveis
AUDIO_QUALITIES = [
    ('320 kbps (Máxima)', '320'),
    ('256 kbps (Alta)', '256'),
    ('192 kbps (Média)', '192'),
    ('128 kbps (Normal)', '128'),
    ('96 kbps (Baixa)', '96'),
]

# Formatos de vídeo
VIDEO_FORMATS = [
    ('MP4', 'mp4'),
    ('MKV', 'mkv'),
    ('WebM', 'webm'),
    ('AVI', 'avi'),
]

# Formatos de áudio
AUDIO_FORMATS = [
    ('MP3', 'mp3'),
    ('M4A', 'm4a'),
    ('FLAC', 'flac'),
    ('WAV', 'wav'),
    ('OGG', 'ogg'),
]

# Idiomas de legenda
SUBTITLE_LANGUAGES = [
    ('Português', 'pt'),
    ('Inglês', 'en'),
    ('Espanhol', 'es'),
    ('Francês', 'fr'),
    ('Alemão', 'de'),
    ('Italiano', 'it'),
    ('Japonês', 'ja'),
    ('Coreano', 'ko'),
    ('Chinês', 'zh'),
    ('Russo', 'ru'),
]


def apply_dark_theme(root):
    """Aplica o tema escuro à aplicação."""
    style_config = {
        '.': {
            'configure': {
                'background': COLORS['bg'],
                'foreground': COLORS['fg'],
                'font': FONTS['normal'],
            }
        },
        'TFrame': {
            'configure': {
                'background': COLORS['bg'],
            }
        },
        'TLabel': {
            'configure': {
                'background': COLORS['bg'],
                'foreground': COLORS['fg'],
            }
        },
        'TButton': {
            'configure': {
                'background': COLORS['accent'],
                'foreground': COLORS['fg'],
                'padding': (10, 5),
            }
        },
        'TEntry': {
            'configure': {
                'fieldbackground': COLORS['bg_input'],
                'foreground': COLORS['fg'],
                'insertcolor': COLORS['fg'],
            }
        },
        'TCheckbutton': {
            'configure': {
                'background': COLORS['bg'],
                'foreground': COLORS['fg'],
            }
        },
        'TRadiobutton': {
            'configure': {
                'background': COLORS['bg'],
                'foreground': COLORS['fg'],
            }
        },
        'TCombobox': {
            'configure': {
                'fieldbackground': COLORS['bg_input'],
                'background': COLORS['bg_input'],
                'foreground': COLORS['fg'],
            }
        },
        'TLabelframe': {
            'configure': {
                'background': COLORS['bg'],
                'foreground': COLORS['fg'],
            }
        },
        'TLabelframe.Label': {
            'configure': {
                'background': COLORS['bg'],
                'foreground': COLORS['accent'],
                'font': FONTS['heading'],
            }
        },
        'Horizontal.TProgressbar': {
            'configure': {
                'background': COLORS['accent'],
                'troughcolor': COLORS['bg_light'],
            }
        },
    }

    try:
        from tkinter import ttk
        style = ttk.Style(root)

        # Tentar usar tema que suporta cores
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')

        for widget, config in style_config.items():
            if 'configure' in config:
                try:
                    style.configure(widget, **config['configure'])
                except Exception:
                    pass

        # Configurar cores do root
        root.configure(bg=COLORS['bg'])

    except Exception:
        pass


def format_duration(seconds):
    """Formata duração em segundos para HH:MM:SS."""
    if not seconds:
        return '--:--'

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f'{hours:02d}:{minutes:02d}:{secs:02d}'
    return f'{minutes:02d}:{secs:02d}'


def format_size(bytes_size):
    """Formata tamanho em bytes para formato legível."""
    if not bytes_size:
        return 'N/A'

    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f'{bytes_size:.1f} {unit}'
        bytes_size /= 1024

    return f'{bytes_size:.1f} TB'
