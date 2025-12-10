# Documentação Step-by-Step - Parsews

## Visão Geral do Projeto

O Parsews é uma aplicação Python desenvolvida para identificar e eliminar arquivos desnecessários do sistema Windows, otimizando o armazenamento sem comprometer arquivos importantes do sistema.

## Estrutura do Projeto

```
Parsews-ClearUp/
├── main.py                      # Ponto de entrada da aplicação
├── requirements.txt             # Dependências do projeto
├── README.md                    # Documentação principal
├── backend/                     # Módulo de backend
│   ├── __init__.py             # Inicialização do módulo backend
│   ├── file_scanner.py         # Scanner de arquivos desnecessários
│   └── safety_checker.py       # Sistema de segurança
├── frontend/                    # Módulo de frontend
│   ├── __init__.py             # Inicialização do módulo frontend
│   └── main_window.py         # Interface gráfica principal
└── docs/                        # Documentação
    └── step-by-step.md         # Este arquivo
```

## Arquivos e Suas Funções

### 1. main.py
**Função:** Ponto de entrada da aplicação
- Inicializa a aplicação PySide6 (QApplication)
- Cria e exibe a janela principal
- Gerencia o loop de eventos da aplicação

**Responsabilidades:**
- Configurar o nome e organização da aplicação
- Iniciar o ciclo de vida da aplicação gráfica

### 2. backend/safety_checker.py
**Função:** Sistema de segurança para proteger arquivos importantes
- Define diretórios protegidos do Windows (Windows, Program Files, etc.)
- Define extensões críticas que nunca devem ser deletadas (.exe, .dll, .sys, etc.)
- Define nomes de arquivos críticos do sistema (boot.ini, ntldr, etc.)
- Verifica se um arquivo é seguro para deletar antes de qualquer operação

**Principais Métodos:**
- `is_safe_to_delete(file_path)`: Verifica se um arquivo pode ser deletado com segurança
- `_is_temporary_file(file_path)`: Identifica arquivos temporários conhecidos
- `get_protected_directories()`: Retorna lista de diretórios protegidos
- `add_custom_protected_directory(directory)`: Permite adicionar diretórios customizados

**Segurança Implementada:**
- Proteção de diretórios críticos do sistema
- Proteção de extensões de arquivos executáveis e do sistema
- Proteção de arquivos com nomes críticos
- Exceções para arquivos temporários em locais seguros

### 3. backend/file_scanner.py
**Função:** Scanner que identifica arquivos desnecessários no sistema
- Escaneia unidades de disco em busca de arquivos desnecessários
- Categoriza arquivos encontrados (cache, temporários, logs, etc.)
- Calcula tamanho total dos arquivos encontrados
- Executa a limpeza de arquivos selecionados

**Principais Classes:**
- `FileInfo`: Dataclass que armazena informações sobre cada arquivo encontrado
  - path: Caminho completo do arquivo
  - size: Tamanho em bytes
  - category: Categoria do arquivo (cache, temporary, logs, etc.)
  - last_modified: Timestamp da última modificação
  - is_safe: Se o arquivo é seguro para deletar

- `FileScanner`: Classe principal do scanner
  - `scan_drives()`: Escaneia unidades de disco
  - `_scan_directory()`: Escaneia recursivamente um diretório
  - `_analyze_file()`: Analisa um arquivo individual
  - `_categorize_file()`: Categoriza arquivo baseado em padrões
  - `delete_files()`: Deleta uma lista de arquivos

**Categorias de Arquivos Detectados:**
1. **Cache**: Arquivos de cache de aplicativos
2. **Temporary**: Arquivos temporários (.tmp, .bak, .old)
3. **Logs**: Arquivos de log do sistema e aplicativos
4. **Prefetch**: Arquivos de prefetch do Windows
5. **Recycle Bin**: Arquivos na lixeira
6. **Downloads Old**: Arquivos antigos na pasta Downloads (mais de 90 dias)

### 4. frontend/main_window.py
**Função:** Interface gráfica da aplicação usando PySide6
- Fornece interface visual para interação com o usuário
- Exibe arquivos encontrados em uma tabela
- Permite seleção individual de arquivos para limpeza
- Mostra estatísticas da varredura
- Gerencia o processo de varredura em thread separada

