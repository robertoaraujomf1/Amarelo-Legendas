import logging
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

from src.core.workflow_manager import WorkflowManager
from src.gui.progress_dialog import ProgressDialog

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, config_manager):
        super().__init__()
        # Armazena as configurações (essencial para não dar erro de NoneType)
        self.config = config_manager
        
        # Inicializa o WorkflowManager passando as configurações
        self.workflow = WorkflowManager(self.config)
        
        # Configurações básicas da janela principal
        self.setWindowTitle("Amarelo Subs")
        self.setMinimumSize(400, 200)

        # Configuração da Interface (UI)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botão de seleção (o "gatilho" do app)
        self.btn_selecionar = QPushButton("Selecionar Diretório de Vídeos")
        self.btn_selecionar.setMinimumWidth(250)
        self.btn_selecionar.setMinimumHeight(60)
        self.btn_selecionar.clicked.connect(self._on_select_directory)

        self.layout.addWidget(self.btn_selecionar)

    def _on_select_directory(self):
        """Abre o seletor de pastas e inicia o trabalho pesado"""
        dir_path = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Vídeos")
        
        if dir_path:
            logger.info(f"Diretório selecionado: {dir_path}")
            
            # 1. Cria e exibe a janela de progresso amarela
            self.progress_ui = ProgressDialog(self)
            self.progress_ui.show()

            # 2. Configura o diretório no Workflow
            self.workflow.set_directory(dir_path)
            
            # 3. Conecta os sinais da Thread aos métodos da Interface
            # Isso garante que o texto e a barra mudem sem travar a janela
            self.workflow.progress_update.connect(self.progress_ui.update_progress)
            self.workflow.preview_update.connect(self.progress_ui.update_preview)
            self.workflow.finished.connect(self._on_workflow_finished)
            
            # 4. Inicia o processamento em segundo plano (Thread separada)
            # IMPORTANTE: Usamos .start() para não congelar a interface
            self.workflow.start()

    def _on_workflow_finished(self, success, message):
        """Chamado quando o WorkflowManager termina o processamento"""
        # Fecha a janela de progresso
        if hasattr(self, 'progress_ui'):
            self.progress_ui.close()
            
        # Exibe o resultado final para o usuário
        if success:
            QMessageBox.information(self, "Sucesso", message)
        else:
            QMessageBox.critical(self, "Erro", f"Ocorreu um problema: {message}")

    def closeEvent(self, event):
        """Garante que o workflow pare se o usuário fechar a janela principal"""
        if self.workflow.isRunning():
            self.workflow.terminate()
            self.workflow.wait()
        event.accept()