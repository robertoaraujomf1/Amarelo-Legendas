import os
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SubtitleSynchronizer:
    """Sincroniza legendas com o vídeo e gerencia diferentes formatos"""
    
    def __init__(self):
        # Pattern para capturar HH:MM:SS,ms ou .ms
        self.time_pattern = re.compile(r'(\d{2}):(\d{2}):(\d{2})[,.](\d{3})')

    def adjust_offset(self, subtitles: List[Dict], offset_seconds: float) -> List[Dict]:
        """
        Ajusta o tempo de todas as legendas (adianta ou atrasa).
        offset_seconds: segundos para somar (ex: 2.0 para adiantar 2s)
        """
        for sub in subtitles:
            sub['start'] = max(0, sub['start'] + offset_seconds)
            sub['end'] = max(0, sub['end'] + offset_seconds)
        return subtitles

    def sync_by_scenes(self, subtitles: List[Dict], scene_changes: List[float]) -> List[Dict]:
        """
        Ajusta a primeira legenda para coincidir com a primeira troca de cena/áudio detectada.
        """
        if not subtitles or not scene_changes:
            return subtitles
            
        first_scene = scene_changes[0]
        first_subtitle_start = subtitles[0]['start']
        
        # Calcula a diferença (o 'drift')
        offset = first_scene - first_subtitle_start
        
        logger.info(f"Aplicando ajuste de sincronia: {offset:.3f}s baseado na primeira cena.")
        return self.adjust_offset(subtitles, offset)

    def _parse_time(self, time_str: str) -> float:
        """Converte string de tempo (SRT/VTT) para segundos decimais"""
        match = self.time_pattern.match(time_str.replace(',', '.'))
        if match:
            h, m, s, ms = map(int, match.groups())
            return h * 3600 + m * 60 + s + ms / 1000.0
        return 0.0

    def _parse_ass_time(self, time_str: str) -> float:
        """Converte tempo formato ASS (H:MM:SS.cs) para segundos"""
        try:
            parts = time_str.split(':')
            h = int(parts[0])
            m = int(parts[1])
            s_parts = parts[2].split('.')
            s = int(s_parts[0])
            cs = int(s_parts[1]) # centisegundos (1/100)
            return h * 3600 + m * 60 + s + cs / 100.0
        except:
            return 0.0

    # ... (Seus métodos _load_srt, _load_ass e _load_vtt aqui dentro)