# 📊 CSVToolBox - Manual do Usuário

## Índice

1. [Introdução](#introdução)
2. [Primeiros Passos](#primeiros-passos)
3. [Ferramentas Disponíveis](#ferramentas-disponíveis)
4. [Workflow Orchestrator](#workflow-orchestrator)
5. [Verticalização e Higienização](#verticalização-e-higienização)
6. [Excel Multi-Perfis](#excel-multi-perfis)
7. [Estrutura do config.json](#estrutura-do-configjson)
8. [Criando Novos Perfis](#criando-novos-perfis)
9. [Dicas e Atalhos](#dicas-e-atalhos)
10. [Suporte](#suporte)

---

## Introdução

O **CSVToolBox** é uma aplicação desktop para manipulação e conversão de arquivos CSV e Excel. Desenvolvido com interface gráfica moderna, oferece diversas ferramentas para:

- Consolidar múltiplos CSVs em um único arquivo
- Dividir arquivos grandes em partes menores
- Limpar e normalizar dados
- Converter entre formatos (Excel, XML, TXT → CSV)
- Verticalizar dados (unpivot) e higienizar
- **Criar workflows automatizados com múltiplas etapas**
- Transformar dados com perfis configuráveis

---

## Primeiros Passos

### Instalação
1. Baixe o arquivo `CSVToolBox.exe`
2. Coloque em uma pasta de sua preferência
3. Execute o aplicativo - não requer instalação!

### Primeira Execução
Na primeira execução, o aplicativo criará automaticamente:
- `config.json` no diretório da aplicação (configurações e perfis)
- Pasta `Documentos\CSVToolBox\` para histórico e presets

### Interface Principal

Ao abrir o CSVToolBox, você verá:
- **Menu lateral esquerdo**: Lista de todas as ferramentas
- **Área central**: Cards com acesso rápido às funcionalidades
- **Barra inferior**: Perfis salvos e histórico de processos recentes

---

## Ferramentas Disponíveis

### 📁 Consolidar CSVs (Merger)
Combina múltiplos arquivos CSV em um único arquivo.

**Uso:**
1. Clique em "Adicionar Arquivos" ou "Adicionar Pasta"
2. Configure separador e encoding
3. Escolha se deseja remover duplicatas
4. Defina o arquivo de saída
5. Clique em "Executar"

### ✂️ Dividir CSV (Splitter)
Divide um arquivo CSV grande em partes menores.

**Opções de divisão:**
- Por número de linhas (ex: 50.000 linhas por arquivo)
- Por tamanho de arquivo
- Por valor de uma coluna específica

### 🧹 Limpar CSV (Cleaner)
Remove linhas vazias, duplicatas e caracteres indesejados.

**Funcionalidades:**
- Remover aspas extras
- Remover espaços em branco
- Remover quebras de linha
- Remover caracteres especiais
- Trim de colunas
- Remover linhas vazias
- Substituição personalizada (com suporte a regex)

### 🔄 Converter Formato (Converter)
Converte entre diferentes formatos de dados e encodings.

### ⚙️ Transformar Dados (Transformer)
Aplica transformações usando tabela DE-PARA (lookup table).

### 📄 XML para CSV
Converte arquivos XML para formato CSV tabular.

### 📊 Excel para CSV
Conversão simples de Excel (.xlsx, .xls) para CSV.

### 📊 Excel Multi-Perfis
Conversão avançada de Excel com perfis configuráveis. Veja seção dedicada abaixo.

### 🔧 Limpar Colunas
Normaliza nomes de colunas para padrão Oracle/SQL.

### 📝 TXT para CSV
Converte arquivos de texto delimitado ou largura fixa para CSV.

### 📊 Verticalizar Dados
Transforma dados horizontais em verticais (unpivot) e aplica higienização. Veja seção dedicada abaixo.

### 🔀 Workflow Orchestrator
Cria e executa sequências de processos automatizados. Veja seção dedicada abaixo.

---

## Workflow Orchestrator

O **Workflow Orchestrator** permite criar sequências de processos que são executados automaticamente em ordem.

### Como Funciona

1. **Configure uma ferramenta**: Vá em qualquer ferramenta (Limpar CSV, Consolidar, etc.)
2. **Defina os parâmetros**: Configure entrada, saída e opções
3. **Adicione ao Workflow**: Clique no botão roxo **"➕ Adicionar ao Workflow"**
4. **Encadeie etapas**: Ao adicionar, você pode escolher usar a saída da etapa anterior como entrada
5. **Execute tudo**: Vá ao Orchestrator e clique em **"▶️ Executar Tudo"**

### Recursos do Orchestrator

- **Fila visual**: Veja todas as etapas com status (pendente, executando, completo, erro)
- **Reordenar etapas**: Use as setas ↑↓ para mover etapas
- **Remover etapas**: Clique em ✖ para remover uma etapa
- **Salvar workflow**: Salve sua sequência como preset para reutilizar
- **Carregar workflow**: Carregue workflows salvos anteriormente
- **Log de execução**: Acompanhe o progresso em tempo real

### Exemplo de Workflow

1. **Etapa 1**: Consolidar 10 arquivos CSV em um único
2. **Etapa 2**: Limpar dados (remover duplicatas, trim)
3. **Etapa 3**: Dividir em arquivos de 50.000 linhas

Cada etapa usa automaticamente a saída da anterior!

### Salvando Workflows

Os workflows são salvos em `Documentos\CSVToolBox\workflows\` como arquivos `.workflow.json` e podem ser compartilhados com outros usuários.

---

## Verticalização e Higienização

A ferramenta **Verticalizar Dados** possui duas abas:

### Aba Verticalização (Unpivot)

Transforma colunas de período em linhas. Ideal para:
- Planilhas com meses como colunas (JAN, FEV, MAR...)
- Relatórios com anos como colunas (2022, 2023, 2024...)

**Configurações:**
- **Colunas Fixas**: Colunas que permanecem como identificadores (ex: CODIGO, DESCRICAO)
- **Colunas a Verticalizar**: Colunas que serão transformadas em linhas
- **Padrão de Período (Regex)**: Para detectar automaticamente colunas de período
- **Nome da Coluna Variável**: Nome da nova coluna de período (ex: ANO_MES)
- **Nome da Coluna Valor**: Nome da nova coluna de valores (ex: QUANTIDADE)

### Aba Higienização (Sanitização)

Limpa e normaliza os dados:
- **Remover espaços extras**: Trim em todas as células
- **Remover acentos**: Converte "São Paulo" para "Sao Paulo"
- **Conversão de caso**: MAIÚSCULAS, minúsculas ou Título
- **Remover duplicatas**: Elimina linhas repetidas
- **Remover linhas vazias**: Elimina linhas sem dados
- **Substituições personalizadas**: Formato `valor_original→valor_novo`

---

## Excel Multi-Perfis

Esta é a ferramenta mais poderosa do CSVToolBox para conversões complexas de Excel.

### Modos de Conversão

#### Modo Direct (Mapeamento Direto)
Extrai colunas específicas e mapeia para novos nomes.

**Use quando:**
- Precisa selecionar apenas algumas colunas
- Precisa renomear colunas
- Dados são tabulares simples

#### Modo Vertical (Transpor/Unpivot)
Transforma colunas de período em linhas.

**Use quando:**
- Meses/anos são colunas na planilha
- Precisa de dados em formato de série temporal

### Detecção Automática de Perfil

Ao selecionar um arquivo Excel:
1. A ferramenta lê os nomes das abas
2. Compara com perfis no `config.json`
3. Seleciona automaticamente o perfil correspondente

**Indicadores:**
- ✅ Verde: Perfil detectado automaticamente
- ⚠️ Laranja: Nenhum perfil encontrado
- 📋 Branco: Seleção manual

---

## Estrutura do config.json

O arquivo `config.json` armazena todas as configurações e perfis.

### Seções Principais

```json
{
    "profiles": {},           // Perfis salvos das ferramentas
    "settings": {},           // Configurações gerais
    "excel": {},              // Config padrão para leitura Excel
    "csv": {},                // Config padrão para geração CSV
    "header": {},             // Normalização de cabeçalhos
    "xlsx_profiles": {}       // Perfis Excel Multi-Perfis
}
```

### Configurações CSV

| Parâmetro | Valores | Descrição |
|-----------|---------|-----------|
| delimiter | `;` `,` `\|` `\t` | Separador de campos |
| quotechar | `"` `'` | Caractere de aspas |
| encoding | `utf-8` `latin-1` `cp1252` | Codificação |

### Normalização de Headers

| Parâmetro | Descrição |
|-----------|-----------|
| normalize | Ativa normalização |
| case | `upper`, `lower`, `keep` |
| strip_accents | Remove acentos |
| deduplicate | Renomeia colunas duplicadas |

---

## Criando Novos Perfis

### Perfil Modo Direct

```json
"MeuPerfil_Direct": {
    "name": "MeuPerfil_Direct",
    "mode": "direct",
    "excel": {
        "sheet_name": "Dados",
        "header_row": 0,
        "columns": ["Coluna1", "Coluna2", "Coluna3"],
        "numeric_columns": ["Coluna2"]
    },
    "header": {
        "mapping": {
            "Coluna1": "COL_1",
            "Coluna2": "COL_2",
            "Coluna3": "COL_3"
        }
    }
}
```

### Perfil Modo Vertical

```json
"MeuPerfil_Vertical": {
    "name": "MeuPerfil_Vertical",
    "mode": "vertical",
    "excel": {
        "sheet_name": "Relatorio",
        "header_row": 0,
        "fixed_columns": ["Produto", "Categoria"],
        "period_pattern": "^\\d{4}\\.\\d{2}$"
    },
    "output": {
        "date_column_name": "ANO_MES",
        "value_column_name": "VALOR"
    }
}
```

### Padrões de Período Suportados

| Formato | Regex | Exemplo |
|---------|-------|---------|
| YYYY.MM | `^\\d{4}\\.\\d{2}$` | 2024.01 |
| mmm-yy | `^[a-zA-Z]{3}-\\d{2}$` | jan-24 |

---

## Dicas e Atalhos

### Produtividade

1. **Use Perfis**: Salve configurações para processos recorrentes
2. **Use Workflows**: Automatize sequências de tarefas repetitivas
3. **Detecção Automática**: Nomeie sheets de forma consistente para auto-detecção
4. **Histórico**: Acesse rapidamente processos recentes na barra inferior
5. **Backup**: Mantenha cópia do `config.json` com seus perfis

### Botão "Adicionar ao Workflow"

Todas as ferramentas possuem o botão roxo **"➕ Adicionar ao Workflow"** que permite:
- Salvar a configuração atual como etapa
- Encadear com etapas anteriores
- Criar automações complexas sem repetir trabalho

---

## Suporte

Para dúvidas, suporte ou atualizações, acesse:

🔗 **https://github.com/GuilhermeP96/CSVToolBox**

### Reportando Problemas

Ao reportar um bug, inclua:
- Descrição do problema
- Passos para reproduzir
- Captura de tela do log de erros (se houver)

---

**CSVToolBox** | Desenvolvido por Guilherme Pinheiro
