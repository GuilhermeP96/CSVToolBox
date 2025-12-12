#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSVToolBox CLI - Command Line Interface / Interface de linha de comando
Usage / Uso: python cli.py <command> [options]
"""

import argparse
import sys
import os
import pandas as pd
import chardet
import json
from pathlib import Path
from datetime import datetime

# Internationalization
from i18n import t, get_language, set_language


def detect_encoding(filepath):
    """Detecta encoding de um arquivo"""
    with open(filepath, 'rb') as f:
        result = chardet.detect(f.read(10000))
        return result['encoding'] or 'utf-8'


def get_separator(sep_name):
    """Converte nome do separador para caractere"""
    separators = {
        'semicolon': ';',
        'comma': ',',
        'tab': '\t',
        'pipe': '|',
        ';': ';',
        ',': ',',
        '|': '|'
    }
    return separators.get(sep_name, sep_name)


def get_user_data_dir():
    """Retorna o diretório de dados do usuário"""
    documents = Path(os.path.expanduser("~")) / "OneDrive - Claro SA" / "Documentos"
    if not documents.exists():
        documents = Path(os.path.expanduser("~")) / "Documents"
    
    data_dir = documents / "CSVToolBox"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def load_config():
    """Carrega configurações (perfis)"""
    config_path = get_user_data_dir() / "config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"profiles": {}, "settings": {}}


def load_history():
    """Carrega histórico de processos"""
    history_path = get_user_data_dir() / "history.json"
    if history_path.exists():
        with open(history_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


# ============================================================
# MERGE - Merge multiple CSVs / Consolidar múltiplos CSVs
# ============================================================
def cmd_merge(args):
    """Merge multiple CSV files into one / Consolida múltiplos arquivos CSV em um único"""
    print(t("cli_merging").format(len(args.files)))
    
    sep = get_separator(args.separator)
    enc = args.encoding
    
    dfs = []
    for filepath in args.files:
        if enc == 'auto':
            file_enc = detect_encoding(filepath)
        else:
            file_enc = enc
        
        print(t("cli_reading").format(filepath))
        df = pd.read_csv(filepath, sep=sep, encoding=file_enc, low_memory=False)
        dfs.append(df)
    
    result = pd.concat(dfs, ignore_index=True)
    
    if args.drop_duplicates:
        before = len(result)
        result = result.drop_duplicates()
        print(t("cli_removed_duplicates").format(before - len(result)))
    
    result.to_csv(args.output, sep=sep, index=False, encoding='utf-8')
    print(t("cli_saved").format(args.output, len(result)))


# ============================================================
# SPLIT - Split large CSV / Dividir CSV grande
# ============================================================
def cmd_split(args):
    """Split a large CSV into smaller parts / Divide um CSV grande em partes menores"""
    print(t("cli_splitting").format(args.file))
    
    sep = get_separator(args.separator)
    enc = args.encoding if args.encoding != 'auto' else detect_encoding(args.file)
    
    df = pd.read_csv(args.file, sep=sep, encoding=enc, low_memory=False)
    total_rows = len(df)
    
    num_files = (total_rows // args.rows) + (1 if total_rows % args.rows else 0)
    print(t("cli_split_info").format(total_rows, args.rows, num_files))
    
    base_name = Path(args.file).stem
    output_dir = Path(args.output_dir or Path(args.file).parent)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(num_files):
        start = i * args.rows
        end = min((i + 1) * args.rows, total_rows)
        chunk = df.iloc[start:end]
        
        output_file = output_dir / f"{base_name}_part{i+1:03d}.csv"
        chunk.to_csv(output_file, sep=sep, index=False, encoding='utf-8')
        print(f"  → {output_file.name}: {len(chunk)} {t('lines')}")
    
    print(t("cli_files_created").format(num_files, output_dir))


# ============================================================
# CLEAN - Clean CSV data / Limpar dados do CSV
# ============================================================
def cmd_clean(args):
    """Clean CSV data / Limpa dados de um CSV"""
    print(t("cli_cleaning").format(args.file))
    
    sep = get_separator(args.separator)
    enc = args.encoding if args.encoding != 'auto' else detect_encoding(args.file)
    
    df = pd.read_csv(args.file, sep=sep, encoding=enc, low_memory=False, dtype=str)
    
    for col in df.columns:
        if args.trim:
            df[col] = df[col].str.strip()
        if args.remove_quotes:
            df[col] = df[col].str.replace('"', '').str.replace("'", '')
        if args.uppercase:
            df[col] = df[col].str.upper()
    
    if args.drop_empty:
        before = len(df)
        df = df.dropna(how='all')
        print(t("cli_removed_empty").format(before - len(df)))
    
    output = args.output or args.file.replace('.csv', '_clean.csv')
    df.to_csv(output, sep=sep, index=False, encoding='utf-8')
    print(t("cli_saved").format(output, len(df)))


# ============================================================
# CONVERT - Convert between formats / Converter entre formatos
# ============================================================
def cmd_convert(args):
    """Convert between formats (CSV, XLSX, JSON) / Converte entre formatos"""
    print(t("cli_converting").format(args.file))
    
    input_ext = Path(args.file).suffix.lower()
    output_ext = Path(args.output).suffix.lower()
    
    # Read input file
    if input_ext == '.csv':
        sep = get_separator(args.separator)
        enc = args.encoding if args.encoding != 'auto' else detect_encoding(args.file)
        df = pd.read_csv(args.file, sep=sep, encoding=enc, low_memory=False)
    elif input_ext in ['.xlsx', '.xls']:
        df = pd.read_excel(args.file, sheet_name=args.sheet or 0)
    elif input_ext == '.json':
        df = pd.read_json(args.file)
    else:
        print(t("cli_format_not_supported").format(input_ext))
        return
    
    # Save output file
    if output_ext == '.csv':
        sep = get_separator(args.output_separator or 'semicolon')
        df.to_csv(args.output, sep=sep, index=False, encoding='utf-8')
    elif output_ext == '.xlsx':
        df.to_excel(args.output, index=False, engine='openpyxl')
    elif output_ext == '.json':
        df.to_json(args.output, orient='records', force_ascii=False, indent=2)
    else:
        print(t("cli_output_format_not_supported").format(output_ext))
        return
    
    print(t("cli_saved").format(args.output, len(df)))


# ============================================================
# TRANSFORM - Apply lookup table / Aplicar DE-PARA
# ============================================================
def cmd_transform(args):
    """Apply lookup table to a column / Aplica tabela DE-PARA em uma coluna"""
    print(t("cli_transforming").format(args.file))
    
    sep = get_separator(args.separator)
    enc = args.encoding if args.encoding != 'auto' else detect_encoding(args.file)
    
    df = pd.read_csv(args.file, sep=sep, encoding=enc, low_memory=False)
    
    # Load lookup table
    depara_enc = detect_encoding(args.depara)
    depara = pd.read_csv(args.depara, sep=sep, encoding=depara_enc)
    
    if len(depara.columns) < 2:
        print(t("cli_depara_need_cols"))
        return
    
    col_de = depara.columns[0]
    col_para = depara.columns[1]
    mapping = dict(zip(depara[col_de], depara[col_para]))
    
    if args.column not in df.columns:
        print(t("cli_column_not_found").format(args.column))
        print(t("cli_available_columns").format(list(df.columns)))
        return
    
    before = df[args.column].copy()
    df[args.column] = df[args.column].map(mapping).fillna(df[args.column])
    changed = (before != df[args.column]).sum()
    
    print(t("cli_values_replaced").format(changed))
    
    output = args.output or args.file.replace('.csv', '_transformed.csv')
    df.to_csv(output, sep=sep, index=False, encoding='utf-8')
    print(f"✅ {t('save')}: {output}")


# ============================================================
# INFO - Show CSV information / Mostrar informações do CSV
# ============================================================
def cmd_info(args):
    """Show CSV file information / Mostra informações sobre um arquivo CSV"""
    print(t("cli_analyzing").format(args.file))
    
    sep = get_separator(args.separator)
    enc = args.encoding if args.encoding != 'auto' else detect_encoding(args.file)
    
    print(f"\n  {t('cli_encoding_detected').format(enc).strip()}")
    
    df = pd.read_csv(args.file, sep=sep, encoding=enc, low_memory=False)
    
    print(t("cli_rows").format(len(df)))
    print(t("cli_columns").format(len(df.columns)))
    print(f"\n  {t('columns')}:")
    for i, col in enumerate(df.columns, 1):
        dtype = df[col].dtype
        nulls = df[col].isna().sum()
        null_text = "nulls" if get_language() == "en" else "nulos"
        print(f"    {i:2}. {col} ({dtype}) - {nulls} {null_text}")
    
    if args.sample:
        print(f"\n  {t('cli_sample').format(args.sample).strip()}")
        print(df.head(args.sample).to_string())


# ============================================================
# PROFILES - Manage saved profiles / Gerenciar perfis salvos
# ============================================================
def cmd_profiles(args):
    """List or show saved profiles / Lista ou mostra perfis salvos"""
    config = load_config()
    profiles = config.get("profiles", {})
    
    if args.action == "list" or args.action is None:
        if not profiles:
            print(t("cli_no_profiles"))
            print(t("cli_use_gui_profiles"))
            return
        
        print(f"{t('cli_saved_profiles')}\n")
        for name, data in profiles.items():
            tool = data.get("tool", "?")
            updated = data.get("updated_at", "?")[:10]
            print(f"  • {name}")
            print(t("cli_tool").format(tool))
            print(f"{t('cli_updated').format(updated)}\n")
    
    elif args.action == "show":
        if not args.name:
            print(t("cli_specify_profile"))
            return
        
        if args.name not in profiles:
            print(t("cli_profile_not_found").format(args.name))
            return
        
        profile = profiles[args.name]
        print(f"{t('cli_profile').format(args.name)}\n")
        print(t("cli_tool").format(profile.get('tool')).strip())
        print(t("cli_created").format(profile.get('created_at', '?')[:19]))
        print(t("cli_updated").format(profile.get('updated_at', '?')[:19]).strip())
        print(f"\n{t('cli_settings')}")
        for key, value in profile.get("settings", {}).items():
            print(f"    {key}: {value}")


# ============================================================
# HISTORY - Manage history / Gerenciar histórico
# ============================================================
def cmd_history(args):
    """List or manage process history / Lista ou gerencia histórico"""
    history = load_history()
    
    if args.action == "list" or args.action is None:
        if not history:
            print(t("cli_no_history"))
            return
        
        print(f"{t('cli_process_history')}\n")
        for i, entry in enumerate(history[:20], 1):
            tool = entry.get("tool_name", entry.get("tool_id", "?"))
            timestamp = entry.get("timestamp", "?")
            input_file = entry.get("input_file", "")
            
            print(f"  {i:2}. [{timestamp}] {tool}")
            if input_file:
                print(t("cli_file").format(Path(input_file).name if input_file else '-'))
    
    elif args.action == "show":
        if args.index is None:
            print(t("cli_specify_index"))
            return
        
        if args.index < 1 or args.index > len(history):
            print(t("cli_invalid_index").format(len(history)))
            return
        
        entry = history[args.index - 1]
        print(f"{t('cli_process').format(args.index)}\n")
        print(t("cli_tool").format(entry.get('tool_name', entry.get('tool_id'))).strip())
        print(t("cli_datetime").format(entry.get('timestamp')))
        print(t("cli_input").format(entry.get('input_file', '-')))
        print(t("cli_output").format(entry.get('output_file', '-')))
        print(f"\n{t('cli_settings')}")
        for key, value in entry.get("settings", {}).items():
            print(f"    {key}: {value}")
    
    elif args.action == "clear":
        import os
        history_path = get_user_data_dir() / "history.json"
        if history_path.exists():
            os.remove(history_path)
            print(t("cli_history_cleared"))
        else:
            print(t("cli_history_empty"))


# ============================================================
# ARGUMENT PARSER / PARSER DE ARGUMENTOS
# ============================================================
def create_parser():
    parser = argparse.ArgumentParser(
        prog='csvtoolbox',
        description=t('cli_desc'),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / Exemplos:
  %(prog)s merge -o output.csv file1.csv file2.csv
  %(prog)s split -r 10000 large_file.csv
  %(prog)s clean --trim --uppercase file.csv
  %(prog)s convert spreadsheet.xlsx -o data.csv
  %(prog)s transform data.csv -c STATE --depara states.csv
  %(prog)s info file.csv --sample 5
  %(prog)s profiles                    # list saved profiles
  %(prog)s profiles show --name my_profile
  %(prog)s history                     # list recent processes
  %(prog)s history show --index 1      # show process #1 details
  %(prog)s history clear               # clear history
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help=t('cli_help_command'))
    
    # --- MERGE ---
    merge_parser = subparsers.add_parser('merge', help=t('cli_merge_help'))
    merge_parser.add_argument('files', nargs='+', help=t('cli_arg_files'))
    merge_parser.add_argument('-o', '--output', required=True, help=t('cli_arg_output'))
    merge_parser.add_argument('-s', '--separator', default='semicolon', help=t('cli_arg_separator'))
    merge_parser.add_argument('-e', '--encoding', default='auto', help=t('cli_arg_encoding'))
    merge_parser.add_argument('--drop-duplicates', action='store_true', help=t('cli_arg_drop_duplicates'))
    
    # --- SPLIT ---
    split_parser = subparsers.add_parser('split', help=t('cli_split_help'))
    split_parser.add_argument('file', help=t('cli_arg_file_split'))
    split_parser.add_argument('-r', '--rows', type=int, default=50000, help=t('cli_arg_rows'))
    split_parser.add_argument('-o', '--output-dir', help=t('cli_arg_output_dir'))
    split_parser.add_argument('-s', '--separator', default='semicolon', help=t('cli_arg_separator'))
    split_parser.add_argument('-e', '--encoding', default='auto', help=t('cli_arg_encoding'))
    
    # --- CLEAN ---
    clean_parser = subparsers.add_parser('clean', help=t('cli_clean_help'))
    clean_parser.add_argument('file', help=t('cli_arg_file_clean'))
    clean_parser.add_argument('-o', '--output', help=t('cli_arg_output'))
    clean_parser.add_argument('-s', '--separator', default='semicolon', help=t('cli_arg_separator'))
    clean_parser.add_argument('-e', '--encoding', default='auto', help=t('cli_arg_encoding'))
    clean_parser.add_argument('--trim', action='store_true', help=t('cli_arg_trim'))
    clean_parser.add_argument('--remove-quotes', action='store_true', help=t('cli_arg_remove_quotes'))
    clean_parser.add_argument('--uppercase', action='store_true', help=t('cli_arg_uppercase'))
    clean_parser.add_argument('--drop-empty', action='store_true', help=t('cli_arg_drop_empty'))
    
    # --- CONVERT ---
    convert_parser = subparsers.add_parser('convert', help=t('cli_convert_help'))
    convert_parser.add_argument('file', help=t('cli_arg_file_input'))
    convert_parser.add_argument('-o', '--output', required=True, help=t('cli_arg_output'))
    convert_parser.add_argument('-s', '--separator', default='semicolon', help=t('cli_arg_separator'))
    convert_parser.add_argument('--output-separator', help=t('cli_arg_output_separator'))
    convert_parser.add_argument('-e', '--encoding', default='auto', help=t('cli_arg_encoding'))
    convert_parser.add_argument('--sheet', help=t('cli_arg_sheet'))
    
    # --- TRANSFORM ---
    transform_parser = subparsers.add_parser('transform', help=t('cli_transform_help'))
    transform_parser.add_argument('file', help='CSV file')
    transform_parser.add_argument('-c', '--column', required=True, help=t('cli_arg_column'))
    transform_parser.add_argument('--depara', required=True, help=t('cli_arg_depara'))
    transform_parser.add_argument('-o', '--output', help=t('cli_arg_output'))
    transform_parser.add_argument('-s', '--separator', default='semicolon', help=t('cli_arg_separator'))
    transform_parser.add_argument('-e', '--encoding', default='auto', help=t('cli_arg_encoding'))
    
    # --- INFO ---
    info_parser = subparsers.add_parser('info', help=t('cli_info_help'))
    info_parser.add_argument('file', help='CSV file')
    info_parser.add_argument('-s', '--separator', default='semicolon', help=t('cli_arg_separator'))
    info_parser.add_argument('-e', '--encoding', default='auto', help=t('cli_arg_encoding'))
    info_parser.add_argument('--sample', type=int, help=t('cli_arg_sample'))
    
    # --- PROFILES ---
    profiles_parser = subparsers.add_parser('profiles', help=t('cli_profiles_help'))
    profiles_parser.add_argument('action', nargs='?', choices=['list', 'show'], default='list',
                                  help=t('cli_arg_action_profiles'))
    profiles_parser.add_argument('--name', '-n', help=t('cli_arg_profile_name'))
    
    # --- HISTORY ---
    history_parser = subparsers.add_parser('history', help=t('cli_history_help'))
    history_parser.add_argument('action', nargs='?', choices=['list', 'show', 'clear'], default='list',
                                 help=t('cli_arg_action_history'))
    history_parser.add_argument('--index', '-i', type=int, help=t('cli_arg_history_index'))
    
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        print(f"\n{t('cli_help_tip')}")
        return
    
    commands = {
        'merge': cmd_merge,
        'split': cmd_split,
        'clean': cmd_clean,
        'convert': cmd_convert,
        'transform': cmd_transform,
        'info': cmd_info,
        'profiles': cmd_profiles,
        'history': cmd_history,
    }
    
    try:
        commands[args.command](args)
    except FileNotFoundError as e:
        print(t("cli_file_not_found").format(e.filename))
        sys.exit(1)
    except Exception as e:
        print(t("cli_error").format(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
