# 📦 CSVToolBox - Manual do Usuário / User Manual

---

## 🇧🇷 Português

### Introdução

**CSVToolBox** é uma caixa de ferramentas completa para manipulação de arquivos CSV, Excel e XML. Oferece uma interface gráfica moderna e intuitiva, além de suporte a linha de comando (CLI).

### Requisitos do Sistema

- Windows 10 ou superior (64-bit)
- Nenhuma instalação adicional necessária (executável standalone)

### Instalação

1. Baixe o arquivo `CSVToolBox.exe`
2. Coloque em qualquer pasta de sua preferência
3. Execute com duplo clique

### Ferramentas Disponíveis

#### 1. 🔗 Mesclar CSVs (CSV Merger)
Combina múltiplos arquivos CSV em um único arquivo.

**Como usar:**
1. Clique em "Adicionar Arquivos" para selecionar os CSVs
2. Organize a ordem se necessário
3. Clique em "Mesclar" e escolha o destino

#### 2. ✂️ Dividir CSV (CSV Splitter)
Divide um arquivo CSV grande em partes menores.

**Como usar:**
1. Selecione o arquivo CSV de origem
2. Escolha o método de divisão:
   - Por número de linhas
   - Por número de arquivos
3. Clique em "Dividir"

#### 3. 🧹 Limpar CSV (CSV Cleaner)
Remove linhas duplicadas e vazias do CSV.

**Como usar:**
1. Selecione o arquivo CSV
2. Marque as opções desejadas:
   - Remover duplicatas
   - Remover linhas vazias
3. Clique em "Limpar"

#### 4. 🔄 Converter CSV (CSV Converter)
Converte entre diferentes delimitadores e encodings.

**Como usar:**
1. Selecione o arquivo de origem
2. Escolha o encoding de entrada (auto-detectado)
3. Escolha o delimitador e encoding de saída
4. Clique em "Converter"

#### 5. 🔀 Transformar CSV (CSV Transformer)
Filtra, ordena e seleciona colunas específicas.

**Como usar:**
1. Carregue o arquivo CSV
2. Selecione as colunas desejadas
3. Aplique filtros se necessário
4. Defina ordenação
5. Clique em "Transformar"

#### 6. 📄 Parser XML (XML Parser)
Converte arquivos XML para formato CSV.

**Como usar:**
1. Selecione o arquivo XML
2. Escolha o elemento raiz para extração
3. Clique em "Converter para CSV"

#### 7. 📊 Excel para CSV (Excel to CSV)
Converte arquivos Excel (.xlsx, .xls, .xlsb) para CSV.

**Como usar:**
1. Selecione o arquivo Excel
2. Escolha a planilha (se houver múltiplas)
3. Configure delimitador e encoding de saída
4. Clique em "Converter"

#### 8. 🗑️ Limpador de Colunas (Column Cleaner)
Remove colunas específicas de um CSV.

**Como usar:**
1. Carregue o arquivo CSV
2. Selecione as colunas a remover
3. Clique em "Remover Colunas"

#### 9. 📝 Parser TXT (TXT Parser)
Converte arquivos TXT delimitados para CSV padronizado.

**Como usar:**
1. Selecione o arquivo TXT
2. Defina o delimitador de entrada
3. Configure o CSV de saída
4. Clique em "Converter"

### Configurações

Acesse as configurações pelo ícone ⚙️ na barra lateral:

- **Idioma**: Português ou English
- **Tema**: Escuro (padrão) ou Claro
- **Pasta padrão de saída**: Define onde os arquivos serão salvos

As configurações são salvas automaticamente em:
`Documentos\CSVToolBox\config.json`

### Modo CLI (Linha de Comando)

O CSVToolBox também pode ser usado via terminal:

```bash
# Ajuda geral
CSVToolBox.exe --help

# Mesclar CSVs
CSVToolBox.exe merge arquivo1.csv arquivo2.csv -o resultado.csv

# Dividir CSV por linhas
CSVToolBox.exe split arquivo.csv -l 1000

# Limpar CSV
CSVToolBox.exe clean arquivo.csv --remove-duplicates --remove-empty

# Converter encoding
CSVToolBox.exe convert arquivo.csv -e utf-8 -d ";"

# Excel para CSV
CSVToolBox.exe excel arquivo.xlsx -o saida.csv

# XML para CSV
CSVToolBox.exe xml arquivo.xml -o saida.csv
```