**Principais Componentes:**
- `MainWindow`: Janela principal da aplicação
  - Título e cabeçalho
  - Controles (seleção de drives, botões de ação)
  - Barra de progresso
  - Estatísticas (contagem, tamanho, categorias)
  - Tabela de arquivos encontrados

- `ScanThread`: Thread para executar varredura em background
  - Evita travar a interface durante a varredura
  - Emite sinais de progresso e conclusão
  - Trata erros durante a varredura

**Funcionalidades da UI:**
1. **Seleção de Unidades**: Combo box para selecionar qual unidade escanear
2. **Botão Escanear**: Inicia a varredura de arquivos
3. **Botão Limpar Selecionados**: Deleta apenas arquivos marcados na tabela
4. **Botão Limpar Tudo**: Deleta todos os arquivos encontrados
5. **Tabela de Arquivos**: Exibe arquivos com checkbox, caminho, categoria, tamanho e data
6. **Estatísticas**: Mostra contagem total, tamanho total e número de categorias

**Estilos Aplicados:**
- Design moderno com cores suaves
- Botões verdes para ações principais
- Tabela com cores alternadas para melhor legibilidade
- Barra de progresso animada
- Interface responsiva e agradável

## Fluxo de Funcionamento

### 1. Inicialização
1. Usuário executa `main.py`
2. Aplicação PySide6 é inicializada
3. `MainWindow` é criada e exibida
4. Interface mostra estado inicial "Pronto para escanear"

### 2. Varredura
1. Usuário seleciona unidade(s) para escanear
2. Usuário clica em "Escanear"
3. `ScanThread` é criada e iniciada
4. `FileScanner` percorre diretórios recursivamente
5. Para cada arquivo encontrado:
   - `SafetyChecker` verifica se é seguro deletar
   - Se seguro, `FileScanner` categoriza o arquivo
   - Arquivo é adicionado à lista de resultados
6. Progresso é atualizado na interface
7. Ao concluir, tabela é preenchida com resultados

### 3. Limpeza
1. Usuário seleciona arquivos na tabela (ou escolhe "Limpar Tudo")
2. Usuário clica em botão de limpeza
3. Diálogo de confirmação é exibido
4. Se confirmado, `FileScanner.delete_files()` é chamado
5. Para cada arquivo:
   - `SafetyChecker` verifica segurança novamente
   - Arquivo é deletado se seguro
6. Tabela e estatísticas são atualizadas
7. Mensagem de sucesso/erro é exibida

## Segurança

O Parsews implementa múltiplas camadas de segurança:

1. **Diretórios Protegidos**: Lista de diretórios críticos do Windows que nunca são escaneados ou deletados
2. **Extensões Protegidas**: Extensões de arquivos executáveis e do sistema são protegidas
3. **Nomes Protegidos**: Arquivos com nomes críticos do sistema são protegidos
4. **Verificação Dupla**: Arquivos são verificados antes de escanear e antes de deletar
5. **Exceções Inteligentes**: Arquivos temporários em locais seguros são permitidos mesmo em diretórios protegidos

## Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **PySide6**: Framework para interface gráfica
- **psutil**: Biblioteca para informações do sistema (futuro uso)
- **pathlib**: Manipulação de caminhos de arquivos
- **dataclasses**: Estruturas de dados para informações de arquivos
- **threading**: Execução de varredura em background

## Melhorias Futuras

1. Adicionar mais categorias de arquivos desnecessários
2. Implementar filtros avançados na tabela
3. Adicionar histórico de limpezas
4. Implementar agendamento de limpezas automáticas
5. Adicionar suporte para múltiplos idiomas
6. Implementar modo de análise apenas (sem deletar)
7. Adicionar relatórios detalhados de limpeza
8. Melhorar detecção de arquivos duplicados

## Notas de Desenvolvimento

- A varredura é executada em thread separada para não travar a UI
- A segurança é verificada em múltiplos pontos para garantir proteção
- A interface é responsiva e atualiza em tempo real
- O código segue boas práticas de Python e PySide6
- Documentação inline explica funcionalidades complexas
