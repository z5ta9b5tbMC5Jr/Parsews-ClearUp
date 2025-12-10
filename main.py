"""
Parsews - Limpador de Arquivos
Ponto de entrada da aplicação
"""

import sys
from PySide6.QtWidgets import QApplication
from frontend.main_window import MainWindow


def main():
    """Função principal que inicia a aplicação"""
    app = QApplication(sys.argv)
    app.setApplicationName("Parsews")
    app.setOrganizationName("Parsews")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
