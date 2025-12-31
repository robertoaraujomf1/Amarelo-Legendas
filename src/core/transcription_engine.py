import whisper
import logging

logger = logging.getLogger(__name__)

class TranscriptionEngine:
    def __init__(self, config_manager=None):
        # Aqui estava o erro: se config_manager for None, o .get() quebra
        self.config = config_manager if config_manager else {}
        self.model_size = self.config.get("model_size", "base")
        self._model = None

    @property
    def model(self):
        if self._model is None:
            logger.info(f"Carregando modelo Whisper: {self.model_size}")
            # Carrega o modelo que já está no seu cache
            self._model = whisper.load_model(self.model_size)
        return self._model

    def transcribe(self, audio_path):
        # verbose=False impede que o Whisper "sequestre" o terminal com barras de progresso
        # que a interface não consegue ler
        return self.model.transcribe(audio_path, verbose=False)