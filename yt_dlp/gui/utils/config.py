"""Gerenciamento de configurações persistentes da GUI."""

import json
import os
from pathlib import Path


class Config:
    """Gerencia configurações persistentes da GUI do yt-dlp."""

    DEFAULT_CONFIG = {
        'download_path': str(Path.home() / 'Downloads'),
        'video_quality': '1080',
        'audio_quality': '192',
        'output_format': 'video',  # 'video' ou 'audio'
        'video_format': 'mp4',
        'audio_format': 'mp3',
        'geo_bypass': False,
        'geo_country': 'BR',
        'embed_thumbnail': False,
        'download_subtitles': False,
        'subtitle_language': 'pt',
        'window_width': 800,
        'window_height': 700,
    }

    def __init__(self):
        self.config_dir = Path.home() / '.yt-dlp-gui'
        self.config_file = self.config_dir / 'config.json'
        self.config = self.DEFAULT_CONFIG.copy()
        self._load()

    def _load(self):
        """Carrega configurações do arquivo."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.config.update(saved)
        except (json.JSONDecodeError, IOError):
            pass

    def save(self):
        """Salva configurações no arquivo."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def get(self, key, default=None):
        """Obtém uma configuração."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Define uma configuração."""
        self.config[key] = value

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value
