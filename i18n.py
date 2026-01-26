# Internationalization (i18n) module for CSVToolBox

import locale

import os

def get_system_language():

    """Detect system language, returns 'pt' or 'en'"""

    try:

        # Windows

        if os.name == 'nt':

            import ctypes

            windll = ctypes.windll.kernel32

            lang_id = windll.GetUserDefaultUILanguage()

            # Portuguese: 1046 (Brazil), 2070 (Portugal)

            if lang_id in [1046, 2070]:

                return 'pt'

            return 'en'

        else:

            # Linux/Mac

            lang = locale.getdefaultlocale()[0]

            if lang and lang.startswith('pt'):

                return 'pt'

            return 'en'

    except:

        return 'en'

# Current language

_current_lang = get_system_language()

def set_language(lang: str):

    """Set current language ('pt' or 'en')"""

    global _current_lang

    if lang in ['pt', 'en']:

        _current_lang = lang

def get_language() -> str:

    """Get current language"""

    return _current_lang

def t(key: str) -> str:

    """Translate a key to current language"""

    lang = _current_lang

    if key in TRANSLATIONS and lang in TRANSLATIONS[key]:

        return TRANSLATIONS[key][lang]

    # Fallback to English, then key itself

    if key in TRANSLATIONS and 'en' in TRANSLATIONS[key]:

        return TRANSLATIONS[key]['en']

    return key

# Translation dictionary

