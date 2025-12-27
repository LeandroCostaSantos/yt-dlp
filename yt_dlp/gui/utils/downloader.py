"""Worker thread-safe para downloads com yt-dlp."""

import queue
import threading
from typing import Callable, Optional

import yt_dlp


class DownloadWorker(threading.Thread):
    """Thread worker para executar downloads sem travar a GUI."""

    def __init__(
        self,
        urls: list,
        options: dict,
        progress_callback: Callable,
        done_callback: Callable,
        error_callback: Callable,
        log_callback: Optional[Callable] = None,
    ):
        super().__init__(daemon=True)
        self.urls = urls if isinstance(urls, list) else [urls]
        self.options = options
        self.progress_callback = progress_callback
        self.done_callback = done_callback
        self.error_callback = error_callback
        self.log_callback = log_callback
        self._cancelled = threading.Event()

    def cancel(self):
        """Cancela o download em andamento."""
        self._cancelled.set()

    def is_cancelled(self):
        """Verifica se o download foi cancelado."""
        return self._cancelled.is_set()

    def _progress_hook(self, d):
        """Hook chamado durante o progresso do download."""
        if self._cancelled.is_set():
            raise yt_dlp.utils.DownloadCancelled('Download cancelado pelo usuário')

        self.progress_callback(d)

    def _create_logger(self):
        """Cria um logger customizado para capturar mensagens."""
        worker = self

        class GUILogger:
            def debug(self, msg):
                if worker.log_callback and not msg.startswith('[debug]'):
                    worker.log_callback(msg, 'debug')

            def info(self, msg):
                if worker.log_callback:
                    worker.log_callback(msg, 'info')

            def warning(self, msg):
                if worker.log_callback:
                    worker.log_callback(msg, 'warning')

            def error(self, msg):
                if worker.log_callback:
                    worker.log_callback(msg, 'error')

        return GUILogger()

    def run(self):
        """Executa o download."""
        try:
            opts = self.options.copy()
            opts['progress_hooks'] = [self._progress_hook]
            if self.log_callback:
                opts['logger'] = self._create_logger()

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download(self.urls)

            if not self._cancelled.is_set():
                self.done_callback(True, 'Download concluído com sucesso!')

        except yt_dlp.utils.DownloadCancelled:
            self.done_callback(False, 'Download cancelado.')

        except yt_dlp.utils.DownloadError as e:
            self.error_callback(str(e))

        except Exception as e:
            self.error_callback(f'Erro inesperado: {str(e)}')


class InfoExtractor(threading.Thread):
    """Thread para extrair informações de URL sem travar a GUI."""

    def __init__(
        self,
        url: str,
        callback: Callable,
        error_callback: Callable,
        extract_flat: bool = False,
    ):
        super().__init__(daemon=True)
        self.url = url
        self.callback = callback
        self.error_callback = error_callback
        self.extract_flat = extract_flat

    def run(self):
        """Extrai informações da URL."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist' if self.extract_flat else False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.callback(info)

        except yt_dlp.utils.DownloadError as e:
            self.error_callback(f'Erro ao extrair informações: {str(e)}')

        except Exception as e:
            self.error_callback(f'Erro inesperado: {str(e)}')


def extract_info_async(
    url: str,
    callback: Callable,
    error_callback: Callable,
    extract_flat: bool = False,
) -> InfoExtractor:
    """
    Extrai informações de uma URL de forma assíncrona.

    Args:
        url: URL do vídeo ou playlist
        callback: Função chamada com o info_dict quando a extração termina
        error_callback: Função chamada com a mensagem de erro
        extract_flat: Se True, não extrai informações completas de playlists

    Returns:
        Thread do extrator (já iniciada)
    """
    extractor = InfoExtractor(url, callback, error_callback, extract_flat)
    extractor.start()
    return extractor


def build_format_string(
    output_format: str,
    video_quality: str,
    audio_quality: str,
) -> str:
    """
    Constrói a string de formato para o yt-dlp.

    Args:
        output_format: 'video' ou 'audio'
        video_quality: resolução desejada (ex: '1080', '720')
        audio_quality: qualidade do áudio (ex: '192', '320')

    Returns:
        String de formato para yt-dlp
    """
    if output_format == 'audio':
        return 'bestaudio/best'

    if video_quality == 'best':
        return 'bestvideo+bestaudio/best'

    return f'bestvideo[height<={video_quality}]+bestaudio/best[height<={video_quality}]'


def build_download_options(
    output_path: str,
    output_format: str = 'video',
    video_quality: str = '1080',
    audio_quality: str = '192',
    video_format: str = 'mp4',
    audio_format: str = 'mp3',
    geo_bypass: bool = False,
    geo_country: str = 'BR',
    embed_thumbnail: bool = False,
    download_subtitles: bool = False,
    subtitle_language: str = 'pt',
    is_livestream: bool = False,
    playlist_items: Optional[str] = None,
) -> dict:
    """
    Constrói as opções de download para o yt-dlp.

    Returns:
        Dicionário de opções para YoutubeDL
    """
    format_string = build_format_string(output_format, video_quality, audio_quality)

    opts = {
        'format': format_string,
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': False,
    }

    # Geo-bypass
    if geo_bypass:
        opts['geo_bypass'] = True
        opts['geo_bypass_country'] = geo_country

    # Livestream
    if is_livestream:
        opts['live_from_start'] = True

    # Playlist
    if playlist_items:
        opts['playlist_items'] = playlist_items

    # Legendas
    if download_subtitles:
        opts['writesubtitles'] = True
        opts['subtitleslangs'] = [subtitle_language]

    # Pós-processadores
    postprocessors = []

    if output_format == 'audio':
        postprocessors.append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': audio_quality,
        })
    elif video_format and video_format != 'mp4':
        postprocessors.append({
            'key': 'FFmpegVideoRemuxer',
            'preferedformat': video_format,
        })

    if embed_thumbnail:
        postprocessors.append({'key': 'EmbedThumbnail'})
        opts['writethumbnail'] = True

    if postprocessors:
        opts['postprocessors'] = postprocessors

    return opts
