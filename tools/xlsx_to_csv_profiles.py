# -*- coding: utf-8 -*-
"""
xlsx_to_csv_profiles.py
Ferramenta de conversao Excel para CSV com perfis configuraveis
Integrada ao CSVToolBox - Baseada não projeto xlsx-CSV-multi-perfis

Todos os perfis sao carregados do config.json (nada hardcoded)
"""

import os
import json
import csv
import re
import unicodedata
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

# Tentar importar pyxlsb para suporte a .xlsb
try:
    import pyxlsb
    HAS_PYXLSB = True
except ImportError:
    HAS_PYXLSB = False

# Mapeamento de meses pt-BR para numero
MONTH_MAP = {
    'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04',
    'mai': '05', 'jun': '06', 'jul': '07', 'ago': '08',
    'set': '09', 'out': '10', 'nov': '11', 'dez': '12'
}


# ==================== FUNCOES DE CONFIG ====================

def get_config_path():
    """Retorna o caminho do config.json do CSVToolBox"""
    import sys
    if hasattr(sys, '_MEIPASS'):
        # Running as compiled exe - usar diretorio do exe
        return os.path.join(os.path.dirname(sys.executable), "config.json")
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def get_temp_config_path():
    """Retorna o caminho do config.json temporario em C:\\temp"""
    return "C:\\temp\\xlsx_csv_multi.config.json"