TRANSLATIONS = {

    # === App General ===

    "app_title": {

        "pt": "CSVToolBox - Caixa de Ferramentas CSV",

        "en": "CSVToolBox - CSV Toolkit"

    },

    "welcome_title": {

        "pt": "Bem-vindo ao CSVToolBox!",

        "en": "Welcome to CSVToolBox!"

    },

    "welcome_subtitle": {

        "pt": "Sua caixa de ferramentas para tratamento de arquivos CSV",

        "en": "Your toolkit for CSV file processing"

    },

    "tip_profiles": {

        "pt": "💪 Dica: Salve perfis para reutilizar configuraes em processos recorrentes",

        "en": "💪 Tip: Save profiles to reuse settings in recurring processes"

    },

    

    # === Menu ===

    "tools": {

        "pt": "FERRAMENTAS",

        "en": "TOOLS"

    },

    "profiles_saved": {

        "pt": "📋 PERFIS SALVOS",

        "en": "📋 SAVED PROFILES"

    },

    "recent": {

        "pt": "🕐 RECENTES",

        "en": "🕐 RECENT"

    },

    "settings": {

        "pt": "⚙️ Configuraes",

        "en": "⚙️ Settings"

    },

    "new_profile": {

        "pt": "+ Novo",

        "en": "+ New"

    },

    "clear": {

        "pt": "🗑️ Limpar",

        "en": "🗑️ Clear"

    },

    "no_profiles": {

        "pt": "Nenhum perfil salvo",

        "en": "No saved profiles"

    },

    "no_recent": {

        "pt": "Nenhum processo recente",

        "en": "No recent processes"

    },

    

    # === Tools Names ===

    "tool_merger": {
        "pt": "📁 Consolidar CSVs",
        "en": "📁 Merge CSVs"
    },

    "tool_splitter": {
        "pt": "✂️ Dividir CSV",
        "en": "✂️ Split CSV"
    },

    "tool_cleaner": {
        "pt": "🧹 Limpar CSV",
        "en": "🧹 Clean CSV"
    },

    "tool_converter": {
        "pt": "🔄 Converter Formato",
        "en": "🔄 Convert Format"
    },

    "tool_transformer": {
        "pt": "⚙️ Transformar Dados",
        "en": "⚙️ Transform Data"
    },

    "tool_xml_parser": {
        "pt": "📄 XML para CSV",
        "en": "📄 XML to CSV"
    },

    "tool_excel_to_csv": {
        "pt": "📊 Excel para CSV",
        "en": "📊 Excel to CSV"
    },

    "tool_column_cleaner": {
        "pt": "🔧 Limpar Colunas",
        "en": "🔧 Clean Columns"
    },

    "tool_txt_parser": {
        "pt": "📝 TXT para CSV",
        "en": "📝 TXT to CSV"
    },

    

    # === Tool Descriptions (for cards) ===

    "desc_merger": {
        "pt": "📁 Combine multiplos CSVs em um uÚnico arquivo",
        "en": "📁 Combine multiple CSVs into one file"
    },

    "tool_xlsx_profiles": {
        "pt": "📊 Excel Multi-Perfis",
        "en": "📊 Excel Multi-Profiles"
    },

    "desc_splitter": {
        "pt": "✂️ Divida arquivos grandes em partes menores",
        "en": "✂️ Split large files into smaller parts"
    },

    "desc_cleaner": {
        "pt": "🧹 Remova linhas vazias, duplicatas e mais",
        "en": "🧹 Remove empty lines, duplicates and more"
    },

    "desc_converter": {
        "pt": "🔄 Converta entre formatos de dados",
        "en": "🔄 Convert between data formats"
    },

    "desc_transformer": {
        "pt": "⚙️ Aplique transformacoes em dados",
        "en": "⚙️ Apply transformations to data"
    },

    "desc_xml_parser": {
        "pt": "📄 Converta XML para formato CSV",
        "en": "📄 Convert XML to CSV format"
    },

    "desc_excel_to_csv": {
        "pt": "📊 Converta planilhas Excel para CSV",
        "en": "📊 Convert Excel spreadsheets to CSV"
    },

    "desc_column_cleaner": {
        "pt": "🔧 Limpe e normalize colunas",
        "en": "🔧 Clean and normalize columns"
    },

    "desc_txt_parser": {
        "pt": "📝 Converta arquivos TXT para CSV",
        "en": "📝 Convert TXT files to CSV"
    },

    

    # === Profile Names (for list) ===

    "profile_merger": {

        "pt": "[Consolidar CSVs]",

        "en": "[Merge CSVs]"

    },

    "desc_xlsx_profiles": {
        "pt": "📊 Converta Excel usando perfis configurados",
        "en": "📊 Convert Excel using configured profiles"
    },

    "profile_splitter": {

        "pt": "[Dividir CSV]",

        "en": "[Split CSV]"

    },

    "profile_cleaner": {

        "pt": "[Limpar CSV]",

        "en": "[Clean CSV]"

    },

    "profile_converter": {

        "pt": "[Converter Formato]",

        "en": "[Convert Format]"

    },

    "profile_transformer": {

        "pt": "[Transformar Dados]",

        "en": "[Transform Data]"

    },

    "profile_xml_parser": {

        "pt": "[XML para CSV]",

        "en": "[XML to CSV]"

    },

    "profile_excel_to_csv": {

        "pt": "[Excel para CSV]",

        "en": "[Excel to CSV]"

    },

    "profile_column_cleaner": {

        "pt": "[Limpar Colunas]",

        "en": "[Clean Columns]"

    },

    "profile_txt_parser": {

        "pt": "[TXT para CSV]",

        "en": "[TXT to CSV]"

    },

    

    # === Common Buttons/Labels ===

    "execute": {

        "pt": "▶️ Executar",

        "en": "▶️ Execute"

    },

    "profile_xlsx_profiles": {

        "pt": "[Excel Multi-Perfis]",

        "en": "[Excel Multi-Profiles]"

    },

    "save_profile": {

        "pt": "💾 Salvar Perfil",

        "en": "💾 Save Profile"

    },

    "browse": {

        "pt": "Procurar...",

        "en": "Browse..."

    },

    "input_file": {

        "pt": "Arquivo de Entrada:",

        "en": "Input File:"

    },

    "output_file": {

        "pt": "Arquivo de Saida:",

        "en": "Output File:"

    },

    "output_folder": {

        "pt": "Pasta de Saida:",

        "en": "Output Folder:"

    },

    "separator": {

        "pt": "Separador:",

        "en": "Separator:"

    },

    "encoding": {

        "pt": "Encoding:",

        "en": "Encoding:"

    },

    "ready": {

        "pt": "Pronto para processar",

        "en": "Ready to process"

    },

    "processing": {

        "pt": "Processando...",

        "en": "Processing..."

    },

    "completed": {

        "pt": "Concluido!",

        "en": "Completed!"

    },

    "error": {

        "pt": "Erro",

        "en": "Error"

    },

    "success": {

        "pt": "Sucesso",

        "en": "Success"

    },

    "warning": {

        "pt": "Aviso",

        "en": "Warning"

    },

    "confirm": {

        "pt": "Confirmar",

        "en": "Confirm"

    },

    "cancel": {

        "pt": "Cancelar",

        "en": "Cancel"

    },

    "save": {

        "pt": "Salvar",

        "en": "Save"

    },

    "load": {

        "pt": "Carregar",

        "en": "Load"

    },

    "lines": {

        "pt": "linhas",

        "en": "rows"

    },

    "columns": {

        "pt": "colunas",

        "en": "columns"

    },

    "files": {

        "pt": "arquivos",

        "en": "files"

    },

    

    # === Settings ===

    "settings_title": {

        "pt": "⚙️ Configuraes",

        "en": "⚙️ Settings"

    },

    "theme": {

        "pt": "Tema:",

        "en": "Theme:"

    },

    "default_encoding": {

        "pt": "Encoding Padro:",

        "en": "Default Encoding:"

    },

    "default_separator": {

        "pt": "Separador Padro:",

        "en": "Default Separator:"

    },

    "language": {

        "pt": "Idioma:",

        "en": "Language:"

    },

    "settings_saved": {

        "pt": "Configuraes salvas!",

        "en": "Settings saved!"

    },

    

    # === Dialogs ===

    "profile_name_prompt": {

        "pt": "Nome do perfil:",

        "en": "Profile name:"

    },

    "create_profile_title": {

        "pt": "Criar Perfil",

        "en": "Create Profile"

    },

    "profile_exists": {

        "pt": "Ja existe um perfil com esse nome!",

        "en": "A profile with this name already exists!"

    },

    "profile_created": {

        "pt": "Perfil '{}' criado!",

        "en": "Profile '{}' created!"

    },

    "profile_saved": {

        "pt": "Perfil '{}' salvo!",

        "en": "Profile '{}' saved!"

    },

    "clear_history_confirm": {

        "pt": "Deseja limpar todo o histrico de processos?",

        "en": "Do you want to clear all process history?"

    },

    "history_cleared": {

        "pt": "Histrico limpo!",

        "en": "History cleared!"

    },

    "select_file": {

        "pt": "Selecione um arquivo primeiro!",

        "en": "Select a file first!"

    },

    "select_output": {

        "pt": "Selecione um arquivo de saida!",

        "en": "Select an output file!"

    },

    

    # === Tool-specific ===

    "origin_settings": {

        "pt": "Configuraes de Origem",

        "en": "Source Settings"

    },

    "dest_settings": {

        "pt": "Configuraes de Destino",

        "en": "Destination Settings"

    },

    "split_settings": {

        "pt": "Configuraes de Diviso",

        "en": "Split Settings"

    },

    "format_settings": {

        "pt": "Formato de Dados",

        "en": "Data Format"

    },

    "max_rows": {

        "pt": "Max. registros por arquivo:",

        "en": "Max rows per file:"

    },

    "presets": {

        "pt": "Presets:",

        "en": "Presets:"

    },

    "keep_original": {

        "pt": "Manter Original",

        "en": "Keep Original"

    },

    "quote_all": {

        "pt": "Colocar aspas em todos os campos",

        "en": "Quote all fields"

    },

    "keep_header": {

        "pt": "Incluir cabealho em cada arquivo",

        "en": "Include header in each file"

    },

    "prefix": {

        "pt": "Prefixo:",

        "en": "Prefix:"

    },

    "process_log": {

        "pt": "Log do Processo:",

        "en": "Process Log:"

    },

    "charset": {

        "pt": "Charset:",

        "en": "Charset:"

    },

    "format": {

        "pt": "Formato:",

        "en": "Format:"

    },

    

    # === CLI ===

    "cli_desc": {

        "pt": "CSVToolBox - Ferramentas para manipulao de CSV",

        "en": "CSVToolBox - Tools for CSV manipulation"

    },

    "cli_help_command": {

        "pt": "Comando a executar",

        "en": "Command to execute"

    },

    "cli_merge_help": {

        "pt": "Consolidar mºltiplos CSVs",

        "en": "Merge multiple CSVs"

    },

    "cli_split_help": {

        "pt": "Dividir CSV em partes",

        "en": "Split CSV into parts"

    },

    "cli_clean_help": {

        "pt": "Limpar dados do CSV",

        "en": "Clean CSV data"

    },

    "cli_convert_help": {

        "pt": "Converter entre formatos",

        "en": "Convert between formats"

    },

    "cli_transform_help": {

        "pt": "Aplicar DE-PARA",

        "en": "Apply lookup table"

    },

    "cli_info_help": {

        "pt": "Informaes do arquivo",

        "en": "File information"

    },

    "cli_profiles_help": {

        "pt": "Gerenciar perfis salvos",

        "en": "Manage saved profiles"

    },

    "cli_history_help": {

        "pt": "Gerenciar histrico",

        "en": "Manage history"

    },

    

    # === CLI Messages ===

    "cli_merging": {

        "pt": "📊 Consolidando {} arquivos...",

        "en": "📊 Merging {} files..."

    },

    "cli_reading": {

        "pt": "  → Lendo: {}",

        "en": "  → Reading: {}"

    },

    "cli_removed_duplicates": {

        "pt": "  → Removidas {} linhas duplicadas",

        "en": "  → Removed {} duplicate rows"

    },

    "cli_saved": {

        "pt": "✅ Salvo: {} ({} linhas)",

        "en": "✅ Saved: {} ({} rows)"

    },

    "cli_splitting": {

        "pt": "✂️ Dividindo: {}",

        "en": "✂️ Splitting: {}"

    },

    "cli_split_info": {

        "pt": "  → {} linhas / {} por arquivo = {} arquivos",

        "en": "  → {} rows / {} per file = {} files"

    },

    "cli_files_created": {

        "pt": "✅ {} arquivos criados em: {}",

        "en": "✅ {} files created in: {}"

    },

    "cli_cleaning": {

        "pt": "🧹 Limpando: {}",

        "en": "🧹 Cleaning: {}"

    },

    "cli_removed_empty": {

        "pt": "  → Removidas {} linhas vazias",

        "en": "  → Removed {} empty rows"

    },

    "cli_converting": {

        "pt": "🔄 Convertendo: {}",

        "en": "🔄 Converting: {}"

    },

    "cli_format_not_supported": {

        "pt": "❌ Formato no suportado: {}",

        "en": "❌ Unsupported format: {}"

    },

    "cli_output_format_not_supported": {

        "pt": "❌ Formato de saida no suportado: {}",

        "en": "❌ Output format not supported: {}"

    },

    "cli_transforming": {

        "pt": "⚙️ Transformando: {}",

        "en": "⚙️ Transforming: {}"

    },

    "cli_depara_need_cols": {

        "pt": "❌ Tabela DE-PARA precisa ter pelo menos 2 colunas",

        "en": "❌ Lookup table needs at least 2 columns"

    },

    "cli_column_not_found": {

        "pt": "❌ Coluna '{}' no encontrada",

        "en": "❌ Column '{}' not found"

    },

    "cli_available_columns": {

        "pt": "   Colunas disponiveis: {}",

        "en": "   Available columns: {}"

    },

    "cli_values_replaced": {

        "pt": "  → {} valores substituidos",

        "en": "  → {} values replaced"

    },

    "cli_analyzing": {

        "pt": "📋 Analisando: {}",

        "en": "📋 Analyzing: {}"

    },

    "cli_encoding_detected": {

        "pt": "  Encoding detectado: {}",

        "en": "  Detected encoding: {}"

    },

    "cli_rows": {

        "pt": "  Linhas: {}",

        "en": "  Rows: {}"

    },

    "cli_columns": {

        "pt": "  Colunas: {}",

        "en": "  Columns: {}"

    },

    "cli_sample": {

        "pt": "  Amostra ({} linhas):",

        "en": "  Sample ({} rows):"

    },

    "cli_no_profiles": {

        "pt": "📋 Nenhum perfil salvo",

        "en": "📋 Não saved profiles"

    },

    "cli_use_gui_profiles": {

        "pt": "   Use a interface grafica para criar perfis",

        "en": "   Use the GUI to create profiles"

    },

    "cli_saved_profiles": {

        "pt": "📋 Perfis salvos:",

        "en": "📋 Saved profiles:"

    },

    "cli_tool": {

        "pt": "    Ferramenta: {}",

        "en": "    Tool: {}"

    },

    "cli_updated": {

        "pt": "    Atualizado: {}",

        "en": "    Updated: {}"

    },

    "cli_specify_profile": {

        "pt": "❌ Especifique o nome do perfil: --name <nome>",

        "en": "❌ Specify profile name: --name <name>"

    },

    "cli_profile_not_found": {

        "pt": "❌ Perfil '{}' no encontrado",

        "en": "❌ Profile '{}' not found"

    },

    "cli_profile": {

        "pt": "📋 Perfil: {}",

        "en": "📋 Profile: {}"

    },

    "cli_created": {

        "pt": "  Criado: {}",

        "en": "  Created: {}"

    },

    "cli_settings": {

        "pt": "  Configuraes:",

        "en": "  Settings:"

    },

    "cli_no_history": {

        "pt": "🕐 Nenhum processo não histrico",

        "en": "🕐 Não processes in history"

    },

    "cli_process_history": {

        "pt": "🕐 Histrico de processos:",

        "en": "🕐 Process history:"

    },

    "cli_file": {

        "pt": "      Arquivo: {}",

        "en": "      File: {}"

    },

    "cli_specify_index": {

        "pt": "❌ Especifique o iíndice: --index <nºmero>",

        "en": "❌ Specify index: --index <number>"

    },

    "cli_invalid_index": {

        "pt": "❌ Índice invalido. Use 1 a {}",

        "en": "❌ Invalid index. Use 1 to {}"

    },

    "cli_process": {

        "pt": "🕐 Processo #{}",

        "en": "🕐 Process #{}"

    },

    "cli_datetime": {

        "pt": "  Data/Hora: {}",

        "en": "  Date/Time: {}"

    },

    "cli_input": {

        "pt": "  Entrada: {}",

        "en": "  Input: {}"

    },

    "cli_output": {

        "pt": "  Saida: {}",

        "en": "  Output: {}"

    },

    "cli_history_cleared": {

        "pt": "✅ Histrico limpo!",

        "en": "✅ History cleared!"

    },

    "cli_history_empty": {

        "pt": "📋 Histrico ja esta vazio",

        "en": "📋 History is already empty"

    },

    "cli_file_not_found": {

        "pt": "❌ Arquivo no encontrado: {}",

        "en": "❌ File not found: {}"

    },

    "cli_error": {

        "pt": "❌ Erro: {}",

        "en": "❌ Error: {}"

    },

    "cli_help_tip": {

        "pt": "💪 Use 'python cli.py <comando> --help' para ver opes de cada comando",

        "en": "💪 Use 'python cli.py <command> --help' for command options"

    },

    

    # === CLI Parser Help ===

    "cli_arg_files": {

        "pt": "Arquivos CSV para consolidar",

        "en": "CSV files to merge"

    },

    "cli_arg_output": {

        "pt": "Arquivo de saida",

        "en": "Output file"

    },

    "cli_arg_separator": {

        "pt": "Separador (semicolon, comma, tab, pipe)",

        "en": "Separator (semicolon, comma, tab, pipe)"

    },

    "cli_arg_encoding": {

        "pt": "Encoding (auto, utf-8, latin-1)",

        "en": "Encoding (auto, utf-8, latin-1)"

    },

    "cli_arg_drop_duplicates": {

        "pt": "Remover duplicatas",

        "en": "Remove duplicates"

    },

    "cli_arg_file_split": {

        "pt": "Arquivo CSV para dividir",

        "en": "CSV file to split"

    },

    "cli_arg_rows": {

        "pt": "Linhas por arquivo (default: 50000)",

        "en": "Rows per file (default: 50000)"

    },

    "cli_arg_output_dir": {

        "pt": "Diretrio de saida",

        "en": "Output directory"

    },

    "cli_arg_file_clean": {

        "pt": "Arquivo CSV para limpar",

        "en": "CSV file to clean"

    },

    "cli_arg_trim": {

        "pt": "Remover espaos",

        "en": "Remove whitespace"

    },

    "cli_arg_remove_quotes": {

        "pt": "Remover aspas",

        "en": "Remove quotes"

    },

    "cli_arg_uppercase": {

        "pt": "Converter para maiºsculas",

        "en": "Convert to uppercase"

    },

    "cli_arg_drop_empty": {

        "pt": "Remover linhas vazias",

        "en": "Remove empty rows"

    },

    "cli_arg_file_input": {

        "pt": "Arquivo de entrada",

        "en": "Input file"

    },

    "cli_arg_output_separator": {

        "pt": "Separador do CSV de saida",

        "en": "Output CSV separator"

    },

    "cli_arg_sheet": {

        "pt": "Nome da sheet (para Excel)",

        "en": "Sheet name (for Excel)"

    },

    "cli_arg_column": {

        "pt": "Coluna para transformar",

        "en": "Column to transform"

    },

    "cli_arg_depara": {

        "pt": "Arquivo CSV com tabela DE-PARA",

        "en": "CSV file with lookup table"

    },

    "cli_arg_sample": {

        "pt": "Mostrar N linhas de amostra",

        "en": "Show N sample rows"

    },

    "cli_arg_action_profiles": {

        "pt": "Ao: list (padro) ou show",

        "en": "Action: list (default) or show"

    },

    "cli_arg_profile_name": {

        "pt": "Nome do perfil (para show)",

        "en": "Profile name (for show)"

    },

    "cli_arg_action_history": {

        "pt": "Ao: list (padro), show ou clear",

        "en": "Action: list (default), show or clear"

    },

    "cli_arg_history_index": {

        "pt": "Índice do item (para show)",

        "en": "Item index (for show)"

    },

    
    # === Data Verticalizer Tool ===
    "tool_verticalizer": {
        "pt": "📊 Verticalizar Dados",
        "en": "📊 Verticalize Data"
    },
    "desc_verticalizer": {
        "pt": "📊 Verticalize (unpivot) e higienize dados",
        "en": "📊 Verticalize (unpivot) and sanitize data"
    },
    "profile_verticalizer": {
        "pt": "[Verticalizar Dados]",
        "en": "[Verticalize Data]"
    },
    "verticalization_tab": {
        "pt": "📊 Verticalização",
        "en": "📊 Verticalization"
    },
    "sanitization_tab": {
        "pt": "🧹 Higienização",
        "en": "🧹 Sanitization"
    },
    "fixed_columns": {
        "pt": "Colunas Fixas (ID):",
        "en": "Fixed Columns (ID):"
    },
    "fixed_columns_hint": {
        "pt": "Ex: CODIGO,DESCRICAO",
        "en": "Ex: CODE,DESCRIPTION"
    },
    "vertical_columns": {
        "pt": "Colunas a Verticalizar:",
        "en": "Columns to Verticalize:"
    },
    "vertical_columns_hint": {
        "pt": "Ex: JAN,FEV,MAR (vazio = detectar por padrão)",
        "en": "Ex: JAN,FEB,MAR (empty = detect by pattern)"
    },
    "period_pattern": {
        "pt": "Padrão de Período (Regex):",
        "en": "Period Pattern (Regex):"
    },
    "period_pattern_hint": {
        "pt": "Ex: ^\\d{4}-\\d{2}$ ou ^(JAN|FEV|MAR)",
        "en": "Ex: ^\\d{4}-\\d{2}$ or ^(JAN|FEB|MAR)"
    },
    "variable_column_name": {
        "pt": "Nome Coluna Variável:",
        "en": "Variable Column Name:"
    },
    "value_column_name": {
        "pt": "Nome Coluna Valor:",
        "en": "Value Column Name:"
    },
    "detect_columns": {
        "pt": "🔍 Detectar Colunas",
        "en": "🔍 Detect Columns"
    },
    "columns_detected": {
        "pt": "colunas detectadas",
        "en": "columns detected"
    },
    "no_columns_detected": {
        "pt": "Nenhuma coluna detectada com o padrão informado",
        "en": "No columns detected with the provided pattern"
    },
    
    # === Sanitization Options ===
    "trim_spaces": {
        "pt": "Remover espaços extras",
        "en": "Trim extra spaces"
    },
    "remove_accents": {
        "pt": "Remover acentos",
        "en": "Remove accents"
    },
    "case_conversion": {
        "pt": "Conversão de caso:",
        "en": "Case conversion:"
    },
    "case_none": {
        "pt": "Nenhuma",
        "en": "None"
    },
    "case_upper": {
        "pt": "MAIÚSCULAS",
        "en": "UPPERCASE"
    },
    "case_lower": {
        "pt": "minúsculas",
        "en": "lowercase"
    },
    "case_title": {
        "pt": "Título",
        "en": "Title"
    },
    "remove_duplicates": {
        "pt": "Remover linhas duplicadas",
        "en": "Remove duplicate rows"
    },
    "remove_empty_rows": {
        "pt": "Remover linhas vazias",
        "en": "Remove empty rows"
    },
    "custom_replacements": {
        "pt": "Substituições personalizadas:",
        "en": "Custom replacements:"
    },
    "custom_replacements_hint": {
        "pt": "Formato: valor_original→valor_novo (um por linha)",
        "en": "Format: original_value→new_value (one per line)"
    },
    "apply_to_columns": {
        "pt": "Aplicar apenas às colunas:",
        "en": "Apply only to columns:"
    },
    "apply_to_columns_hint": {
        "pt": "Vazio = todas as colunas",
        "en": "Empty = all columns"
    },
    "preview_verticalization": {
        "pt": "📊 Prévia Verticalização",
        "en": "📊 Preview Verticalization"
    },
    "preview_sanitization": {
        "pt": "🧹 Prévia Higienização",
        "en": "🧹 Preview Sanitization"
    },
    
    # === Workflow Orchestrator Tool ===
    "tool_workflow": {
        "pt": "🔀 Orquestrador de Workflows",
        "en": "🔀 Workflow Orchestrator"
    },
    "desc_workflow": {
        "pt": "🔀 Crie e execute sequências de processos",
        "en": "🔀 Create and run process sequences"
    },
    "profile_workflow": {
        "pt": "[Orquestrador]",
        "en": "[Orchestrator]"
    },
    "workflow_management": {
        "pt": "Gerenciamento de Workflows",
        "en": "Workflow Management"
    },
    "new_workflow": {
        "pt": "Novo Workflow",
        "en": "New Workflow"
    },
    "load_workflow": {
        "pt": "Carregar Workflow",
        "en": "Load Workflow"
    },
    "save_workflow": {
        "pt": "Salvar Workflow",
        "en": "Save Workflow"
    },
    "workflow_name": {
        "pt": "Nome do Workflow",
        "en": "Workflow Name"
    },
    "workflow_name_hint": {
        "pt": "Digite um nome para o workflow...",
        "en": "Enter a workflow name..."
    },
    "add_step": {
        "pt": "Adicionar Etapa",
        "en": "Add Step"
    },
    "select_tool": {
        "pt": "Selecionar Ferramenta",
        "en": "Select Tool"
    },
    "input_file": {
        "pt": "Arquivo de Entrada",
        "en": "Input File"
    },
    "input_placeholder": {
        "pt": "Caminho do arquivo de entrada...",
        "en": "Input file path..."
    },
    "output_placeholder": {
        "pt": "Caminho do arquivo de saída...",
        "en": "Output file path..."
    },
    "use_previous_output": {
        "pt": "Usar saída da etapa anterior como entrada",
        "en": "Use previous step output as input"
    },
    "step_config": {
        "pt": "Configurações da Etapa (JSON)",
        "en": "Step Configuration (JSON)"
    },
    "add_to_queue": {
        "pt": "Adicionar à Fila",
        "en": "Add to Queue"
    },
    "execution_queue": {
        "pt": "Fila de Execução",
        "en": "Execution Queue"
    },
    "queue_empty": {
        "pt": "Nenhuma etapa na fila.\nAdicione etapas para criar seu workflow.",
        "en": "No steps in queue.\nAdd steps to create your workflow."
    },
    "run_all": {
        "pt": "Executar Tudo",
        "en": "Run All"
    },
    "run_selected": {
        "pt": "Executar Selecionado",
        "en": "Run Selected"
    },
    "stop": {
        "pt": "Parar",
        "en": "Stop"
    },
    "execution_log": {
        "pt": "Log de Execução",
        "en": "Execution Log"
    },
    "ready": {
        "pt": "Pronto",
        "en": "Ready"
    },
    "running": {
        "pt": "Executando",
        "en": "Running"
    },
    "completed": {
        "pt": "Concluído",
        "en": "Completed"
    },
    "finished_with_errors": {
        "pt": "Concluído com erros",
        "en": "Finished with errors"
    },
    "step_added": {
        "pt": "Etapa adicionada",
        "en": "Step added"
    },
    "step_removed": {
        "pt": "Etapa removida",
        "en": "Step removed"
    },
    "step_completed": {
        "pt": "Etapa concluída",
        "en": "Step completed"
    },
    "step_failed": {
        "pt": "Etapa falhou",
        "en": "Step failed"
    },
    "executing_step": {
        "pt": "Executando etapa",
        "en": "Executing step"
    },
    "execution_stopped": {
        "pt": "Execução interrompida",
        "en": "Execution stopped"
    },
    "stopping_execution": {
        "pt": "Parando execução",
        "en": "Stopping execution"
    },
    "queue_cleared": {
        "pt": "Fila limpa",
        "en": "Queue cleared"
    },
    "clear_queue_confirm": {
        "pt": "Tem certeza que deseja limpar a fila?",
        "en": "Are you sure you want to clear the queue?"
    },
    "new_workflow_confirm": {
        "pt": "Criar novo workflow? O workflow atual será perdido.",
        "en": "Create new workflow? Current workflow will be lost."
    },
    "new_workflow_created": {
        "pt": "Novo workflow criado",
        "en": "New workflow created"
    },
    "workflow_saved": {
        "pt": "Workflow salvo",
        "en": "Workflow saved"
    },
    "workflow_loaded": {
        "pt": "Workflow carregado",
        "en": "Workflow loaded"
    },
    "enter_workflow_name": {
        "pt": "Digite um nome para o workflow",
        "en": "Enter a workflow name"
    },
    "add_steps_first": {
        "pt": "Adicione etapas primeiro",
        "en": "Add steps first"
    },
    "invalid_json": {
        "pt": "JSON inválido",
        "en": "Invalid JSON"
    },
    "select_tool_first": {
        "pt": "Selecione uma ferramenta",
        "en": "Select a tool"
    },
    "select_input_file": {
        "pt": "Selecionar arquivo de entrada",
        "en": "Select input file"
    },
    "select_output_file": {
        "pt": "Selecionar arquivo de saída",
        "en": "Select output file"
    },
    "previous_output": {
        "pt": "(saída anterior)",
        "en": "(previous output)"
    },
    "no_pending_steps": {
        "pt": "Nenhuma etapa pendente",
        "en": "No pending steps"
    },
    "preview_rows": {
        "pt": "linhas de prévia",
        "en": "preview rows"
    },
    
    # === Workflow Integration (Botões em cada módulo) ===
    "add_to_workflow": {
        "pt": "Adicionar ao Workflow",
        "en": "Add to Workflow"
    },
    "step_added_to_workflow": {
        "pt": "Etapa adicionada ao workflow!",
        "en": "Step added to workflow!"
    },
    "total_steps": {
        "pt": "Total de etapas",
        "en": "Total steps"
    },
    "select_input_first": {
        "pt": "Selecione um arquivo de entrada primeiro",
        "en": "Select an input file first"
    },
    "select_output_first": {
        "pt": "Selecione um arquivo de saída primeiro",
        "en": "Select an output file first"
    },
    "select_files_first": {
        "pt": "Selecione arquivos primeiro",
        "en": "Select files first"
    },
    "use_previous_output_question": {
        "pt": "Usar a saída da etapa anterior como entrada desta etapa?",
        "en": "Use previous step output as input for this step?"
    },
    "workflow": {
        "pt": "Workflow",
        "en": "Workflow"
    },
    "steps": {
        "pt": "etapas",
        "en": "steps"
    },
    "workflow_instructions": {
        "pt": "Configure cada ferramenta normalmente e clique em 'Adicionar ao Workflow' para criar sua sequência de processos.",
        "en": "Configure each tool normally and click 'Add to Workflow' to create your process sequence."
    },
    "queue_empty_instruction": {
        "pt": "Nenhuma etapa na fila.\nVá até uma ferramenta, configure-a e clique em 'Adicionar ao Workflow'.",
        "en": "No steps in queue.\nGo to a tool, configure it and click 'Add to Workflow'."
    },
    "execution_controls": {
        "pt": "Controles de Execução",
        "en": "Execution Controls"
    },
    "clear_queue": {
        "pt": "Limpar Fila",
        "en": "Clear Queue"
    },
    "input": {
        "pt": "Entrada",
        "en": "Input"
    },
    "output": {
        "pt": "Saída",
        "en": "Output"
    },
    "rows": {
        "pt": "linhas",
        "en": "rows"
    },
    "no_input_file": {
        "pt": "Arquivo de entrada não especificado",
        "en": "No input file specified"
    },

}

