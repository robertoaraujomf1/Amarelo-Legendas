import os
import logging
from PyQt6.QtCore import QThread, pyqtSignal
from src.core.transcription_engine import TranscriptionEngine

logger = logging.getLogger(__name__)

class WorkflowManager(QThread):
    # Sinais definidos para enviar UM valor por vez
    progress_update = pyqtSignal(int)
    preview_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager if config_manager else {}
        self.directory = None
        # Passa a config para o motor evitar erro de NoneType
        self.engine = TranscriptionEngine(config_manager=self.config)

    def set_directory(self, directory):
        self.directory = directory

    def run(self):
        try:
            if not self.directory:
                self.finished.emit(False, "Nenhum diretório selecionado.")
                return

            videos = [f for f in os.listdir(self.directory) 
                     if f.lower().endswith(('.mp4', '.mkv', '.avi'))]
            
            if not videos:
                self.finished.emit(False, "Nenhum vídeo encontrado na pasta.")
                return

            total_videos = len(videos)
            
            for index, video in enumerate(videos):
                video_path = os.path.join(self.directory, video)
                
                # Atualiza o texto na interface
                self.preview_update.emit(f"Processando vídeo {index+1}/{total_videos}: {video}")
                self.progress_update.emit(int((index / total_videos) * 100))
                
                # Executa a transcrição (Motor Whisper)
                # verbose=False para não sujar o terminal e focar na UI
                result = self.engine.transcribe(video_path)
                
                # Aqui futuramente salvaremos o .srt
                logger.info(f"Transcrição concluída para {video}")

            self.progress_update.emit(100)
            self.finished.emit(True, "Todos os vídeos foram processados!")

        except Exception as e:
            logger.error(f"Erro crítico no workflow: {e}")
            self.finished.emit(False, str(e))