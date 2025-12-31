import os
import whisper
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TranscriptionEngine:
    """
    Motor de IA do Amarelo Subs baseado no Whisper.
    Responsável por transcrever do zero e validar sincronia de legendas existentes.
    """

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None  # Carregamento preguiçoso (lazy loading) para economizar RAM

    @property
    def model(self):
        if self._model is None:
            logger.info(f"Carregando modelo Whisper: {self.model_size}")
            self._model = whisper.load_model(self.model_size)
        return self._model

    def transcribe(self, video_path: str) -> List[Dict]:
        """Transcreve o vídeo completo (Cenário de geração total)"""
        logger.info(f"Iniciando transcrição completa: {video_path}")
        
        result = self.model.transcribe(video_path, verbose=False)
        
        subtitles = []
        for i, segment in enumerate(result['segments']):
            subtitles.append({
                'index': i + 1,
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip(),
                'original_text': segment['text'].strip()
            })
        return subtitles

    def verify_alignment(self, video_path: str, first_subtitle: Dict) -> float:
        """
        MODO CAUTELOSO: Ouve apenas os primeiros segundos do vídeo para
        verificar se a legenda existente bate com o áudio real.
        
        Retorna o 'offset' (diferença) em segundos.
        """
        try:
            logger.info(f"Verificando alinhamento para: {video_path}")
            
            # 1. Definimos uma janela de busca (ex: primeiros 20 segundos)
            # O parâmetro 'duration' limita o áudio processado para ser ultra rápido
            sample_result = self.model.transcribe(
                video_path, 
                duration=20, 
                task="transcribe"
            )
            
            if not sample_result['segments']:
                return 0.0

            # 2. Pegamos o tempo real onde a IA detectou a primeira fala significativa
            real_start = sample_result['segments'][0]['start']
            
            # 3. Pegamos o tempo onde a legenda existente diz que a fala começa
            expected_start = first_subtitle['start']
            
            # 4. Calculamos a diferença
            # Se real_start é 3.5 e expected_start é 1.5, o offset é +2.0s
            offset = real_start - expected_start
            
            # Só aplicamos se a diferença for relevante (ex: mais de 150ms)
            if abs(offset) < 0.15:
                return 0.0
                
            return round(offset, 3)

        except Exception as e:
            logger.error(f"Falha na verificação de alinhamento: {e}")
            return 0.0

    def get_video_info(self, video_path: str) -> Dict:
        """Retorna metadados básicos do vídeo via Whisper/FFmpeg"""
        # Implementação básica de suporte
        return {
            "path": video_path,
            "duration": 0, # Poderia ser extraído via ffprobe
            "scenes": []   # Reservado para detecção de mudança de cena futura
        }