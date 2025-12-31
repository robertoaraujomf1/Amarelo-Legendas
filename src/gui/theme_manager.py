import os
import logging
from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)

class ThemeManager:
    """Gerencia os estilos CSS (QSS) do Amarelo Subs"""
    
    def __init__(self):
        # Caminho base para os estilos
        self.styles_dir = os.path.join('assets', 'styles')

    def get_style(self, theme_name: str = 'dark') -> str:
        """Retorna a string CSS do tema selecionado"""
        style_file = os.path.join(self.styles_dir, f"{theme_name}.qss")
        
        # Se o arquivo .qss existir, lê e retorna
        if os.path.exists(style_file):
            try:
                with open(style_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Erro ao ler arquivo de estilo: {e}")
        
        # Estilo de fallback (caso o arquivo não exista)
        # Garante que o Amarelo Subs não quebre se faltar a pasta assets
        return """
            QMainWindow, QDialog { background-color: #2d2d2d; color: white; }
            QPushButton { background-color: #f4c430; color: black; border-radius: 5px; padding: 5px; font-weight: bold; }
            QLabel { color: #f4c430; }
            QTextEdit { background-color: #1e1e1e; color: #d0d0d0; border: 1px solid #4a4a4a; }
        """

    def apply_theme(self, app: QApplication, theme_name: str = 'dark'):
        """Aplica o tema diretamente na aplicação"""
        style = self.get_style(theme_name)
        app.setStyleSheet(style)