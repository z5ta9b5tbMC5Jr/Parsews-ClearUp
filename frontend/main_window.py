"""
Janela principal da aplicação Parsews
Interface gráfica usando PySide6
"""

import os
from typing import List
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QGroupBox, QCheckBox, QComboBox, QFileDialog,
    QSplitter, QTextEdit
)
from PySide6.QtGui import QFont, QColor, QPalette

from backend.file_scanner import FileScanner, FileInfo
from backend.safety_checker import SafetyChecker


class ScanThread(QThread):
    """Thread para executar a varredura em background"""
    progress = Signal(str)
    finished = Signal(list)
    error = Signal(str)
    
    def __init__(self, scanner: FileScanner, drives: List[str]):
        super().__init__()
        self.scanner = scanner
        self.drives = drives
    
    def run(self):
        """Executa a varredura"""
        try:
            files = self.scanner.scan_drives(self.drives)
            self.finished.emit(files)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Janela principal da aplicação"""
    
    def __init__(self):
        super().__init__()
        self.scanner = FileScanner()
        self.safety_checker = SafetyChecker()
        self.scanned_files: List[FileInfo] = []
        self.scan_thread = None
        
        self._setup_ui()
        self._apply_styles()
        self._connect_signals()
    
    def _setup_ui(self):
        """Configura a interface do usuário"""
        self.setWindowTitle("Parsews - Limpador de Arquivos")
        self.setMinimumSize(1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("Parsews - Limpador de Arquivos")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Grupo de controles
        controls_group = QGroupBox("Controles")
        controls_layout = QHBoxLayout()
        
        # Seleção de drives
        drives_label = QLabel("Unidades:")
        self.drives_combo = QComboBox()
        self._populate_drives()
        
        # Botões
        self.scan_button = QPushButton("🔍 Escanear")
        self.scan_button.setMinimumHeight(40)
        self.clean_button = QPushButton("🧹 Limpar Selecionados")
        self.clean_button.setMinimumHeight(40)
        self.clean_button.setEnabled(False)
        self.clean_all_button = QPushButton("🗑️ Limpar Tudo")
        self.clean_all_button.setMinimumHeight(40)
        self.clean_all_button.setEnabled(False)
        
        controls_layout.addWidget(drives_label)
        controls_layout.addWidget(self.drives_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(self.scan_button)
        controls_layout.addWidget(self.clean_button)
        controls_layout.addWidget(self.clean_all_button)
        controls_group.setLayout(controls_layout)
        main_layout.addWidget(controls_group)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminado
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Label de status
        self.status_label = QLabel("Pronto para escanear")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Estatísticas
        stats_group = QGroupBox("Estatísticas")
        stats_layout = QHBoxLayout()
        
        self.files_count_label = QLabel("Arquivos: 0")
        self.size_label = QLabel("Tamanho: 0 MB")
        self.category_label = QLabel("Categorias: 0")
        
        stats_layout.addWidget(self.files_count_label)
        stats_layout.addWidget(self.size_label)
        stats_layout.addWidget(self.category_label)
        stats_layout.addStretch()
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # Tabela de arquivos
        files_group = QGroupBox("Arquivos Encontrados")
        files_layout = QVBoxLayout()
        
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(5)
        self.files_table.setHorizontalHeaderLabels([
            "Selecionar", "Caminho", "Categoria", "Tamanho", "Última Modificação"
        ])
        self.files_table.horizontalHeader().setStretchLastSection(True)
        self.files_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.files_table.setAlternatingRowColors(True)
        
        # Checkbox na primeira coluna
        header = self.files_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.files_table.setColumnWidth(0, 80)
        
        files_layout.addWidget(self.files_table)
        files_group.setLayout(files_layout)
        main_layout.addWidget(files_group, stretch=1)
    
    def _populate_drives(self):
        """Preenche o combo box com drives disponíveis"""
        import string
        self.drives_combo.clear()
        self.drives_combo.addItem("Todas as unidades", None)
        
        for letter in string.ascii_uppercase:
            drive = f"{letter}:"
            if os.path.exists(drive + "\\"):
                self.drives_combo.addItem(f"{drive} ({drive}\\)", [drive])
    
    def _apply_styles(self):
        """Aplica estilos modernos à interface"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QComboBox:hover {
                border: 1px solid #2196F3;
            }
            QLabel {
                color: #333333;
            }
        """)
    
    def _connect_signals(self):
        """Conecta sinais e slots"""
        self.scan_button.clicked.connect(self._start_scan)
        self.clean_button.clicked.connect(self._clean_selected)
        self.clean_all_button.clicked.connect(self._clean_all)
        
        # Callback de progresso
        def progress_callback(path):
            self.status_label.setText(f"Escaneando: {path[:60]}...")
        
        self.scanner.set_progress_callback(progress_callback)
    
    def _start_scan(self):
        """Inicia a varredura de arquivos"""
        if self.scan_thread and self.scan_thread.isRunning():
            QMessageBox.warning(self, "Aviso", "Uma varredura já está em andamento!")
            return
        
        # Obtém drives selecionados
        drives = self.drives_combo.currentData()
        
        # Desabilita botões
        self.scan_button.setEnabled(False)
        self.clean_button.setEnabled(False)
        self.clean_all_button.setEnabled(False)
        
        # Mostra progresso
        self.progress_bar.setVisible(True)
        self.status_label.setText("Iniciando varredura...")
        
        # Limpa tabela anterior
        self.files_table.setRowCount(0)
        self.scanned_files = []
        
        # Cria e inicia thread
        self.scan_thread = ScanThread(self.scanner, drives)
        self.scan_thread.finished.connect(self._on_scan_finished)
        self.scan_thread.error.connect(self._on_scan_error)
        self.scan_thread.start()
    
    def _on_scan_finished(self, files: List[FileInfo]):
        """Callback quando a varredura termina"""
        self.scanned_files = files
        
        # Atualiza UI
        self.progress_bar.setVisible(False)
        self.scan_button.setEnabled(True)
        
        if files:
            self.clean_button.setEnabled(True)
            self.clean_all_button.setEnabled(True)
            self.status_label.setText(f"Varredura concluída! {len(files)} arquivos encontrados.")
        else:
            self.status_label.setText("Nenhum arquivo desnecessário encontrado.")
        
        # Preenche tabela
        self._populate_table()
        self._update_statistics()
    
    def _on_scan_error(self, error_msg: str):
        """Callback quando ocorre erro na varredura"""
        self.progress_bar.setVisible(False)
        self.scan_button.setEnabled(True)
        self.status_label.setText(f"Erro: {error_msg}")
        QMessageBox.critical(self, "Erro", f"Erro durante a varredura:\n{error_msg}")
    
    def _populate_table(self):
        """Preenche a tabela com arquivos encontrados"""
        self.files_table.setRowCount(len(self.scanned_files))
        
        for row, file_info in enumerate(self.scanned_files):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.files_table.setCellWidget(row, 0, checkbox)
            
            # Caminho
            path_item = QTableWidgetItem(file_info.path)
            path_item.setToolTip(file_info.path)
            self.files_table.setItem(row, 1, path_item)
            
            # Categoria
            category_item = QTableWidgetItem(file_info.category)
            self.files_table.setItem(row, 2, category_item)
            
            # Tamanho
            if file_info.size_mb < 1:
                size_text = f"{file_info.size / 1024:.2f} KB"
            elif file_info.size_mb < 1024:
                size_text = f"{file_info.size_mb:.2f} MB"
            else:
                size_text = f"{file_info.size_gb:.2f} GB"
            size_item = QTableWidgetItem(size_text)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.files_table.setItem(row, 3, size_item)
            
            # Última modificação
            import datetime
            mod_time = datetime.datetime.fromtimestamp(file_info.last_modified)
            time_item = QTableWidgetItem(mod_time.strftime("%Y-%m-%d %H:%M:%S"))
            self.files_table.setItem(row, 4, time_item)
    
    def _update_statistics(self):
        """Atualiza as estatísticas exibidas"""
        if not self.scanned_files:
            self.files_count_label.setText("Arquivos: 0")
            self.size_label.setText("Tamanho: 0 MB")
            self.category_label.setText("Categorias: 0")
            return
        
        total_files = len(self.scanned_files)
        total_size_mb = self.scanner.get_total_size_mb()
        categories = len(self.scanner.get_files_by_category())
        
        self.files_count_label.setText(f"Arquivos: {total_files}")
        
        if total_size_mb < 1024:
            self.size_label.setText(f"Tamanho: {total_size_mb:.2f} MB")
        else:
            total_size_gb = self.scanner.get_total_size_gb()
            self.size_label.setText(f"Tamanho: {total_size_gb:.2f} GB")
        
        self.category_label.setText(f"Categorias: {categories}")
    
    def _get_selected_files(self) -> List[str]:
        """Retorna lista de arquivos selecionados"""
        selected = []
        for row in range(self.files_table.rowCount()):
            checkbox = self.files_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                file_info = self.scanned_files[row]
                selected.append(file_info.path)
        return selected
    
    def _clean_selected(self):
        """Limpa apenas os arquivos selecionados"""
        selected = self._get_selected_files()
        
        if not selected:
            QMessageBox.warning(self, "Aviso", "Nenhum arquivo selecionado!")
            return
        
        # Confirmação
        reply = QMessageBox.question(
            self,
            "Confirmar Limpeza",
            f"Deseja realmente deletar {len(selected)} arquivo(s) selecionado(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._execute_cleanup(selected)
    
    def _clean_all(self):
        """Limpa todos os arquivos encontrados"""
        if not self.scanned_files:
            QMessageBox.warning(self, "Aviso", "Nenhum arquivo para limpar!")
            return
        
        # Confirmação
        reply = QMessageBox.question(
            self,
            "Confirmar Limpeza",
            f"Deseja realmente deletar TODOS os {len(self.scanned_files)} arquivo(s) encontrados?\n\n"
            "Esta ação não pode ser desfeita!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            all_files = [f.path for f in self.scanned_files]
            self._execute_cleanup(all_files)
    
    def _execute_cleanup(self, file_paths: List[str]):
        """Executa a limpeza dos arquivos"""
        self.status_label.setText("Limpando arquivos...")
        self.clean_button.setEnabled(False)
        self.clean_all_button.setEnabled(False)
        
        # Deleta arquivos
        results = self.scanner.delete_files(file_paths)
        
        # Conta sucessos e falhas
        success_count = sum(1 for success in results.values() if success)
        fail_count = len(results) - success_count
        
        # Atualiza lista removendo arquivos deletados
        self.scanned_files = [
            f for f in self.scanned_files
            if f.path not in results or not results[f.path]
        ]
        
        # Atualiza UI
        self._populate_table()
        self._update_statistics()
        
        self.status_label.setText(
            f"Limpeza concluída! {success_count} deletado(s), {fail_count} erro(s)."
        )
        
        if fail_count > 0:
            QMessageBox.warning(
                self,
                "Limpeza Concluída",
                f"{success_count} arquivo(s) deletado(s) com sucesso.\n"
                f"{fail_count} arquivo(s) não puderam ser deletados."
            )
        else:
            QMessageBox.information(
                self,
                "Sucesso",
                f"{success_count} arquivo(s) deletado(s) com sucesso!"
            )
        
        self.clean_button.setEnabled(len(self.scanned_files) > 0)
        self.clean_all_button.setEnabled(len(self.scanned_files) > 0)
