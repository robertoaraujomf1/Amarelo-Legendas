from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt6.QtCore import QThread
from src.core.workflow_manager import WorkflowManager
from src.gui.progress_dialog import ProgressDialog

class MainWindow(QMainWindow):
    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        
        # Define o título usando o nome oficial
        self.setWindowTitle(self.config.get('app_name', 'Amarelo Subs'))
        
        # ... (seu código de UI: botões, inputs, etc.)
        
        # Conexão do botão de processar
        # self.btn_run.clicked.connect(self.handle_processing)

    def handle_processing(self):
        video = self.input_video.text() # caminho do vídeo selecionado
        subtitle = self.input_subtitle.text() # pode ser vazio
        
        if not video:
            QMessageBox.warning(self, "Erro", "Selecione um vídeo primeiro!")
            return

        # 1. Criar o Diálogo de Progresso
        self.progress_dialog = ProgressDialog(self)
        
        # 2. Criar a Thread e o Worker (WorkflowManager)
        self.thread = QThread()
        self.worker = WorkflowManager(self.config)
        self.worker.moveToThread(self.thread)

        # 3. Conectar os Sinais (A mágica acontece aqui)
        self.thread.started.connect(lambda: self.worker.run_workflow(video, subtitle))
        
        # Atualiza a UI do diálogo com dados do Worker
        self.worker.progress_update.connect(self.progress_dialog.update_progress)
        self.worker.preview_update.connect(self.progress_dialog.update_preview)
        
        # Finalização
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # 4. Iniciar
        self.thread.start()
        self.progress_dialog.exec() # Abre como modal

    def on_processing_finished(self, success, message):
        if success:
            QMessageBox.information(self, "Sucesso", f"Processamento concluído!\nSalvo em: {message}")
        else:
            QMessageBox.critical(self, "Erro crítico", f"Falha no processamento:\n{message}")