def sync_config_to_temp():
    """Copia o config.json da raiz para C:\\temp se existir"""
    source_path = get_config_path()
    temp_path = get_temp_config_path()
    
    if os.path.exists(source_path):
        try:
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(source_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao sincronizar config: {e}")
            return False
    return False


def load_full_config():
    """Carrega o config.json completo"""
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar config.json: {e}")
    return {}


def load_xlsx_profiles():
    """Carrega os perfis de conversao do config.json"""
    config = load_full_config()
    return config.get("xlsx_profiles", {})


def load_base_config():
    """Carrega as configuracoes base (excel, csv, header, output)"""
    config = load_full_config()
    return {
        "excel": config.get("excel", {}),
        "csv": config.get("csv", {}),
        "header": config.get("header", {}),
        "output": config.get("output", {})
    }


def save_xlsx_profile(profile_name, profile_data):
    """Salva um perfil não config.json"""
    config_path = get_config_path()
    try:
        config = load_full_config()
        if "xlsx_profiles" not in config:
            config["xlsx_profiles"] = {}
        config["xlsx_profiles"][profile_name] = profile_data
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar perfil: {e}")
        return False


def delete_xlsx_profile(profile_name):
    """Remove um perfil do config.json"""
    config_path = get_config_path()
    try:
        config = load_full_config()
        if "xlsx_profiles" in config and profile_name in config["xlsx_profiles"]:
            del config["xlsx_profiles"][profile_name]
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        return False
    except Exception as e:
        print(f"Erro ao deletar perfil: {e}")
        return False


def merge_config(base: Dict, profile: Dict) -> Dict:
    """Mescla configuracao base com perfil especifico (deep merge)."""
    result = {}
    for key in set(list(base.keys()) + list(profile.keys())):
        if key in base and key in profile:
            if isinstance(base[key], dict) and isinstance(profile[key], dict):
                result[key] = merge_config(base[key], profile[key])
            else:
                result[key] = profile[key]
        elif key in profile:
            result[key] = profile[key]
        else:
            result[key] = base[key]
    return result


# ==================== FUNCOES DE NORMALIZACAO ====================

_WS_RE = re.compile(r"\s+", flags=re.UNICODE)


def normalize(text: str) -> str:
    """Normaliza nomes de colunas removendo espacos extras e NBSP."""
    if text is None:
        return ''
    text = str(text).replace('\u00A0', ' ').replace('\u200B', '')
    text = text.strip()
    text = _WS_RE.sub(' ', text)
    return text


def strip_accents(s: str) -> str:
    """Normalizacao NFD e remocao de acentos."""
    nf = unicodedata.normalize('NFD', s)
    return ''.join(ch for ch in nf if unicodedata.category(ch) != 'Mn')


def normalize_header_for_oracle(name: str, cfg: Dict) -> str:
    """Normaliza nome de coluna para padrao Oracle."""
    s = str(name)
    if cfg.get('strip_accents', True):
        s = strip_accents(s)
    space_to = cfg.get('space_to', '_') or '_'
    s = re.sub(r"\s+", space_to, s)
    case = cfg.get('case', 'upper')
    if case == 'upper':
        s = s.upper()
    elif case == 'lower':
        s = s.lower()
    punct_as = cfg.get('punct_as', '_') or '_'
    allowed = cfg.get('allowed', 'A-Z0-9_')
    s = re.sub(fr"[^{allowed}]", punct_as, s)
    if cfg.get('collapse_underscores', True):
        s = re.sub(r"_+", "_", s)
    if cfg.get('trim_underscores', True):
        s = s.strip('_')
    return s


def normalize_headers(headers: List[str], header_cfg: Optional[Dict]) -> List[str]:
    """Normaliza lista de cabecalhos usando config."""
    cfg = header_cfg or {"normalize": True}
    if not cfg.get('normalize', True):
        return headers
    mapping = cfg.get('mapping') or {}
    out: List[str] = []
    for h in headers:
        if h in mapping and mapping[h]:
            out.append(str(mapping[h]))
        else:
            out.append(normalize_header_for_oracle(h, cfg))
    if cfg.get('deduplicate', True):
        seen = {}
        uniq = []
        for h in out:
            base = h or 'COL'
            if base not in seen:
                seen[base] = 0
                uniq.append(base)
            else:
                seen[base] += 1
                uniq.append(f"{base}_{seen[base]}")
        return uniq
    return out


# ==================== FUNCOES DE PARSING ====================

def parse_number(value) -> str:
    """Converte valor numerico para string com ponto decimal."""
    if pd.isna(value):
        return ''
    s = str(value).strip()
    if s == '':
        return ''
    try:
        if isinstance(value, (int, float)):
            return ("%s" % (float(value))).replace(',', '.')
    except Exception:
        pass
    s = s.replace('\u00A0', '')
    s = s.replace('.', '').replace(',', '.')
    return s


def parse_ptbr_number(value) -> str:
    """Converte numero em string do padrao pt-BR para ponto como separador decimal."""
    if pd.isna(value):
        return ''
    s = str(value).strip()
    if s == '':
        return ''
    try:
        if isinstance(value, (int, float)):
            return ("%s" % (float(value))).replace(',', '.')
    except Exception:
        pass
    s = s.replace('\u00A0', '')
    s = s.replace('.', '').replace(',', '.')
    return s


def period_to_date(period: str, date_format: str = "01/{month}/{year}") -> str:
    """Converte periodo não formato YYYY.MM para data DD/MM/YYYY."""
    try:
        parts = str(period).split('.')
        if len(parts) == 2:
            year = parts[0]
            month = parts[1].zfill(2)
            return date_format.format(month=month, year=year)
    except Exception:
        pass
    return period


def period_mmm_yy_to_date(period: str, date_format: str = "01/{month}/{year}") -> str:
    """Converte periodo não formato mmm-yy para data DD/MM/YYYY."""
    try:
        period = str(period).strip().lower()
        match = re.match(r'([a-z]{3})-(\d{2})', period)
        if match:
            month_abbr = match.group(1)
            year_short = match.group(2)
            month = MONTH_MAP.get(month_abbr, '01')
            year_int = int(year_short)
            year = str(2000 + year_int) if year_int < 50 else str(1900 + year_int)
            return date_format.format(month=month, year=year)
    except Exception:
        pass
    return period


# ==================== FUNCOES DE IDENTIFICACAO ====================

def infer_engine(input_path: Path) -> Optional[str]:
    """Infere o engine do pandas baseado na extensao do arquivo."""
    ext = input_path.suffix.lower()
    if ext == '.xlsb':
        return 'pyxlsb'
    return None


def map_columns(df_cols: List[str], wanted_cols: List[str]) -> Dict[str, str]:
    """Cria um mapeamento de colunas desejadas -> nomes reais do DataFrame."""
    norm_to_real = {normalize(c): c for c in df_cols}
    mapping: Dict[str, str] = {}
    missing: List[str] = []
    
    for w in wanted_cols:
        wn = normalize(w)
        real = norm_to_real.get(wn)
        if real is None:
            missing.append(w)
        else:
            mapping[w] = real
    
    if missing:
        available = '\n - '.join(sorted(norm_to_real.keys()))
        miss = '\n - '.join(missing)
        raise KeyError(
            "Nao encontrei as seguintes colunas na planilha:\n - " + miss +
            "\n\nColunas disponiveis (normalizadas):\n - " + available)
    
    return mapping


def identify_period_columns(columns: List[str], pattern: str, exclude_pattern: str) -> Tuple[List[str], List[str]]:
    """Identifica colunas de periodo pelo padrao regex."""
    period_re = re.compile(pattern)
    exclude_re = re.compile(exclude_pattern) if exclude_pattern else None
    
    period_cols = []
    excluded_cols = []
    
    for col in columns:
        col_str = str(col).strip()
        if exclude_re and exclude_re.match(col_str):
            excluded_cols.append(col)
        elif period_re.match(col_str):
            period_cols.append(col)
    
    return period_cols, excluded_cols


def read_super_header(input_path: Path, excel_cfg: Dict, engine_to_use: Optional[str],
                      all_columns: List[str], period_cols: List[str], log=lambda msg: None) -> Dict[str, str]:
    """Le a linha de super-header (ex: REAL/DESAFIO) e mapeia para cada coluna de periodo."""
    super_header_row = excel_cfg.get('super_header_row')
    if super_header_row is None:
        return {}
    
    sheet_name = excel_cfg.get('sheet_name')
    
    df_super = pd.read_excel(
        input_path,
        sheet_name=sheet_name,
        dtype=object,
        header=None,
        nrows=super_header_row + 1,
        engine=engine_to_use
    )
    
    super_row = df_super.iloc[super_header_row].tolist()
    log(f"Super-header (linha {super_header_row}): {[x for x in super_row if pd.notna(x)][:6]}...")
    
    col_type_map = {}
    
    for period_col in period_cols:
        try:
            col_idx = all_columns.index(period_col)
            if col_idx < len(super_row):
                super_val = super_row[col_idx]
                if pd.notna(super_val):
                    col_type_map[period_col] = str(super_val).strip()
        except (ValueError, IndexError):
            continue
    
    log(f"Mapeamento tipo periodo: {len(col_type_map)} colunas mapeadas")
    return col_type_map


def detect_profile(sheet_names: List[str], profiles: Dict, log=lambda msg: None) -> Tuple[Optional[str], Optional[Dict]]:
    """Detecta automaticamente qual perfil usar baseado nos nomes das sheets."""
    log(f"Abas encontradas: {sheet_names}")
    
    for profile_name, profile_data in profiles.items():
        excel_cfg = profile_data.get('excel', {})
        expected_sheet = excel_cfg.get('sheet_name', '')
        
        if expected_sheet in sheet_names:
            log(f"Perfil detectado: {profile_name} (aba: {expected_sheet})")
            return profile_name, profile_data
    
    log(f"Nenhum perfil correspondente encontrado para as abas: {sheet_names}")
    return None, None


# ==================== TRANSFORMACAO DIRETA ====================

def transform_direct(input_path: Path, out_dir_path: Path, config: Dict, log=lambda msg: None) -> Path:
    """Executa transformacao direta (sem verticalizacao) - usado pelo perfil CarteiraMVL."""
    excel_cfg = config.get('excel', {})
    csv_cfg = config.get('csv', {})
    
    sheet_name = excel_cfg.get('sheet_name', 'Dados')
    wanted_cols: List[str] = excel_cfg.get('columns', [])
    numeric_cols: List[str] = excel_cfg.get('numeric_columns', ['QTD'])
    header_row = excel_cfg.get('header_row', 0)
    
    out_dir_path.mkdir(parents=True, exist_ok=True)
    
    engine: Optional[str] = excel_cfg.get('engine') or infer_engine(input_path)
    valid_engines = {'openpyxl', 'pyxlsb', 'xlrd', 'odf', 'calamine'}
    engine_to_use: Optional[str] = engine if (engine in valid_engines) else None
    
    log(f"Lendo planilha: {input_path} | aba='{sheet_name}' | engine={engine_to_use or 'auto'}")
    df = pd.read_excel(
        input_path,
        sheet_name=sheet_name,
        dtype=object,
        header=header_row,
        engine=engine_to_use
    )
    
    log("Mapeando colunas...")
    df_columns = list(df.columns)
    mapping = map_columns(df_columns, wanted_cols)
    
    ordered_real_cols = [mapping[w] for w in wanted_cols]
    out_df = df[ordered_real_cols].copy()
    out_df.columns = wanted_cols
    
    header_cfg = config.get('header')
    final_headers = normalize_headers(list(out_df.columns), header_cfg)
    if final_headers != list(out_df.columns):
        log("Normalizando cabecalhos para padrao Oracle...")
        out_df.columns = final_headers
    
    log("Normalizando numeros (pt-BR)...")
    final_header_map = {w: final_headers[i] for i, w in enumerate(wanted_cols)}
    for col in numeric_cols:
        final_col_name = final_header_map.get(col, col)
        if final_col_name in out_df.columns:
            out_df[final_col_name] = out_df[final_col_name].apply(parse_ptbr_number)
    
    def _clean_empty(v):
        if pd.isna(v):
            return pd.NA
        s = str(v).replace('\u00A0', ' ').strip()
        return s if s != '' else pd.NA
    
    out_df = out_df.map(_clean_empty)
    drop_cfg = excel_cfg.get('drop_rows', {})
    drop_how = drop_cfg.get('how', 'all')
    if drop_how not in ('all', 'any'):
        drop_how = 'all'
    before = len(out_df)
    out_df = out_df.dropna(how=drop_how)
    after = len(out_df)
    if before != after:
        log(f"Linhas removidas por estarem vazias ({drop_how}): {before - after}")
    
    filename = csv_cfg.get('filename', 'output.csv')
    out_path = out_dir_path / filename
    
    quoting_mode = csv_cfg.get('quoting', 'all').lower()
    if quoting_mode == 'all':
        quoting = csv.QUOTE_ALL
    elif quoting_mode == 'minimal':
        quoting = csv.QUOTE_MINIMAL
    elif quoting_mode == 'nonnumeric':
        quoting = csv.QUOTE_NONNUMERIC
    else:
        quoting = csv.QUOTE_ALL
    
    sep = csv_cfg.get('delimiter', ';')
    quotechar = csv_cfg.get('quotechar', '"')
    encoding = csv_cfg.get('encoding', 'utf-8')
    
    log(f"Gravando CSV em: {out_path}")
    log(f"  {len(out_df)} linhas | Separador: '{sep}' | Encoding: {encoding}")
    
    out_df.to_csv(
        out_path,
        index=False,
        sep=sep,
        encoding=encoding,
        quoting=quoting,
        quotechar=quotechar,
        lineterminator='\n'
    )
    
    return out_path


# ==================== TRANSFORMACAO VERTICAL ====================

def transform_vertical(input_path: Path, out_dir_path: Path, config: Dict, log=lambda msg: None) -> Path:
    """Executa transformacao com verticalizacao de periodos - usado pelos perfis Fisicos e Ticket."""
    excel_cfg = config.get('excel', {})
    csv_cfg = config.get('csv', {})
    output_cfg = config.get('output', {})
    
    profile_name = config.get('name', 'Desconhecido')
    sheet_name = excel_cfg.get('sheet_name', 'Fisicos_Orcamento')
    header_row = excel_cfg.get('header_row', 6)
    fixed_columns: List[str] = list(excel_cfg.get('fixed_columns', []))
    period_pattern = excel_cfg.get('period_pattern', r"^\d{4}\.\d{2}$")
    exclude_pattern = excel_cfg.get('exclude_columns_pattern')
    period_format = excel_cfg.get('period_format', 'YYYY.MM')
    
    out_dir_path.mkdir(parents=True, exist_ok=True)
    
    engine: Optional[str] = excel_cfg.get('engine') or infer_engine(input_path)
    valid_engines = {'openpyxl', 'pyxlsb', 'xlrd', 'odf', 'calamine'}
    engine_to_use: Optional[str] = engine if (engine in valid_engines) else None
    
    log(f"=== Perfil: {profile_name} ===")
    log(f"Lendo planilha: {input_path}")
    log(f"  Aba: '{sheet_name}' | Linha cabecalho: {header_row} | Engine: {engine_to_use or 'auto'}")
    
    df = pd.read_excel(
        input_path,
        sheet_name=sheet_name,
        dtype=object,
        header=header_row,
        engine=engine_to_use
    )
    
    log(f"Planilha carregada: {len(df)} linhas x {len(df.columns)} colunas")
    
    all_columns = list(df.columns)
    log(f"Colunas encontradas (primeiras 10): {all_columns[:10]}...")
    
    period_cols, excluded_cols = identify_period_columns(all_columns, period_pattern, exclude_pattern)
    
    log(f"Colunas de periodo identificadas: {len(period_cols)}")
    if period_cols:
        log(f"  Primeira: {period_cols[0]} | Ultima: {period_cols[-1]}")
    
    if excluded_cols:
        log(f"Colunas excluidas (totais): {excluded_cols}")
    
    col_type_map = read_super_header(input_path, excel_cfg, engine_to_use, all_columns, period_cols, log)
    has_super_header = len(col_type_map) > 0
    
    missing_fixed = [c for c in fixed_columns if c not in all_columns]
    if missing_fixed:
        norm_to_real = {normalize(c): c for c in all_columns}
        for mf in list(missing_fixed):
            norm_mf = normalize(mf)
            if norm_mf in norm_to_real:
                idx = fixed_columns.index(mf)
                fixed_columns[idx] = norm_to_real[norm_mf]
                missing_fixed.remove(mf)
    
    if missing_fixed:
        available = ', '.join(all_columns[:10])
        raise KeyError(f"Colunas fixas nao encontradas: {missing_fixed}\nDisponiveis (primeiras 10): {available}...")
    
    log(f"Colunas fixas: {fixed_columns}")
    
    if not period_cols:
        raise ValueError(f"Nenhuma coluna de periodo encontrada não padrao: {period_pattern}")
    
    cols_to_keep = fixed_columns + period_cols
    df_filtered = df[cols_to_keep].copy()
    
    log(f"Verticalizando dados (unpivot)...")
    
    df_melted = pd.melt(
        df_filtered,
        id_vars=fixed_columns,
        value_vars=period_cols,
        var_name='PERIODO_ORIGINAL',
        value_name='QTD'
    )
    
    log(f"Dados apos unpivot: {len(df_melted)} linhas")
    
    date_col_name = output_cfg.get('date_column_name', 'ANO_MES')
    date_format = output_cfg.get('date_format', '01/{month}/{year}')
    
    if period_format == 'mmm-yy':
        log("Convertendo periodos do formato mmm-yy para data...")
        df_melted[date_col_name] = df_melted['PERIODO_ORIGINAL'].apply(
            lambda x: period_mmm_yy_to_date(x, date_format)
        )
    else:
        log("Convertendo periodos do formato YYYY.MM para data...")
        df_melted[date_col_name] = df_melted['PERIODO_ORIGINAL'].apply(
            lambda x: period_to_date(x, date_format)
        )
    
    type_col_name = output_cfg.get('type_column_name', 'TIPO_PERIODO')
    if has_super_header:
        log(f"Adicionando coluna {type_col_name} (REAL/DESAFIO)...")
        df_melted[type_col_name] = df_melted['PERIODO_ORIGINAL'].map(col_type_map).fillna('DESCONHECIDO')
    
    df_melted = df_melted.drop(columns=['PERIODO_ORIGINAL'])
    
    value_col_name = output_cfg.get('value_column_name', 'QTD')
    if has_super_header:
        final_columns = fixed_columns + [date_col_name, type_col_name, value_col_name]
    else:
        final_columns = fixed_columns + [date_col_name, value_col_name]
    
    if value_col_name != 'QTD':
        df_melted = df_melted.rename(columns={'QTD': value_col_name})
    
    df_final = df_melted[final_columns].copy()
    
    log("Normalizando valores numericos...")
    df_final[value_col_name] = df_final[value_col_name].apply(parse_number)
    
    def _clean_empty(v):
        if pd.isna(v):
            return pd.NA
        s = str(v).replace('\u00A0', ' ').strip()
        return s if s != '' else pd.NA
    
    df_final = df_final.map(_clean_empty)
    before = len(df_final)
    df_final = df_final.dropna(how='all')
    after = len(df_final)
    if before != after:
        log(f"Linhas removidas por estarem totalmente vazias: {before - after}")
    
    header_cfg = config.get('header')
    original_headers = list(df_final.columns)
    final_headers = normalize_headers(original_headers, header_cfg)
    
    if final_headers != original_headers:
        log("Normalizando cabecalhos para padrao Oracle...")
        log(f"  {original_headers} -> {final_headers}")
        df_final.columns = final_headers
    
    filename = csv_cfg.get('filename', 'output.csv')
    out_path = out_dir_path / filename
    
    quoting_mode = csv_cfg.get('quoting', 'all').lower()
    if quoting_mode == 'all':
        quoting = csv.QUOTE_ALL
    elif quoting_mode == 'minimal':
        quoting = csv.QUOTE_MINIMAL
    elif quoting_mode == 'nonnumeric':
        quoting = csv.QUOTE_NONNUMERIC
    else:
        quoting = csv.QUOTE_ALL
    
    sep = csv_cfg.get('delimiter', ';')
    quotechar = csv_cfg.get('quotechar', '"')
    encoding = csv_cfg.get('encoding', 'utf-8')
    
    log(f"Gravando CSV em: {out_path}")
    log(f"  {len(df_final)} linhas | Separador: '{sep}' | Encoding: {encoding}")
    
    df_final.to_csv(
        out_path,
        index=False,
        sep=sep,
        encoding=encoding,
        quoting=quoting,
        quotechar=quotechar,
        lineterminator='\n'
    )
    
    return out_path


# ==================== FUNCAO PRINCIPAL DE TRANSFORMACAO ====================

def transform_excel_to_csv(input_path: Path, out_dir_path: Path, config: Dict, log=lambda msg: None) -> Path:
    """Executa a transformacao baseada não modo do perfil (vertical ou direct)."""
    mode = config.get('mode', 'vertical')
    profile_name = config.get('name', 'Desconhecido')
    
    log(f"=== Perfil: {profile_name} | Modo: {mode} ===")
    
    if mode == 'direct':
        return transform_direct(input_path, out_dir_path, config, log)
    else:
        return transform_vertical(input_path, out_dir_path, config, log)


# ==================== GUI ====================

class ExcelToCSVProfilesTool(ctk.CTkFrame):
    """
    Ferramenta de conversao Excel para CSV com perfis configuraveis
    Integrada ao CSVToolBox
    """
    
    def __init__(self, parent, profile_manager=None):
        super().__init__(parent)
        self.profile_manager = profile_manager
        
        # Sincronizar config da raiz para temp ao iniciar
        sync_config_to_temp()
        
        self.profiles = load_xlsx_profiles()
        self.base_config = load_base_config()
        self.current_profile = None
        self.sheet_names = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Container principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # === Secao de Arquivo ===
        file_frame = ctk.CTkFrame(self)
        file_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(file_frame, text="Arquivo Excel:", font=("", 14, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        
        self.input_entry = ctk.CTkEntry(file_frame, placeholder_text="Selecione o arquivo Excel...")
        self.input_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        ctk.CTkButton(file_frame, text="Procurar...", width=100, command=self.browse_input).grid(
            row=0, column=2, padx=10, pady=10
        )
        
        # Seletor de Sheet
        ctk.CTkLabel(file_frame, text="Sheet:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.sheet_combo = ctk.CTkComboBox(file_frame, values=["(Selecione arquivo primeiro)"], state="disabled")
        self.sheet_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Pasta de saida
        ctk.CTkLabel(file_frame, text="Pasta de Saida:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.output_entry = ctk.CTkEntry(file_frame, placeholder_text="Pasta de saida (deixe vazio para mesma pasta)")
        self.output_entry.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        ctk.CTkButton(file_frame, text="Procurar...", width=100, command=self.browse_output).grid(
            row=2, column=2, padx=10, pady=10
        )
        
        # === Secao de Perfil ===
        profile_frame = ctk.CTkFrame(self)
        profile_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        profile_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(profile_frame, text="Perfil de Conversao:", font=("", 14, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        
        profile_names = ["Automatico"] + list(self.profiles.keys()) if self.profiles else ["(Nenhum perfil)"]
        self.profile_combo = ctk.CTkComboBox(
            profile_frame, 
            values=profile_names,
            command=self.on_profile_selected
        )
        self.profile_combo.set("Automatico")
        self.profile_combo.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        # Botãoes de perfil
        btn_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=10, pady=10)
        
        ctk.CTkButton(btn_frame, text="Editar", width=80, command=self.edit_profile).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Novo", width=80, command=self.new_profile).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Recarregar", width=90, command=self.reload_profiles).pack(side="left", padx=2)
        
        # Descricao do perfil
        self.profile_desc = ctk.CTkLabel(profile_frame, text="", text_color="gray")
        self.profile_desc.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        
        # === Opcoes ===
        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(options_frame, text="Separador:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.sep_combo = ctk.CTkComboBox(options_frame, values=[";", ",", "|", "\\t"], width=80)
        self.sep_combo.set(";")
        self.sep_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(options_frame, text="Encoding:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.enc_combo = ctk.CTkComboBox(options_frame, values=["utf-8", "latin-1", "cp1252"], width=100)
        self.enc_combo.set("utf-8")
        self.enc_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # === Log ===
        log_frame = ctk.CTkFrame(self)
        log_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(log_frame, text="Log:", font=("", 12, "bold")).grid(
            row=0, column=0, padx=10, pady=5, sticky="w"
        )
        
        self.log_text = ctk.CTkTextbox(log_frame, height=150)
        self.log_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # === Botãoes de Acao ===
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(
            action_frame, 
            text="Converter", 
            font=("", 14, "bold"),
            height=40,
            command=self.execute_conversion
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame,
            text="Salvar Perfil Atual",
            height=40,
            command=self.save_current_profile
        ).pack(side="left", padx=5)
        
        self.status_label = ctk.CTkLabel(action_frame, text="Pronto", text_color="gray")
        self.status_label.pack(side="right", padx=10)
    
    def log(self, message):
        """Adiciona mensagem ao log"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.update()
    
    def browse_input(self):
        """Abre diálogo para selecionar arquivo Excel"""
        filetypes = [
            ("Excel Files", "*.xlsx *.xlsb *.xls"),
            ("Todos", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, filename)
            self.load_sheet_names(filename)
    
    def browse_output(self):
        """Abre diálogo para selecionar pasta de saida"""
        dirname = filedialog.askdirectory()
        if dirname:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, dirname)
    
    def load_sheet_names(self, filepath):
        """Carrega nomes das sheets do arquivo Excel e detecta perfil automaticamente"""
        try:
            ext = os.path.splitext(filepath)[1].lower()
            if ext == '.xlsb':
                if not HAS_PYXLSB:
                    self.log("pyxlsb nao instalado. Instale com: pip install pyxlsb")
                    return
                engine = 'pyxlsb'
            else:
                engine = 'openpyxl'
            
            xl = pd.ExcelFile(filepath, engine=engine)
            self.sheet_names = xl.sheet_names
            
            self.sheet_combo.configure(values=self.sheet_names, state="normal")
            if self.sheet_names:
                self.sheet_combo.set(self.sheet_names[0])
            
            self.log(f"Sheets encontradas: {', '.join(self.sheet_names)}")
            
            # SEMPRE detectar perfil automaticamente ao carregar arquivo
            detected_name, detected_profile = detect_profile(self.sheet_names, self.profiles, self.log)
            if detected_name:
                self.current_profile = detected_profile
                # Atualizar o combo para mostrar o perfil detectado
                self.profile_combo.set(detected_name)
                mode = detected_profile.get('mode', 'vertical')
                self.profile_desc.configure(
                    text=f"✅ Perfil detectado automaticamente: {detected_name} | Modo: {mode}",
                    text_color="green"
                )
                self.log(f"✅ Perfil '{detected_name}' selecionado automaticamente!")
                # Selecionar a sheet correta
                excel_cfg = detected_profile.get('excel', {})
                expected_sheet = excel_cfg.get('sheet_name', '')
                if expected_sheet in self.sheet_names:
                    self.sheet_combo.set(expected_sheet)
                    self.log(f"Sheet '{expected_sheet}' selecionada")
            else:
                self.profile_desc.configure(
                    text="⚠️ Nenhum perfil detectado - selecione manualmente",
                    text_color="orange"
                )
                self.current_profile = None
                self.profile_combo.set("Automatico")
        
        except Exception as e:
            self.log(f"Erro ao ler sheets: {e}")
            import traceback
            self.log(traceback.format_exc())
    
    def on_profile_selected(self, profile_name):
        """Callback quando um perfil e selecionado"""
        if profile_name == "Automatico":
            self.profile_desc.configure(
                text="Deteccao automatica baseada na aba do Excel",
                text_color="gray"
            )
            self.current_profile = None
            # Re-detectar se ja tem arquivo selecionado
            if self.sheet_names:
                detected_name, detected_profile = detect_profile(self.sheet_names, self.profiles, self.log)
                if detected_name:
                    self.current_profile = detected_profile
                    self.profile_combo.set(detected_name)
                    self.profile_desc.configure(
                        text=f"✅ Perfil detectado: {detected_name} | Modo: {detected_profile.get('mode', 'vertical')}",
                        text_color="green"
                    )
                    # Selecionar sheet correta
                    excel_cfg = detected_profile.get('excel', {})
                    expected_sheet = excel_cfg.get('sheet_name', '')
                    if expected_sheet in self.sheet_names:
                        self.sheet_combo.set(expected_sheet)
        elif profile_name in self.profiles:
            self.current_profile = self.profiles[profile_name]
            mode = self.current_profile.get("mode", "direct")
            excel_cfg = self.current_profile.get("excel", {})
            sheet = excel_cfg.get("sheet_name", "?")
            self.profile_desc.configure(
                text=f"📋 Perfil: {profile_name} | Modo: {mode} | Sheet: {sheet}",
                text_color="white"
            )
            self.log(f"Perfil '{profile_name}' selecionado manualmente")
            # Selecionar a sheet correta se disponivel
            if sheet in self.sheet_names:
                self.sheet_combo.set(sheet)
    
    def edit_profile(self):
        """Abre editor de perfil"""
        profile_name = self.profile_combo.get()
        if profile_name == "Automatico" or profile_name not in self.profiles:
            messagebox.showwarning("Aviso", "Selecione um perfil valido para editar!")
            return
        
        ProfileEditorWindow(self, profile_name, self.profiles[profile_name])
    
    def new_profile(self):
        """Cria novo perfil"""
        ProfileEditorWindow(self, None, None)
    
    def reload_profiles(self):
        """Recarrega perfis do config.json"""
        self.profiles = load_xlsx_profiles()
        self.base_config = load_base_config()
        profile_names = ["Automatico"] + list(self.profiles.keys()) if self.profiles else ["(Nenhum perfil)"]
        self.profile_combo.configure(values=profile_names)
        self.profile_combo.set("Automatico")
        self.log("Perfis recarregados!")
    
    def save_current_profile(self):
        """Salva configuracoes atuais como perfil"""
        if self.profile_manager:
            self.profile_manager.save_profile("xlsx_profiles", self.get_current_settings())
            self.log("Perfil salvo não gerenciador!")
    
    def get_current_settings(self):
        """Retorna configuracoes atuais"""
        return {
            "input_file": self.input_entry.get(),
            "output_dir": self.output_entry.get(),
            "profile": self.profile_combo.get(),
            "sheet": self.sheet_combo.get(),
            "separator": self.sep_combo.get(),
            "encoding": self.enc_combo.get()
        }
    
    def load_settings(self, settings):
        """Carrega configuracoes de um perfil salvo"""
        if "input_file" in settings:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, settings["input_file"])
        if "output_dir" in settings:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, settings["output_dir"])
        if "profile" in settings:
            self.profile_combo.set(settings["profile"])
            self.on_profile_selected(settings["profile"])
        if "separator" in settings:
            self.sep_combo.set(settings["separator"])
        if "encoding" in settings:
            self.enc_combo.set(settings["encoding"])
    
    def execute_conversion(self):
        """Executa a conversao"""
        input_file = self.input_entry.get()
        output_dir = self.output_entry.get()
        profile_name = self.profile_combo.get()
        
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Erro", "Selecione um arquivo Excel valido!")
            return
        
        input_path = Path(input_file)
        
        # Determinar pasta de saida
        if output_dir:
            out_dir_path = Path(output_dir)
        else:
            out_dir_path = input_path.parent
        
        # Determinar perfil
        if profile_name == "Automatico":
            if self.current_profile is None:
                # Tentar detectar novamente
                detected_name, detected_profile = detect_profile(self.sheet_names, self.profiles, self.log)
                if detected_profile is None:
                    messagebox.showerror("Erro", 
                        "Nao foi possivel detectar o perfil automaticamente.\n\n"
                        "Verifique se o arquivo contem uma das abas esperadas ou selecione um perfil manualmente.")
                    return
                self.current_profile = detected_profile
            profile = self.current_profile
        elif profile_name in self.profiles:
            profile = self.profiles[profile_name]
        else:
            messagebox.showerror("Erro", "Selecione um perfil valido!")
            return
        
        # Mesclar config base com perfil
        config = merge_config(self.base_config, profile)
        
        # Sobrescrever separador e encoding se alterados na UI
        sep = self.sep_combo.get()
        if sep == "\\t":
            sep = "\t"
        config.setdefault('csv', {})['delimiter'] = sep
        config['csv']['encoding'] = self.enc_combo.get()
        
        self.status_label.configure(text="Processando...", text_color="orange")
        self.log_text.delete("1.0", "end")
        self.update()
        
        try:
            self.log(f"{'='*50}")
            self.log(f"Iniciando conversao...")
            self.log(f"Arquivo: {input_file}")
            self.log(f"Destino: {out_dir_path}")
            self.log(f"{'='*50}")
            
            out_path = transform_excel_to_csv(input_path, out_dir_path, config, log=self.log)
            
            self.log(f"{'='*50}")
            self.log(f"SUCESSO: CSV gerado em {out_path}")
            
            self.status_label.configure(text="Concluido!", text_color="green")
            messagebox.showinfo("Sucesso", f"CSV gerado em:\n{out_path}")
        
        except Exception as e:
            self.log(f"{'='*50}")
            self.log(f"ERRO: {e}")
            self.status_label.configure(text="Erro!", text_color="red")
            messagebox.showerror("Erro", str(e))


class ProfileEditorWindow(ctk.CTkToplevel):
    """Janela de edicao de perfil"""
    
    def __init__(self, parent, profile_name=None, profile_data=None):
        super().__init__(parent)
        self.parent_tool = parent
        self.original_name = profile_name
        self.profile_data = profile_data or {
            "name": "",
            "mode": "direct",
            "excel": {
                "sheet_name": "",
                "header_row": 0,
                "columns": []
            },
            "csv": {
                "filename": "output.csv"
            },
            "header": {
                "mapping": {}
            }
        }
        
        self.title("Editor de Perfil" if profile_name else "Novo Perfil")
        self.geometry("700x600")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        # Nome
        name_frame = ctk.CTkFrame(self)
        name_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        name_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(name_frame, text="Nome:").grid(row=0, column=0, padx=10, pady=5)
        self.name_entry = ctk.CTkEntry(name_frame)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        if self.original_name:
            self.name_entry.insert(0, self.original_name)
        
        # Modo
        mode_frame = ctk.CTkFrame(self)
        mode_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(mode_frame, text="Modo:").pack(side="left", padx=10, pady=5)
        self.mode_var = ctk.StringVar(value=self.profile_data.get("mode", "direct"))
        ctk.CTkRadioButton(mode_frame, text="Direto (mapeamento de colunas)", variable=self.mode_var, value="direct").pack(side="left", padx=10)
        ctk.CTkRadioButton(mode_frame, text="Vertical (transpor periodos)", variable=self.mode_var, value="vertical").pack(side="left", padx=10)
        
        # Excel config
        excel_frame = ctk.CTkFrame(self)
        excel_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        excel_frame.grid_columnconfigure(1, weight=1)
        
        excel_cfg = self.profile_data.get("excel", {})
        
        ctk.CTkLabel(excel_frame, text="Sheet:").grid(row=0, column=0, padx=10, pady=5)
        self.sheet_entry = ctk.CTkEntry(excel_frame)
        self.sheet_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.sheet_entry.insert(0, excel_cfg.get("sheet_name", ""))
        
        ctk.CTkLabel(excel_frame, text="Header Row:").grid(row=1, column=0, padx=10, pady=5)
        self.header_row_entry = ctk.CTkEntry(excel_frame, width=80)
        self.header_row_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.header_row_entry.insert(0, str(excel_cfg.get("header_row", 0)))
        
        # CSV config
        csv_frame = ctk.CTkFrame(self)
        csv_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        csv_frame.grid_columnconfigure(1, weight=1)
        
        csv_cfg = self.profile_data.get("csv", {})
        
        ctk.CTkLabel(csv_frame, text="Nome arquivo CSV:").grid(row=0, column=0, padx=10, pady=5)
        self.filename_entry = ctk.CTkEntry(csv_frame)
        self.filename_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.filename_entry.insert(0, csv_cfg.get("filename", "output.csv"))
        
        # JSON do perfil (avancado)
        json_frame = ctk.CTkFrame(self)
        json_frame.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        json_frame.grid_columnconfigure(0, weight=1)
        json_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(json_frame, text="Configuracao JSON (avancado):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.json_text = ctk.CTkTextbox(json_frame)
        self.json_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.json_text.insert("1.0", json.dumps(self.profile_data, indent=2, ensure_ascii=False))
        
        # Botãoes
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(btn_frame, text="Salvar", command=self.save_profile).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancelar", command=self.destroy).pack(side="left", padx=5)
        
        if self.original_name:
            ctk.CTkButton(btn_frame, text="Excluir", fg_color="red", command=self.delete_profile).pack(side="right", padx=5)
    
    def save_profile(self):
        """Salva o perfil"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Erro", "Digite um nome para o perfil!")
            return
        
        try:
            # Tentar parsear o JSON
            profile_data = json.loads(self.json_text.get("1.0", "end"))
            
            # Atualizar campos basicos do JSON com os valores dos campos
            profile_data["name"] = name
            profile_data["mode"] = self.mode_var.get()
            profile_data.setdefault("excel", {})["sheet_name"] = self.sheet_entry.get()
            profile_data["excel"]["header_row"] = int(self.header_row_entry.get() or 0)
            profile_data.setdefault("csv", {})["filename"] = self.filename_entry.get()
            
            # Salvar
            if save_xlsx_profile(name, profile_data):
                # Se renomeou, deletar o antigo
                if self.original_name and self.original_name != name:
                    delete_xlsx_profile(self.original_name)
                
                messagebox.showinfo("Sucesso", f"Perfil '{name}' salvo!")
                self.parent_tool.reload_profiles()
                self.destroy()
            else:
                messagebox.showerror("Erro", "Falha ao salvar perfil!")
        
        except json.JSONDecodeError as e:
            messagebox.showerror("Erro JSON", f"JSON invalido: {e}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    def delete_profile(self):
        """Exclui o perfil"""
        if messagebox.askyesno("Confirmar", f"Excluir perfil '{self.original_name}'?"):
            if delete_xlsx_profile(self.original_name):
                messagebox.showinfo("Sucesso", "Perfil excluido!")
                self.parent_tool.reload_profiles()
                self.destroy()
            else:
                messagebox.showerror("Erro", "Falha ao excluir perfil!")
