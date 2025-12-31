import os
import logging
from PyQt6.QtCore import QObject, pyqtSignal
from src.core.transcription_engine import TranscriptionEngine
from src.core.translator import Translator
from src.core.subtitle_generator import SubtitleGenerator
from src.core.subtitle_sync import SubtitleSynchronizer

class WorkflowManager(QObject):
    """
    O Cérebro do Amarelo Subs.
    Gerencia a detecção inteligente de arquivos e decide o destino de cada vídeo.
    """
    
    # Sinais para comunicação com a Interface (ProgressDialog)
    progress_update = pyqtSignal(str, int, int) # mensagem, atual, total
    preview_update = pyqtSignal(str)           # texto da legenda para o preview
    finished = pyqtSignal(bool, str)           # status, mensagem final

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Inicializa os motores
        self.transcriber = TranscriptionEngine(
            model_size=self.config.get('transcription', {}).get('model', 'base')
        )
        self.translator = Translator()
        self.generator = SubtitleGenerator()
        self.sync_manager = SubtitleSynchronizer()

    def run_directory_workflow(self, directory_path):
        """Varre o diretório e processa cada vídeo com cautela individual"""
        try:
            video_extensions = ('.mp4', '.mkv', '.avi', '.mov', '.wmv')
            files = [f for f in os.listdir(directory_path) if f.lower().endswith(video_extensions)]
            
            if not files:
                self.finished.emit(False, "Nenhum arquivo de vídeo encontrado no diretório.")
                return

            total_videos = len(files)
            for index, video_name in enumerate(files):
                video_path = os.path.join(directory_path, video_name)
                self.progress_update.emit(f"Analisando: {video_name}", index, total_videos)
                
                self._process_single_video(video_path, directory_path)
            
            self.finished.emit(True, f"Processamento de {total_videos} arquivos concluído.")
            
        except Exception as e:
            self.logger.error(f"Erro no workflow de diretório: {str(e)}")
            self.finished.emit(False, str(e))

    def _process_single_video(self, video_path, directory_path):
        """Decide o que fazer com um vídeo específico"""
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        existing_sub = None
        
        # 1. Busca por legenda existente com o mesmo nome
        for ext in ['.srt', '.ass', '.vtt']:
            pot_sub = os.path.join(directory_path, base_name + ext)
            if os.path.exists(pot_sub):
                existing_sub = pot_sub
                break

        subtitles = []

        # --- CASO A: LEGENDA JÁ EXISTE (Modo Cauteloso) ---
        if existing_sub:
            self.progress_update.emit(f"Legenda encontrada para {base_name}. Validando...", 0, 0)
            subtitles = self.sync_manager.load_subtitles(existing_sub)
            
            # Verificação de Sincronia via IA (Opcional na config)
            if self.config.get('sync', {}).get('auto_verify', True):
                # O Whisper ouve apenas os primeiros 15s para validar o tempo
                offset = self.transcriber.verify_alignment(video_path, subtitles[0])
                if abs(offset) > 0.1: # Se o desvio for maior que 100ms
                    self.progress_update.emit(f"Ajustando sincronia ({offset}s)...", 0, 0)
                    subtitles = self.sync_manager.adjust_offset(subtitles, offset)

            # Tradução se habilitada
            if self.config.get('translation', {}).get('enabled', False):
                self.progress_update.emit(f"Traduzindo legenda existente...", 0, 0)
                target = self.config.get('translation', {}).get('target_language', 'pt')
                subtitles = self.translator.translate_batch(subtitles, target)

        # --- CASO B: LEGENDA NÃO EXISTE (Geração Total) ---
        else:
            self.progress_update.emit(f"Transcrevendo áudio de {base_name}...", 0, 0)
            subtitles = self.transcriber.transcribe(video_path)
            
            # Tradução da nova transcrição se necessário
            if self.config.get('translation', {}).get('enabled', False):
                target = self.config.get('translation', {}).get('target_language', 'pt')
                subtitles = self.translator.translate_batch(subtitles, target)

        # --- FINALIZAÇÃO: FORMATAÇÃO E SALVAMENTO ---
        # Aqui aplicamos a cor, tamanho e negrito definidos no Amarelo Subs
        font_config = self.config.get('font')
        output_dir = self.config.get('general', {}).get('output_dir', 'output')
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, f"{base_name}_Amarelo.srt")
        self.generator.generate(subtitles, output_path, font_config)
        
        # Envia para o preview da UI
        self.preview_update.emit(self.generator.format_preview(subtitles))