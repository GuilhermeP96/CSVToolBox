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
        "pt": "💡 Dica: Salve perfis para reutilizar configurações em processos recorrentes",
        "en": "💡 Tip: Save profiles to reuse settings in recurring processes"
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
        "pt": "⚙️ Configurações",
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
        "pt": "📊 Consolidar CSVs",
        "en": "📊 Merge CSVs"
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
        "pt": "📑 Excel para CSV",
        "en": "📑 Excel to CSV"
    },
    "tool_column_cleaner": {
        "pt": "🔤 Limpar Colunas",
        "en": "🔤 Clean Columns"
    },
    "tool_txt_parser": {
        "pt": "📝 TXT para CSV",
        "en": "📝 TXT to CSV"
    },
    
    # === Tool Descriptions (for cards) ===
    "desc_merger": {
        "pt": "Mescle múltiplos arquivos CSV em um único arquivo",
        "en": "Merge multiple CSV files into a single file"
    },
    "desc_splitter": {
        "pt": "Divida arquivos grandes em partes menores",
        "en": "Split large files into smaller parts"
    },
    "desc_cleaner": {
        "pt": "Remova caracteres especiais, aspas e limpe dados",
        "en": "Remove special characters, quotes and clean data"
    },
    "desc_converter": {
        "pt": "Converta entre CSV, XLSX, XML e outros formatos",
        "en": "Convert between CSV, XLSX, XML and other formats"
    },
    "desc_transformer": {
        "pt": "Substitua valores, filtre colunas e transforme dados",
        "en": "Replace values, filter columns and transform data"
    },
    "desc_xml_parser": {
        "pt": "Converta arquivos XML para CSV com parsing inteligente",
        "en": "Convert XML files to CSV with smart parsing"
    },
    "desc_excel_to_csv": {
        "pt": "Converta planilhas Excel com normalização de headers",
        "en": "Convert Excel spreadsheets with header normalization"
    },
    "desc_column_cleaner": {
        "pt": "Remova acentos e normalize texto de colunas",
        "en": "Remove accents and normalize column text"
    },
    "desc_txt_parser": {
        "pt": "Converta arquivos TXT delimitados ou largura fixa",
        "en": "Convert delimited or fixed-width TXT files"
    },
    
    # === Profile Names (for list) ===
    "profile_merger": {
        "pt": "[Consolidar CSVs]",
        "en": "[Merge CSVs]"
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
        "pt": "Arquivo de Saída:",
        "en": "Output File:"
    },
    "output_folder": {
        "pt": "Pasta de Saída:",
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
        "pt": "Concluído!",
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
        "pt": "⚙️ Configurações",
        "en": "⚙️ Settings"
    },
    "theme": {
        "pt": "Tema:",
        "en": "Theme:"
    },
    "default_encoding": {
        "pt": "Encoding Padrão:",
        "en": "Default Encoding:"
    },
    "default_separator": {
        "pt": "Separador Padrão:",
        "en": "Default Separator:"
    },
    "language": {
        "pt": "Idioma:",
        "en": "Language:"
    },
    "settings_saved": {
        "pt": "Configurações salvas!",
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
        "pt": "Já existe um perfil com esse nome!",
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
        "pt": "Deseja limpar todo o histórico de processos?",
        "en": "Do you want to clear all process history?"
    },
    "history_cleared": {
        "pt": "Histórico limpo!",
        "en": "History cleared!"
    },
    "select_file": {
        "pt": "Selecione um arquivo primeiro!",
        "en": "Select a file first!"
    },
    "select_output": {
        "pt": "Selecione um arquivo de saída!",
        "en": "Select an output file!"
    },
    
    # === Tool-specific ===
    "origin_settings": {
        "pt": "Configurações de Origem",
        "en": "Source Settings"
    },
    "dest_settings": {
        "pt": "Configurações de Destino",
        "en": "Destination Settings"
    },
    "split_settings": {
        "pt": "Configurações de Divisão",
        "en": "Split Settings"
    },
    "format_settings": {
        "pt": "Formato de Dados",
        "en": "Data Format"
    },
    "max_rows": {
        "pt": "Máx. registros por arquivo:",
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
        "pt": "Incluir cabeçalho em cada arquivo",
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
        "pt": "CSVToolBox - Ferramentas para manipulação de CSV",
        "en": "CSVToolBox - Tools for CSV manipulation"
    },
    "cli_help_command": {
        "pt": "Comando a executar",
        "en": "Command to execute"
    },
    "cli_merge_help": {
        "pt": "Consolidar múltiplos CSVs",
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
        "pt": "Informações do arquivo",
        "en": "File information"
    },
    "cli_profiles_help": {
        "pt": "Gerenciar perfis salvos",
        "en": "Manage saved profiles"
    },
    "cli_history_help": {
        "pt": "Gerenciar histórico",
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
        "pt": "❌ Formato não suportado: {}",
        "en": "❌ Unsupported format: {}"
    },
    "cli_output_format_not_supported": {
        "pt": "❌ Formato de saída não suportado: {}",
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
        "pt": "❌ Coluna '{}' não encontrada",
        "en": "❌ Column '{}' not found"
    },
    "cli_available_columns": {
        "pt": "   Colunas disponíveis: {}",
        "en": "   Available columns: {}"
    },
    "cli_values_replaced": {
        "pt": "  → {} valores substituídos",
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
        "en": "📋 No saved profiles"
    },
    "cli_use_gui_profiles": {
        "pt": "   Use a interface gráfica para criar perfis",
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
        "pt": "❌ Perfil '{}' não encontrado",
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
        "pt": "  Configurações:",
        "en": "  Settings:"
    },
    "cli_no_history": {
        "pt": "🕐 Nenhum processo no histórico",
        "en": "🕐 No processes in history"
    },
    "cli_process_history": {
        "pt": "🕐 Histórico de processos:",
        "en": "🕐 Process history:"
    },
    "cli_file": {
        "pt": "      Arquivo: {}",
        "en": "      File: {}"
    },
    "cli_specify_index": {
        "pt": "❌ Especifique o índice: --index <número>",
        "en": "❌ Specify index: --index <number>"
    },
    "cli_invalid_index": {
        "pt": "❌ Índice inválido. Use 1 a {}",
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
        "pt": "  Saída: {}",
        "en": "  Output: {}"
    },
    "cli_history_cleared": {
        "pt": "✅ Histórico limpo!",
        "en": "✅ History cleared!"
    },
    "cli_history_empty": {
        "pt": "📋 Histórico já está vazio",
        "en": "📋 History is already empty"
    },
    "cli_file_not_found": {
        "pt": "❌ Arquivo não encontrado: {}",
        "en": "❌ File not found: {}"
    },
    "cli_error": {
        "pt": "❌ Erro: {}",
        "en": "❌ Error: {}"
    },
    "cli_help_tip": {
        "pt": "💡 Use 'python cli.py <comando> --help' para ver opções de cada comando",
        "en": "💡 Use 'python cli.py <command> --help' for command options"
    },
    
    # === CLI Parser Help ===
    "cli_arg_files": {
        "pt": "Arquivos CSV para consolidar",
        "en": "CSV files to merge"
    },
    "cli_arg_output": {
        "pt": "Arquivo de saída",
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
        "pt": "Diretório de saída",
        "en": "Output directory"
    },
    "cli_arg_file_clean": {
        "pt": "Arquivo CSV para limpar",
        "en": "CSV file to clean"
    },
    "cli_arg_trim": {
        "pt": "Remover espaços",
        "en": "Remove whitespace"
    },
    "cli_arg_remove_quotes": {
        "pt": "Remover aspas",
        "en": "Remove quotes"
    },
    "cli_arg_uppercase": {
        "pt": "Converter para maiúsculas",
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
        "pt": "Separador do CSV de saída",
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
        "pt": "Ação: list (padrão) ou show",
        "en": "Action: list (default) or show"
    },
    "cli_arg_profile_name": {
        "pt": "Nome do perfil (para show)",
        "en": "Profile name (for show)"
    },
    "cli_arg_action_history": {
        "pt": "Ação: list (padrão), show ou clear",
        "en": "Action: list (default), show or clear"
    },
    "cli_arg_history_index": {
        "pt": "Índice do item (para show)",
        "en": "Item index (for show)"
    },
}