### Solução de Problemas

**Problema**: O programa não abre
**Solução**: Certifique-se de que está usando Windows 64-bit

**Problema**: Erro ao abrir arquivo CSV
**Solução**: Verifique se o arquivo não está aberto em outro programa

**Problema**: Caracteres estranhos no resultado
**Solução**: Tente alterar o encoding na conversão (UTF-8, Latin-1, etc.)

---

## 🇺🇸 English

### Introduction

**CSVToolBox** is a complete toolkit for manipulating CSV, Excel, and XML files. It offers a modern and intuitive graphical interface, plus command-line (CLI) support.

### System Requirements

- Windows 10 or higher (64-bit)
- No additional installation required (standalone executable)

### Installation

1. Download `CSVToolBox.exe`
2. Place it in any folder of your choice
3. Run with double-click

### Available Tools

#### 1. 🔗 CSV Merger
Combines multiple CSV files into a single file.

**How to use:**
1. Click "Add Files" to select CSVs
2. Arrange the order if needed
3. Click "Merge" and choose the destination

#### 2. ✂️ CSV Splitter
Splits a large CSV file into smaller parts.

**How to use:**
1. Select the source CSV file
2. Choose the split method:
   - By number of rows
   - By number of files
3. Click "Split"

#### 3. 🧹 CSV Cleaner
Removes duplicate and empty rows from CSV.

**How to use:**
1. Select the CSV file
2. Check the desired options:
   - Remove duplicates
   - Remove empty rows
3. Click "Clean"

#### 4. 🔄 CSV Converter
Converts between different delimiters and encodings.

**How to use:**
1. Select the source file
2. Choose input encoding (auto-detected)
3. Choose output delimiter and encoding
4. Click "Convert"

#### 5. 🔀 CSV Transformer
Filters, sorts, and selects specific columns.

**How to use:**
1. Load the CSV file
2. Select the desired columns
3. Apply filters if needed
4. Set sorting
5. Click "Transform"

#### 6. 📄 XML Parser
Converts XML files to CSV format.

**How to use:**
1. Select the XML file
2. Choose the root element for extraction
3. Click "Convert to CSV"

#### 7. 📊 Excel to CSV
Converts Excel files (.xlsx, .xls, .xlsb) to CSV.

**How to use:**
1. Select the Excel file
2. Choose the worksheet (if multiple)
3. Configure output delimiter and encoding
4. Click "Convert"

#### 8. 🗑️ Column Cleaner
Removes specific columns from a CSV.

**How to use:**
1. Load the CSV file
2. Select columns to remove
3. Click "Remove Columns"

#### 9. 📝 TXT Parser
Converts delimited TXT files to standardized CSV.

**How to use:**
1. Select the TXT file
2. Define the input delimiter
3. Configure the output CSV
4. Click "Convert"

### Settings

Access settings via the ⚙️ icon in the sidebar:

- **Language**: Português or English
- **Theme**: Dark (default) or Light
- **Default output folder**: Sets where files will be saved

Settings are automatically saved to:
`Documents\CSVToolBox\config.json`

### CLI Mode (Command Line)

CSVToolBox can also be used via terminal:

```bash
# General help
CSVToolBox.exe --help

# Merge CSVs
CSVToolBox.exe merge file1.csv file2.csv -o result.csv

# Split CSV by rows
CSVToolBox.exe split file.csv -l 1000

# Clean CSV
CSVToolBox.exe clean file.csv --remove-duplicates --remove-empty

# Convert encoding
CSVToolBox.exe convert file.csv -e utf-8 -d ";"

# Excel to CSV
CSVToolBox.exe excel file.xlsx -o output.csv

# XML to CSV
CSVToolBox.exe xml file.xml -o output.csv
```

### Troubleshooting

**Problem**: Program won't open
**Solution**: Make sure you're using 64-bit Windows

**Problem**: Error opening CSV file
**Solution**: Check if the file isn't open in another program

**Problem**: Strange characters in result
**Solution**: Try changing the encoding in conversion (UTF-8, Latin-1, etc.)

---

## 📜 Licença / License

MIT License - © 2025 Guilherme Pinheiro

---

## 🔗 Links

- **GitHub**: https://github.com/GuilhermeP96/CSVToolBox
- **Autor / Author**: Guilherme Pinheiro
