"""
Scanner de arquivos desnecessários
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from backend.safety_checker import SafetyChecker


@dataclass
class FileInfo:
    """Informações sobre um arquivo encontrado"""
    path: str
    size: int
    category: str
    last_modified: float
    is_safe: bool
    reason: str = ""
    
    def __post_init__(self):
        """Converte tamanho para formato legível"""
        self.size_mb = self.size / (1024 * 1024)
        self.size_gb = self.size / (1024 * 1024 * 1024)


class FileScanner:
    """Scanner que identifica arquivos desnecessários"""
    
    # Categorias de arquivos desnecessários
    CATEGORIES = {
        "cache": {
            "patterns": ["cache", "Cache", "CACHE"],
            "extensions": [".cache", ".tmp"],
            "paths": ["AppData\\Local\\Temp", "AppData\\Local\\Microsoft\\Windows\\INetCache"],
        },
        "temporary": {
            "patterns": ["temp", "Temp", "TEMP", "tmp", "TMP"],
            "extensions": [".tmp", ".temp", ".bak", ".old"],
            "paths": ["Temp", "tmp", "Windows\\Temp"],
        },
        "logs": {
            "patterns": ["log", "Log", "LOG"],
            "extensions": [".log", ".txt"],
            "paths": ["Logs", "logs"],
        },
        "prefetch": {
            "patterns": ["Prefetch"],
            "extensions": [".pf"],
            "paths": ["Windows\\Prefetch"],
        },
        "recycle_bin": {
            "patterns": ["$Recycle.Bin"],
            "extensions": [],
            "paths": ["$Recycle.Bin"],
        },
        "downloads_old": {
            "patterns": [],
            "extensions": [],
            "paths": ["Downloads"],
            "age_days": 90,  # Arquivos com mais de 90 dias
        },
    }
    
    def __init__(self):
        """Inicializa o scanner"""
        self.safety_checker = SafetyChecker()
        self.scanned_files: List[FileInfo] = []
        self.total_size = 0
        self.scan_progress_callback = None
    
    def set_progress_callback(self, callback):
        """Define callback para progresso da varredura"""
        self.scan_progress_callback = callback
    
    def scan_drives(self, drives: Optional[List[str]] = None) -> List[FileInfo]:
        """
        Escaneia unidades de disco em busca de arquivos desnecessários
        
        Args:
            drives: Lista de drives para escanear (ex: ['C:', 'D:']). 
                   Se None, escaneia todas as unidades disponíveis.
        
        Returns:
            Lista de FileInfo com arquivos encontrados
        """
        if drives is None:
            drives = self._get_available_drives()
        
        self.scanned_files = []
        self.total_size = 0
        
        for drive in drives:
            self._scan_directory(drive + "\\", drive)
        
        return self.scanned_files
    
    def _get_available_drives(self) -> List[str]:
        """Retorna lista de drives disponíveis no Windows"""
        import string
        drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:"
            if os.path.exists(drive + "\\"):
                drives.append(drive)
        return drives
    
    def _scan_directory(self, directory: str, root_drive: str, max_depth: int = 10, current_depth: int = 0):
        """
        Escaneia recursivamente um diretório
        
        Args:
            directory: Diretório para escanear
            root_drive: Drive raiz sendo escaneado
            max_depth: Profundidade máxima de recursão
            current_depth: Profundidade atual
        """
        if current_depth >= max_depth:
            return
        
        try:
            # Verifica se o diretório é seguro para escanear
            is_safe, reason = self.safety_checker.is_safe_to_delete(directory)
            if not is_safe and "diretório protegido" in reason.lower():
                return  # Pula diretórios protegidos completamente
            
            # Verifica se o diretório existe e é acessível
            if not os.path.exists(directory) or not os.path.isdir(directory):
                return
            
            # Notifica progresso
            if self.scan_progress_callback:
                self.scan_progress_callback(directory)
            
            # Escaneia arquivos no diretório atual
            try:
                entries = os.listdir(directory)
            except PermissionError:
                return  # Sem permissão, pula
            
            for entry in entries:
                entry_path = os.path.join(directory, entry)
                
                try:
                    # Verifica se é arquivo
                    if os.path.isfile(entry_path):
                        file_info = self._analyze_file(entry_path)
                        if file_info:
                            self.scanned_files.append(file_info)
                            self.total_size += file_info.size
                    
                    # Continua recursão para subdiretórios
                    elif os.path.isdir(entry_path):
                        self._scan_directory(entry_path, root_drive, max_depth, current_depth + 1)
                
                except (PermissionError, OSError):
                    continue  # Pula arquivos/diretórios inacessíveis
        
        except Exception:
            pass  # Continua mesmo em caso de erro
    
    def _analyze_file(self, file_path: str) -> Optional[FileInfo]:
        """
        Analisa um arquivo para determinar se é desnecessário
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            FileInfo se o arquivo for desnecessário, None caso contrário
        """
        try:
            path_obj = Path(file_path)
            file_name = path_obj.name.lower()
            file_ext = path_obj.suffix.lower()
            normalized_path = os.path.normpath(file_path).lower()
            
            # Verifica segurança primeiro
            is_safe, reason = self.safety_checker.is_safe_to_delete(file_path)
            if not is_safe:
                return None  # Não inclui arquivos não seguros
            
            # Obtém informações do arquivo
            stat = os.stat(file_path)
            file_size = stat.st_size
            last_modified = stat.st_mtime
            
            # Categoriza o arquivo
            category = self._categorize_file(file_name, file_ext, normalized_path, last_modified)
            
            if category:
                return FileInfo(
                    path=file_path,
                    size=file_size,
                    category=category,
                    last_modified=last_modified,
                    is_safe=True,
                    reason=""
                )
            
            return None
        
        except Exception:
            return None
    
    def _categorize_file(self, file_name: str, file_ext: str, file_path: str, last_modified: float) -> Optional[str]:
        """
        Categoriza um arquivo baseado em padrões
        
        Args:
            file_name: Nome do arquivo (lowercase)
            file_ext: Extensão do arquivo (lowercase)
            file_path: Caminho completo (lowercase, normalized)
            last_modified: Timestamp da última modificação
            
        Returns:
            Nome da categoria ou None se não for desnecessário
        """
        current_time = time.time()
        
        for category, config in self.CATEGORIES.items():
            # Verifica padrões no nome
            if config["patterns"]:
                if any(pattern.lower() in file_name for pattern in config["patterns"]):
                    # Verifica idade se necessário
                    if "age_days" in config:
                        age_days = (current_time - last_modified) / (24 * 3600)
                        if age_days < config["age_days"]:
                            continue
                    return category
            
            # Verifica extensões
            if config["extensions"]:
                if file_ext in config["extensions"]:
                    return category
            
            # Verifica caminhos
            if config["paths"]:
                if any(path.lower() in file_path for path in config["paths"]):
                    # Verifica idade se necessário
                    if "age_days" in config:
                        age_days = (current_time - last_modified) / (24 * 3600)
                        if age_days < config["age_days"]:
                            continue
                    return category
        
        return None
    
    def get_total_size_mb(self) -> float:
        """Retorna tamanho total em MB"""
        return self.total_size / (1024 * 1024)
    
    def get_total_size_gb(self) -> float:
        """Retorna tamanho total em GB"""
        return self.total_size / (1024 * 1024 * 1024)
    
    def get_files_by_category(self) -> Dict[str, List[FileInfo]]:
        """Retorna arquivos agrupados por categoria"""
        categorized = {}
        for file_info in self.scanned_files:
            if file_info.category not in categorized:
                categorized[file_info.category] = []
            categorized[file_info.category].append(file_info)
        return categorized
    
    def delete_files(self, file_paths: List[str]) -> Dict[str, bool]:
        """
        Deleta uma lista de arquivos
        
        Args:
            file_paths: Lista de caminhos de arquivos para deletar
            
        Returns:
            Dicionário com status de cada arquivo (True = deletado, False = erro)
        """
        results = {}
        
        for file_path in file_paths:
            try:
                # Verifica segurança novamente antes de deletar
                is_safe, reason = self.safety_checker.is_safe_to_delete(file_path)
                if not is_safe:
                    results[file_path] = False
                    continue
                
                # Deleta o arquivo
                if os.path.exists(file_path):
                    os.remove(file_path)
                    results[file_path] = True
                else:
                    results[file_path] = False
            
            except Exception:
                results[file_path] = False
        
        return results
