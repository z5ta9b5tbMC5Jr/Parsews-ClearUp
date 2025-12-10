"""
Sistema de segurança para evitar deletar arquivos importantes
"""

import os
import platform
from pathlib import Path
from typing import Set, List, Tuple


class SafetyChecker:
    """Verifica se um arquivo ou diretório é seguro para deletar"""
    
    # Diretórios críticos do Windows que nunca devem ser deletados
    PROTECTED_DIRECTORIES: Set[str] = {
        "C:\\Windows",
        "C:\\Windows\\System32",
        "C:\\Windows\\SysWOW64",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\ProgramData",
        "C:\\Users",
        "C:\\$Recycle.Bin",
        "C:\\System Volume Information",
        "C:\\Recovery",
        "C:\\Boot",
        "C:\\PerfLogs",
    }
    
    # Extensões críticas que nunca devem ser deletadas
    PROTECTED_EXTENSIONS: Set[str] = {
        ".exe", ".dll", ".sys", ".drv", ".ocx", ".cpl",
        ".msi", ".msm", ".msp", ".bat", ".cmd", ".ps1",
        ".reg", ".inf", ".cat", ".cer", ".crt", ".key",
        ".pfx", ".p12", ".p7b", ".p7c", ".p7m", ".p7s",
    }
    
    # Nomes de arquivos críticos do sistema
    PROTECTED_FILENAMES: Set[str] = {
        "boot.ini", "ntldr", "ntdetect.com", "bootmgr",
        "bootmgr.efi", "bcd", "boot.sdi", "winload.exe",
        "winload.efi", "winresume.exe", "winresume.efi",
    }
    
    def __init__(self):
        """Inicializa o verificador de segurança"""
        self._normalize_protected_paths()
    
    def _normalize_protected_paths(self):
        """Normaliza os caminhos protegidos para o sistema atual"""
        if platform.system() != "Windows":
            return
        
        # Normaliza os caminhos protegidos
        normalized = set()
        for path in self.PROTECTED_DIRECTORIES:
            try:
                normalized.add(os.path.normpath(path))
            except Exception:
                continue
        self.PROTECTED_DIRECTORIES = normalized
    
    def is_safe_to_delete(self, file_path: str) -> Tuple[bool, str]:
        """
        Verifica se um arquivo é seguro para deletar
        
        Args:
            file_path: Caminho completo do arquivo
            
        Returns:
            Tupla (é_seguro, motivo)
        """
        try:
            path = Path(file_path)
            normalized_path = os.path.normpath(str(path.resolve()))
            
            # Verifica se está em diretório protegido
            for protected_dir in self.PROTECTED_DIRECTORIES:
                protected_normalized = os.path.normpath(protected_dir)
                if normalized_path.startswith(protected_normalized):
                    # Exceção: permite arquivos temporários em diretórios protegidos
                    if not self._is_temporary_file(normalized_path):
                        return False, f"Arquivo está em diretório protegido: {protected_dir}"
            
            # Verifica extensão protegida
            if path.suffix.lower() in self.PROTECTED_EXTENSIONS:
                # Exceção: permite alguns arquivos temporários com extensões protegidas
                if not self._is_temporary_file(normalized_path):
                    return False, f"Extensão protegida: {path.suffix}"
            
            # Verifica nome de arquivo protegido
            if path.name.lower() in self.PROTECTED_FILENAMES:
                return False, f"Nome de arquivo protegido: {path.name}"
            
            # Verifica se é arquivo do sistema (atributo)
            if path.exists():
                try:
                    import stat
                    file_stat = os.stat(file_path)
                    # Verifica se é arquivo oculto ou sistema (simplificado)
                    if path.name.startswith('.'):
                        return False, "Arquivo oculto do sistema"
                except Exception:
                    pass
            
            return True, "Arquivo seguro para deletar"
            
        except Exception as e:
            return False, f"Erro ao verificar segurança: {str(e)}"
    
    def _is_temporary_file(self, file_path: str) -> bool:
        """
        Verifica se é um arquivo temporário conhecido
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se for arquivo temporário seguro
        """
        temp_indicators = [
            "\\Temp\\",
            "\\tmp\\",
            "\\AppData\\Local\\Temp\\",
            "\\AppData\\Local\\Microsoft\\Windows\\INetCache\\",
            "\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files\\",
            "\\Windows\\Temp\\",
            "\\Windows\\Prefetch\\",
            "\\Windows\\SoftwareDistribution\\Download\\",
        ]
        
        normalized = file_path.lower()
        return any(indicator.lower() in normalized for indicator in temp_indicators)
    
    def get_protected_directories(self) -> List[str]:
        """Retorna lista de diretórios protegidos"""
        return sorted(list(self.PROTECTED_DIRECTORIES))
    
    def add_custom_protected_directory(self, directory: str):
        """Adiciona um diretório customizado à lista de protegidos"""
        normalized = os.path.normpath(directory)
        self.PROTECTED_DIRECTORIES.add(normalized)
