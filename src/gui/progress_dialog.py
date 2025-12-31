import logging
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Amarelo Subs - Processando")
        self.setFixedSize(400, 150)
        # Remove o botão de fechar para o usuário não interromper o processo acidentalmente
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        self.layout = QVBoxLayout(self)

        # Rótulo que mostra o nome do vídeo atual
        self.label_status = QLabel("Iniciando...")
        self.label_status.setWordWrap(True)
        self.layout.addWidget(self.label_status)

        # Barra de progresso (0 a 100)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #f4c430; /* Amarelo Subs */
                width: 10px;
            }
        """)
        self.layout.addWidget(self.progress_bar)

    def update_progress(self, value):
        """Recebe um inteiro de 0 a 100 e atualiza a barra"""
        self.progress_bar.setValue(value)

    def update_preview(self, text):
        """Atualiza o texto exibido acima da barra"""
        self.label_status.setText(text)
        logger.info(f"Status da UI: {text}")