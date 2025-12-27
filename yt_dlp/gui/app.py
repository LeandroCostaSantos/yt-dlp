"""Aplicação principal da GUI do yt-dlp."""

import io
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import urllib.request

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from .styles import COLORS, FONTS, apply_dark_theme, format_duration
from .widgets import URLInput, FormatSelector, ProgressFrame, PlaylistView
from .utils import Config, DownloadWorker, extract_info_async
from .utils.downloader import build_download_options


class YTDLPApp(tk.Tk):
    """Aplicação principal da GUI do yt-dlp."""

    def __init__(self):
        super().__init__()

        self.title('YT-DLP GUI')
        self.geometry('1000x850')
        self.minsize(900, 750)

        # Configurações
        self.config = Config()

        # Estado
        self.current_info = None
        self.download_worker = None
        self.thumbnail_image = None  # Manter referência para evitar garbage collection

        # Aplicar tema
        apply_dark_theme(self)
        self.configure(bg=COLORS['bg'])

        # Criar widgets
        self._create_widgets()

        # Restaurar tamanho da janela
        width = self.config.get('window_width', 1000)
        height = self.config.get('window_height', 850)
        self.geometry(f'{width}x{height}')

        # Bind para salvar tamanho ao fechar
        self.protocol('WM_DELETE_WINDOW', self._on_close)

    def _create_widgets(self):
        """Cria todos os widgets da aplicação."""
        # Frame principal com padding
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)

        # Header com título e créditos
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 10))

        # Título
        title_label = ttk.Label(
            header_frame,
            text='YT-DLP GUI',
            font=FONTS['title'],
        )
        title_label.pack(side='left')

        # Créditos - CostaDEV
        credit_label = ttk.Label(
            header_frame,
            text='UI by CostaDEV',
            font=FONTS['small'],
            foreground=COLORS['encore'],
        )
        credit_label.pack(side='right', padx=(0, 5))

        # URL Input
        self.url_input = URLInput(
            main_frame,
            on_analyze_callback=self._on_analyze,
        )
        self.url_input.pack(fill='x', pady=(0, 10))

        # Frame de informações do vídeo
        self.info_frame = ttk.LabelFrame(main_frame, text='Informações')
        self.info_frame.pack(fill='x', pady=(0, 10))

        info_inner = ttk.Frame(self.info_frame)
        info_inner.pack(fill='x', padx=10, pady=10)

        # Thumbnail (lado esquerdo)
        self.thumb_frame = ttk.Frame(info_inner)
        self.thumb_frame.pack(side='left', padx=(0, 15))

        self.thumb_label = ttk.Label(
            self.thumb_frame,
            text='[Thumbnail]',
            width=20,
        )
        self.thumb_label.pack()

        # Informações (lado direito)
        info_text_frame = ttk.Frame(info_inner)
        info_text_frame.pack(side='left', fill='both', expand=True)

        # Título do vídeo
        self.title_var = tk.StringVar(value='--')
        ttk.Label(
            info_text_frame,
            text='Título:',
            font=FONTS['heading'],
        ).pack(anchor='w')
        self.title_label = ttk.Label(
            info_text_frame,
            textvariable=self.title_var,
            font=FONTS['normal'],
            wraplength=450,
        )
        self.title_label.pack(anchor='w', pady=(0, 5))

        # Duração e canal
        details_frame = ttk.Frame(info_text_frame)
        details_frame.pack(anchor='w', fill='x')

        ttk.Label(details_frame, text='Duração:', font=FONTS['small']).pack(side='left')
        self.duration_var = tk.StringVar(value='--')
        ttk.Label(
            details_frame,
            textvariable=self.duration_var,
            font=FONTS['small'],
        ).pack(side='left', padx=(5, 20))

        ttk.Label(details_frame, text='Canal:', font=FONTS['small']).pack(side='left')
        self.channel_var = tk.StringVar(value='--')
        ttk.Label(
            details_frame,
            textvariable=self.channel_var,
            font=FONTS['small'],
        ).pack(side='left', padx=(5, 0))

        # Seletor de formato
        self.format_selector = FormatSelector(main_frame, self.config)
        self.format_selector.pack(fill='x', pady=(0, 10))

        # Visualização de playlist (inicialmente oculto)
        self.playlist_view = PlaylistView(main_frame)

        # Barra de progresso
        self.progress_frame = ProgressFrame(main_frame)
        self.progress_frame.pack(fill='x', pady=(0, 10))

        # Botões de ação
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.download_btn = ttk.Button(
            button_frame,
            text='Baixar',
            command=self._on_download,
            width=15,
        )
        self.download_btn.pack(side='left', padx=5)
        self.download_btn.configure(state='disabled')

        self.cancel_btn = ttk.Button(
            button_frame,
            text='Cancelar',
            command=self._on_cancel,
            width=15,
        )
        self.cancel_btn.pack(side='left', padx=5)
        self.cancel_btn.configure(state='disabled')

        # Log
        log_frame = ttk.LabelFrame(main_frame, text='Log')
        log_frame.pack(fill='both', expand=True)

        self.log_text = tk.Text(
            log_frame,
            height=5,
            font=FONTS['mono'],
            bg=COLORS['bg_input'],
            fg=COLORS['fg'],
            wrap='word',
        )
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)

        log_scroll = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        log_scroll.pack(side='right', fill='y')
        self.log_text.configure(yscrollcommand=log_scroll.set)

    def _log(self, message, level='info'):
        """Adiciona mensagem ao log."""
        self.log_text.configure(state='normal')

        # Cor baseada no nível
        tag = level
        if level == 'error':
            self.log_text.insert('end', f'[ERRO] {message}\n', tag)
        elif level == 'warning':
            self.log_text.insert('end', f'[AVISO] {message}\n', tag)
        else:
            self.log_text.insert('end', f'{message}\n')

        self.log_text.see('end')
        self.log_text.configure(state='disabled')

    def _on_analyze(self, url):
        """Chamado quando o usuário clica em Analisar."""
        self._log(f'Analisando: {url}')
        self.url_input.set_analyzing(True)
        self.download_btn.configure(state='disabled')
        self.progress_frame.set_status('Analisando URL...')
        self.progress_frame.set_indeterminate(True)

        # Limpar informações anteriores
        self._clear_info()

        # Extrair informações em thread separada
        extract_info_async(
            url,
            callback=lambda info: self.after(0, self._on_info_extracted, info),
            error_callback=lambda err: self.after(0, self._on_extract_error, err),
            extract_flat=True,  # Para playlists
        )

    def _on_info_extracted(self, info):
        """Chamado quando a extração de informações termina."""
        self.url_input.set_analyzing(False)
        self.progress_frame.set_indeterminate(False)
        self.progress_frame.set_status('Análise concluída')

        self.current_info = info

        if not info:
            self._log('Nenhuma informação extraída', 'error')
            return

        # Verificar se é playlist
        entries = info.get('entries')
        if entries:
            # É uma playlist
            entries_list = list(entries)  # Converter generator
            self._log(f'Playlist detectada: {len(entries_list)} itens')
            self.title_var.set(info.get('title', 'Playlist sem título'))
            self.duration_var.set(f'{len(entries_list)} vídeos')
            self.channel_var.set(info.get('uploader', info.get('channel', '--')))

            # Mostrar playlist view
            self.playlist_view.set_items(entries_list)
            self.playlist_view.pack(fill='both', expand=True, pady=(0, 10),
                                    before=self.progress_frame)
        else:
            # Vídeo único
            self._log(f'Vídeo encontrado: {info.get("title", "Sem título")}')
            self.title_var.set(info.get('title', 'Sem título'))
            self.duration_var.set(format_duration(info.get('duration')))
            self.channel_var.set(info.get('uploader', info.get('channel', '--')))

            # Ocultar playlist view
            self.playlist_view.pack_forget()
            self.playlist_view.clear()

            # Carregar thumbnail
            self._load_thumbnail(info)

        self.download_btn.configure(state='normal')

    def _on_extract_error(self, error):
        """Chamado quando há erro na extração."""
        self.url_input.set_analyzing(False)
        self.progress_frame.set_indeterminate(False)
        self.progress_frame.set_status('Erro na análise')
        self._log(error, 'error')
        messagebox.showerror('Erro', error)

    def _load_thumbnail(self, info):
        """Carrega e exibe a thumbnail do vídeo."""
        if not HAS_PIL:
            return

        thumbnails = info.get('thumbnails', [])
        if not thumbnails:
            thumb_url = info.get('thumbnail')
            if thumb_url:
                thumbnails = [{'url': thumb_url}]

        if not thumbnails:
            return

        # Pegar a melhor thumbnail
        thumb_url = thumbnails[-1].get('url')
        if not thumb_url:
            return

        def load():
            try:
                with urllib.request.urlopen(thumb_url, timeout=10) as response:
                    image_data = response.read()

                image = Image.open(io.BytesIO(image_data))
                image.thumbnail((160, 90), Image.Resampling.LANCZOS)

                self.after(0, lambda: self._set_thumbnail(image))

            except Exception as e:
                self._log(f'Erro ao carregar thumbnail: {e}', 'warning')

        threading.Thread(target=load, daemon=True).start()

    def _set_thumbnail(self, image):
        """Define a imagem da thumbnail (thread-safe)."""
        try:
            self.thumbnail_image = ImageTk.PhotoImage(image)
            self.thumb_label.configure(image=self.thumbnail_image, text='')
        except Exception:
            pass

    def _clear_info(self):
        """Limpa informações do vídeo atual."""
        self.current_info = None
        self.title_var.set('--')
        self.duration_var.set('--')
        self.channel_var.set('--')
        self.thumb_label.configure(image='', text='[Thumbnail]')
        self.thumbnail_image = None
        self.playlist_view.pack_forget()
        self.playlist_view.clear()

    def _on_download(self):
        """Inicia o download."""
        if not self.current_info:
            messagebox.showwarning('Aviso', 'Analise uma URL primeiro.')
            return

        # Verificar se há itens selecionados (playlist)
        if self.playlist_view.has_items():
            if self.playlist_view.get_selected_count() == 0:
                messagebox.showwarning('Aviso', 'Selecione pelo menos um item da playlist.')
                return

        # Obter opções
        options = self.format_selector.get_options()

        if not options['output_path']:
            messagebox.showwarning('Aviso', 'Selecione uma pasta de destino.')
            return

        # Salvar configurações
        self.format_selector.save_to_config()

        # Construir opções de download
        playlist_items = None
        if self.playlist_view.has_items():
            playlist_items = self.playlist_view.get_playlist_items_string()

        ydl_opts = build_download_options(
            output_path=options['output_path'],
            output_format=options['output_format'],
            video_quality=options['video_quality'],
            audio_quality=options['audio_quality'],
            video_format=options['video_format'],
            audio_format=options['audio_format'],
            geo_bypass=options['geo_bypass'],
            geo_country=options['geo_country'],
            embed_thumbnail=options['embed_thumbnail'],
            download_subtitles=options['download_subtitles'],
            subtitle_language=options['subtitle_language'],
            is_livestream=options['is_livestream'],
            playlist_items=playlist_items,
        )

        # URL para download
        url = self.url_input.get_url()

        # Iniciar download
        self._log(f'Iniciando download: {url}')
        self._set_downloading(True)
        self.progress_frame.reset()
        self.progress_frame.set_status('Iniciando download...')

        self.download_worker = DownloadWorker(
            urls=[url],
            options=ydl_opts,
            progress_callback=lambda d: self.after(0, self._on_progress, d),
            done_callback=lambda s, m: self.after(0, self._on_download_done, s, m),
            error_callback=lambda e: self.after(0, self._on_download_error, e),
            log_callback=lambda m, l: self.after(0, self._log, m, l),
        )
        self.download_worker.start()

    def _on_progress(self, data):
        """Atualiza progresso do download."""
        self.progress_frame.update_progress(data)

    def _on_download_done(self, success, message):
        """Chamado quando o download termina."""
        self._set_downloading(False)
        self.progress_frame.set_complete(success, message)
        self._log(message, 'info' if success else 'error')

        if success:
            messagebox.showinfo('Concluído', message)
        else:
            messagebox.showwarning('Aviso', message)

    def _on_download_error(self, error):
        """Chamado quando há erro no download."""
        self._set_downloading(False)
        self.progress_frame.set_complete(False, 'Erro no download')
        self._log(error, 'error')
        messagebox.showerror('Erro', error)

    def _on_cancel(self):
        """Cancela o download em andamento."""
        if self.download_worker and self.download_worker.is_alive():
            self._log('Cancelando download...')
            self.download_worker.cancel()
            self.progress_frame.set_status('Cancelando...')

    def _set_downloading(self, downloading):
        """Define estado de download (habilita/desabilita controles)."""
        state = 'disabled' if downloading else 'normal'
        cancel_state = 'normal' if downloading else 'disabled'

        self.download_btn.configure(state=state)
        self.cancel_btn.configure(state=cancel_state)
        self.url_input.set_analyzing(downloading)
        self.format_selector.set_enabled(not downloading)

    def _on_close(self):
        """Chamado ao fechar a janela."""
        # Cancelar download em andamento
        if self.download_worker and self.download_worker.is_alive():
            self.download_worker.cancel()

        # Salvar tamanho da janela
        self.config['window_width'] = self.winfo_width()
        self.config['window_height'] = self.winfo_height()
        self.config.save()

        self.destroy()


def main():
    """Função principal para iniciar a GUI."""
    app = YTDLPApp()
    app.mainloop()


if __name__ == '__main__':
    main()
