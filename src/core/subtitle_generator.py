import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class SubtitleGenerator:
    """Gera arquivos de legenda formatados (SRT/ASS) com a marca Amarelo Subs"""

    def generate(self, subtitles: List[Dict], output_path: str, font_config: Dict):
        """Escolhe o formato correto com base na extensão do arquivo"""
        ext = os.path.splitext(output_path)[1].lower()
        
        if ext == '.ass':
            self._save_ass(subtitles, output_path, font_config)
        else:
            self._save_srt(subtitles, output_path, font_config)

    def _format_time_srt(self, seconds: float) -> str:
        """Converte segundos para o formato SRT: HH:MM:SS,mmm"""
        td_hours = int(seconds // 3600)
        td_minutes = int((seconds % 3600) // 60)
        td_seconds = int(seconds % 60)
        td_milliseconds = int((seconds % 1) * 1000)
        return f"{td_hours:02}:{td_minutes:02}:{td_seconds:02},{td_milliseconds:03}"

    def _format_time_ass(self, seconds: float) -> str:
        """Converte segundos para o formato ASS: H:MM:SS.cc"""
        td_hours = int(seconds // 3600)
        td_minutes = int((seconds % 3600) // 60)
        td_seconds = int(seconds % 60)
        td_centiseconds = int((seconds % 1) * 100)
        return f"{td_hours}:{td_minutes:02}:{td_seconds:02}.{td_centiseconds:02}"

    def _save_srt(self, subtitles: List[Dict], path: str, font: Dict):
        """Gera arquivo SRT com tags de cor básica"""
        color_hex = font.get('color', '#FFFF00').replace('#', '')
        with open(path, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(subtitles, 1):
                start = self._format_time_srt(sub['start'])
                end = self._format_time_srt(sub['end'])
                text = sub['text']
                
                # Aplica negrito se configurado
                if font.get('bold', False):
                    text = f"<b>{text}</b>"
                
                # Aplica cor amarela via tag font (suportado pela maioria dos players)
                text = f'<font color="#{color_hex}">{text}</font>'
                
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    def _save_ass(self, subtitles: List[Dict], path: str, font: Dict):
        """Gera arquivo ASS com estilos avançados de tipografia"""
        color_ass = self._hex_to_ass_color(font.get('color', '#FFFF00'))
        font_name = font.get('name', 'Arial')
        font_size = font.get('size', 20)
        bold = "-1" if font.get('bold', False) else "0"

        header = [
            "[Script Info]", "Title: Amarelo Subs Generated", "ScriptType: v4.00+", "Collisions: Normal", "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            f"Style: Default,{font_name},{font_size},{color_ass},&H000000FF,&H00000000,&H00000000,{bold},0,0,0,100,100,0,0,1,2,2,2,10,10,10,1", "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]

        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(header) + "\n")
            for sub in subtitles:
                start = self._format_time_ass(sub['start'])
                end = self._format_time_ass(sub['end'])
                # No ASS, \N é quebra de linha
                text = sub['text'].replace('\n', '\\N')
                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")

    def _hex_to_ass_color(self, hex_color: str) -> str:
        """Converte #RRGGBB para o formato ABGR do ASS (&HAA_BB_GG_RR)"""
        hex_color = hex_color.replace('#', '')
        r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        return f"&H00{b}{g}{r}" # Alfa 00 (opaco) + BGR

    def format_preview(self, subtitles: List[Dict]) -> str:
        """Cria uma string simples para o Log/Preview da interface"""
        preview = []
        for sub in subtitles[:20]: # Mostra as primeiras 20 linhas
            preview.append(f"[{self._format_time_srt(sub['start'])}] {sub['text']}")
        if len(subtitles) > 20:
            preview.append("...")
        return "\n".join(preview)