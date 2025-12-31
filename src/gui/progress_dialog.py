import time
from datetime import datetime, timedelta
# Alterado de PySide6 para PyQt6
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, 
    QTextEdit, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processando - Amarelo Subs")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        # Estilo visual condizente com o tema Dark do Amarelo Subs
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
            }
        """)
        
        # Variáveis de controle
        self.start_time = None
        self.processed_count = 0
        self.total_count = 0
        self.errors = []

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Status Label
        self.label_status = QLabel("Preparando...")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_status.setStyleSheet("""
            QLabel {
                background-color: #3a3a3a;
                border: 1px solid #5a5a5a;
                border-radius: 8px;
                padding: 12px;
                color: #f4c430;
                font-size: 11pt;
                font-weight: bold;
            }
        """)

        # Barra de Progresso
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #5a5a5a;
                border-radius: 8px;
                text-align: center;
                background-color: #1a1a1a;
                color: white;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #f4c430;
                border-radius: 7px;
            }
        """)

        self.label_time = QLabel("")
        self.label_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_time.setStyleSheet("color: #b0b0b0;")

        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d0d0d0;
                border-radius: 5px;
                font-family: 'Consolas';
            }
        """)
        self.log_text.setMaximumHeight(150)

        # Preview
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #ffffff;
                border: 1px solid #f4c430;
                border-radius: 5px;
            }
        """)

        layout.addWidget(self.label_status)
        layout.addWidget(self.progress)
        layout.addWidget(self.label_time)
        layout.addWidget(QLabel("Log detalhado:"))
        layout.addWidget(self.log_text)
        layout.addWidget(QLabel("Pré-visualização:"))
        layout.addWidget(self.preview_text)

    def _add_log(self, message: str, is_error: bool = False):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "❌" if is_error else "ℹ️"
        self.log_text.append(f"[{timestamp}] {prefix} {message}")
        # Scroll automático
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def update_progress(self, message: str, current: int, total: int):
        """Método principal para atualizar a interface via Sinais"""
        self.label_status.setText(message)
        self._add_log(message)

        if self.start_time is None and total > 0:
            self.start_time = time.time()

        if total > 0:
            percent = int((current / total) * 100)
            self.progress.setValue(percent)
            self.progress.setFormat(f"{percent}% ({current}/{total})")
            
            # Cálculo de ETA (Tempo Estimado)
            if current > 0:
                elapsed = time.time() - self.start_time
                avg = elapsed / current
                remaining = avg * (total - current)
                eta = timedelta(seconds=int(remaining))
                self.label_time.setText(f"Tempo restante estimado: {str(eta)}")

        if current >= total and total > 0:
            self._add_log("✅ Processamento concluído!")

    def update_preview(self, content: str):
        """Atualiza a caixa de texto com a legenda gerada"""
        self.preview_text.setPlainText(content)

    def showEvent(self, event):
        """Limpa o diálogo sempre que ele for aberto"""
        super().showEvent(event)
        self.progress.setValue(0)
        self.log_text.clear()
        self.preview_text.clear()
        self.start_time = None