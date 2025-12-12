# CSVToolBox

Uma caixa de ferramentas completa para tratamento de arquivos CSV com interface gráfica moderna.

## 📋 Funcionalidades

### 📊 Consolidar CSVs
- Mescle múltiplos arquivos CSV em um único arquivo
- Suporte a diferentes encodings e separadores
- Opção para remover linhas duplicadas
- Detecção automática de encoding (chardet)

### ✂️ Dividir CSV
- Divida arquivos CSV grandes em partes menores
- Configure número máximo de linhas por arquivo
- Presets rápidos (10K, 50K, 100K, 500K, 1M)
- Conversão de formato de dados (BR, EUA, EU, UK)
- Charset e separador diferentes para origem e destino
- Opção de aspas em todos os campos
- Log de processo em tempo real

### 🧹 Limpar CSV
- Remover aspas (simples e duplas)
- Remover espaços extras
- Remover quebras de linha
- Remover caracteres especiais
- Trim em todas as colunas
- Substituição customizada (com suporte a Regex)

### 🔄 Converter Formato
Converta entre formatos:
- CSV ↔ Excel (XLSX)
- CSV ↔ JSON
- CSV ↔ XML
- CSV ↔ TXT

### ⚙️ Transformar Dados
- **DE-PARA**: Substitua valores usando tabela de referência
- **Filtro de Colunas**: Selecione quais colunas manter
- **Transformações**:
  - Converter para MAIÚSCULAS/minúsculas
  - Remover acentos
  - Adicionar prefixo/sufixo
  - Trim (remover espaços)

### 📄 XML para CSV
- Converta arquivos XML para CSV
- Detecção automática de estrutura
- Suporte a namespaces XML
- Concatenação de valores repetidos
- Modos de parsing: auto, flat, nested
- Opções de quoting (QUOTE_ALL, QUOTE_MINIMAL, etc.)

## 💾 Sistema de Perfis

Salve configurações de processos recorrentes para reutilização rápida:
- Crie perfis com nome personalizado
- Carregue perfis diretamente da sidebar
- Exporte/importe perfis para compartilhar

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd CSVToolBox
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## ▶️ Execução

```bash
python main.py
```

## 📦 Dependências

- **customtkinter**: Interface gráfica moderna
- **pandas**: Manipulação de dados
- **openpyxl**: Suporte a arquivos Excel
- **chardet**: Detecção de encoding
- **tqdm**: Barra de progresso (operações em batch)

## 🎨 Interface

A aplicação utiliza CustomTkinter para uma interface moderna com:
- Tema escuro por padrão (configurável)
- Sidebar com navegação entre ferramentas
- Lista de perfis salvos para acesso rápido
- Barra de progresso para operações longas
- Feedback visual de status

## 📁 Estrutura do Projeto

```
CSVToolBox/
├── main.py                    # Aplicação principal
├── config.json                # Configurações e perfis salvos
├── requirements.txt           # Dependências
├── README.md                  # Este arquivo
└── tools/
    ├── __init__.py
    ├── profile_manager.py     # Gerenciador de perfis
    ├── csv_merger.py          # Ferramenta de consolidação
    ├── csv_splitter.py        # Ferramenta de divisão
    ├── csv_cleaner.py         # Ferramenta de limpeza
    ├── csv_converter.py       # Ferramenta de conversão
    ├── csv_transformer.py     # Ferramenta de transformação
    └── xml_parser.py          # Ferramenta XML para CSV
```

## 🔧 Configurações

O arquivo `config.json` armazena:
- Perfis salvos com todas as configurações
- Arquivos recentes
- Configurações globais (tema, encoding padrão, etc.)

## 📝 Exemplo de Uso

### Consolidar arquivos de vendas mensais:
1. Abra a ferramenta "Consolidar CSVs"
2. Adicione os arquivos CSV ou selecione uma pasta
3. Configure separador (;) e encoding (utf-8)
4. Marque "Remover duplicatas" se necessário
5. Defina o arquivo de saída
6. Clique em "Executar Consolidação"
7. Salve como perfil "Vendas Mensais" para reutilizar

### Substituir códigos usando DE-PARA:
1. Abra "Transformar Dados"
2. Carregue o arquivo CSV
3. Na aba "DE-PARA", carregue a tabela de referência
4. Selecione as colunas DE e PARA
5. Habilite a substituição e execute
6. Salve como perfil para uso futuro

## 📄 Licença

MIT License

## 👤 Autor

Desenvolvido como parte do projeto de consolidação de ferramentas CSV.
