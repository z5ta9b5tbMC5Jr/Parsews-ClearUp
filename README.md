# Parsews - Limpador de Arquivos

Parsews é um programa desenvolvido nativamente em Python que ajuda a identificar e eliminar arquivos desnecessários do seu computador, otimizando o armazenamento sem comprometer arquivos importantes do sistema.

## Características

- Interface gráfica moderna e responsiva usando PySide6
- Sistema rigoroso de segurança para evitar deletar arquivos importantes
- Detecção inteligente de arquivos desnecessários (cache, temporários, logs, etc.)
- Focado em sistemas Windows
- Análise detalhada antes da limpeza

## Requisitos

- Python 3.8 ou superior
- Windows 10/11
- PySide6
- psutil

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/z5ta9b5tbMC5Jr/Parsews-ClearUp.git
cd Parsews-ClearUp
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

Execute o programa:
```bash
python main.py
```

## Estrutura do Projeto

```
Parsews-ClearUp/
├── main.py                 # Ponto de entrada da aplicação
├── backend/                # Lógica de backend
│   ├── __init__.py
│   ├── file_scanner.py    # Scanner de arquivos
│   └── safety_checker.py  # Verificador de segurança
├── frontend/               # Interface gráfica
│   ├── __init__.py
│   └── main_window.py     # Janela principal
├── docs/                   # Documentação
│   └── step-by-step.md    # Documentação de desenvolvimento
└── requirements.txt        # Dependências
```

## Segurança

O Parsews implementa múltiplas camadas de segurança:
- Lista de diretórios protegidos do sistema Windows
- Verificação de extensões críticas
- Validação de arquivos do sistema
- Confirmação antes de deletar

## Licença

Este projeto está sob licença MIT.
