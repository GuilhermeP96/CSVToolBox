# Data Verticalizer Tool - Ferramenta para Verticalização e Higienização de Dados

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import re
import unicodedata
import chardet
from pathlib import Path
from datetime import datetime

# PyAccelerate — thread pool
from pyaccelerate.threads import submit as pa_submit

# Importar workflow manager
from tools.workflow_manager import workflow_manager

# Importar sistema de internacionalização
try:
    from i18n import t
except ImportError:
    def t(key):
        return key


class DataVerticalizerTool(ctk.CTkFrame):
    """Ferramenta para verticalização (unpivot) e higienização de dados CSV"""
    
    def __init__(self, parent, profile_manager):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.df = None
        self.input_file = None
        self.columns = []
        
        self.create_widgets()
        
    def create_widgets(self):
        """Cria os widgets da ferramenta"""
        
        # === Container com Scroll ===
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True)
        
        # === Cabeçalho ===
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="📊 " + t("tool_verticalizer"),
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Botão salvar perfil
        self.btn_save_profile = ctk.CTkButton(
            header,
            text="💾 " + t("save_profile"),
            command=self.save_current_profile,
            width=120,
            height=32
        )
        self.btn_save_profile.pack(side="right", padx=5)
        
        # === Frame de Seleção de Arquivo ===
        file_frame = ctk.CTkFrame(self.scroll_container)
        file_frame.pack(fill="x", padx=20, pady=10)
        
        file_label = ctk.CTkLabel(file_frame, text=t("input_file") + ":", font=ctk.CTkFont(size=14))
        file_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.file_entry = ctk.CTkEntry(file_frame, width=400, placeholder_text=t("select_csv_file"))
        self.file_entry.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        self.btn_browse = ctk.CTkButton(
            file_frame,
            text="📁 " + t("browse"),
            command=self.browse_file,
            width=100
        )
        self.btn_browse.grid(row=0, column=2, padx=10, pady=15)
        
        self.btn_load = ctk.CTkButton(
            file_frame,
            text="📥 " + t("load"),
            command=self.load_file,
            width=100,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_load.grid(row=0, column=3, padx=10, pady=15)
        
        file_frame.columnconfigure(1, weight=1)
        
        # === Configurações de Leitura ===
        read_frame = ctk.CTkFrame(self.scroll_container)
        read_frame.pack(fill="x", padx=20, pady=10)
        
        read_label = ctk.CTkLabel(read_frame, text=t("read_settings"), font=ctk.CTkFont(size=14, weight="bold"))
        read_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        # Separador
        sep_label = ctk.CTkLabel(read_frame, text=t("separator") + ":")
        sep_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.sep_var = ctk.StringVar(value=";")
        sep_menu = ctk.CTkOptionMenu(read_frame, values=[";", ",", "|", "\\t"], variable=self.sep_var, width=80)
        sep_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Encoding
        enc_label = ctk.CTkLabel(read_frame, text=t("encoding") + ":")
        enc_label.grid(row=1, column=2, padx=20, pady=5, sticky="w")
        self.enc_var = ctk.StringVar(value="utf-8")
        enc_menu = ctk.CTkOptionMenu(read_frame, values=["utf-8", "latin-1", "windows-1252", "iso-8859-1", "auto"], variable=self.enc_var, width=120)
        enc_menu.grid(row=1, column=3, padx=10, pady=5, sticky="w")
        
        # === Notebook com abas ===
        self.tabview = ctk.CTkTabview(self.scroll_container)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Aba Verticalização
        self.tab_vertical = self.tabview.add(t("verticalization"))
        self.create_vertical_tab()
        
        # Aba Higienização
        self.tab_sanitize = self.tabview.add(t("sanitization"))
        self.create_sanitize_tab()
        
        # === Frame de Saída ===
        output_frame = ctk.CTkFrame(self.scroll_container)
        output_frame.pack(fill="x", padx=20, pady=10)
        
        output_label = ctk.CTkLabel(output_frame, text=t("output_file") + ":", font=ctk.CTkFont(size=14))
        output_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.output_entry = ctk.CTkEntry(output_frame, width=400, placeholder_text=t("output_file_path"))
        self.output_entry.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        self.btn_output_browse = ctk.CTkButton(
            output_frame,
            text="📁 " + t("browse"),
            command=self.browse_output,
            width=100
        )
        self.btn_output_browse.grid(row=0, column=2, padx=10, pady=15)
        
        output_frame.columnconfigure(1, weight=1)
        
        # === Botão Executar ===
        self.btn_execute = ctk.CTkButton(
            self.scroll_container,
            text="▶️ " + t("execute"),
            command=self.execute,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_execute.pack(fill="x", padx=20, pady=20)
        
        # === Botão Adicionar ao Workflow ===
        self.btn_add_workflow = ctk.CTkButton(
            self.scroll_container,
            text="➕ " + t("add_to_workflow"),
            command=self.add_to_workflow,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="purple",
            hover_color="darkmagenta"
        )
        self.btn_add_workflow.pack(fill="x", padx=20, pady=(0, 20))
        
        # === Log de Saída ===
        log_label = ctk.CTkLabel(self.scroll_container, text=t("output_log") + ":", font=ctk.CTkFont(size=14, weight="bold"))
        log_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.log_text = ctk.CTkTextbox(self.scroll_container, height=150)
        self.log_text.pack(fill="x", padx=20, pady=(0, 20))
        
    def create_vertical_tab(self):
        """Cria a aba de verticalização"""
        
        # Descrição
        desc = ctk.CTkLabel(
            self.tab_vertical,
            text=t("vertical_desc"),
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            wraplength=700
        )
        desc.pack(pady=10, padx=20, anchor="w")
        
        # Frame de configuração
        config_frame = ctk.CTkFrame(self.tab_vertical)
        config_frame.pack(fill="x", padx=10, pady=10)
        
        # Colunas fixas (ID)
        fixed_label = ctk.CTkLabel(config_frame, text=t("fixed_columns") + ":", font=ctk.CTkFont(size=13))
        fixed_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.fixed_cols_entry = ctk.CTkEntry(config_frame, width=300, placeholder_text=t("fixed_cols_hint"))
        self.fixed_cols_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Colunas a verticalizar
        vert_label = ctk.CTkLabel(config_frame, text=t("columns_to_vertical") + ":", font=ctk.CTkFont(size=13))
        vert_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        
        self.vert_cols_entry = ctk.CTkEntry(config_frame, width=300, placeholder_text=t("vert_cols_hint"))
        self.vert_cols_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Nome da coluna de variável
        var_label = ctk.CTkLabel(config_frame, text=t("variable_column_name") + ":", font=ctk.CTkFont(size=13))
        var_label.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        
        self.var_name_entry = ctk.CTkEntry(config_frame, width=200)
        self.var_name_entry.insert(0, "PERIODO")
        self.var_name_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Nome da coluna de valor
        val_label = ctk.CTkLabel(config_frame, text=t("value_column_name") + ":", font=ctk.CTkFont(size=13))
        val_label.grid(row=3, column=0, padx=15, pady=10, sticky="w")
        
        self.val_name_entry = ctk.CTkEntry(config_frame, width=200)
        self.val_name_entry.insert(0, "VALOR")
        self.val_name_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Padrão regex para colunas de período
        pattern_label = ctk.CTkLabel(config_frame, text=t("period_pattern") + ":", font=ctk.CTkFont(size=13))
        pattern_label.grid(row=4, column=0, padx=15, pady=10, sticky="w")
        
        self.pattern_entry = ctk.CTkEntry(config_frame, width=300, placeholder_text="^\\d{4}\\.\\d{2}$")
        self.pattern_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        
        config_frame.columnconfigure(1, weight=1)
        
        # Opções adicionais
        options_frame = ctk.CTkFrame(self.tab_vertical)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        self.drop_na_var = ctk.BooleanVar(value=True)
        drop_na_cb = ctk.CTkCheckBox(options_frame, text=t("drop_empty_values"), variable=self.drop_na_var)
        drop_na_cb.pack(side="left", padx=15, pady=10)
        
        self.sort_result_var = ctk.BooleanVar(value=True)
        sort_cb = ctk.CTkCheckBox(options_frame, text=t("sort_result"), variable=self.sort_result_var)
        sort_cb.pack(side="left", padx=15, pady=10)
        
    def create_sanitize_tab(self):
        """Cria a aba de higienização"""
        
        # Descrição
        desc = ctk.CTkLabel(
            self.tab_sanitize,
            text=t("sanitize_desc"),
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            wraplength=700
        )
        desc.pack(pady=10, padx=20, anchor="w")
        
        # Frame de opções de higienização
        options_frame = ctk.CTkFrame(self.tab_sanitize)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        # Coluna 1
        col1 = ctk.CTkFrame(options_frame, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=10)
        
        self.trim_spaces_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(col1, text=t("trim_spaces"), variable=self.trim_spaces_var).pack(anchor="w", pady=5)
        
        self.remove_accents_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(col1, text=t("remove_accents"), variable=self.remove_accents_var).pack(anchor="w", pady=5)
        
        self.upper_case_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(col1, text=t("convert_upper"), variable=self.upper_case_var).pack(anchor="w", pady=5)
        
        self.lower_case_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(col1, text=t("convert_lower"), variable=self.lower_case_var).pack(anchor="w", pady=5)
        
        # Coluna 2
        col2 = ctk.CTkFrame(options_frame, fg_color="transparent")
        col2.pack(side="left", fill="both", expand=True, padx=10)
        
        self.remove_duplicates_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(col2, text=t("remove_duplicates"), variable=self.remove_duplicates_var).pack(anchor="w", pady=5)
        
        self.remove_empty_rows_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(col2, text=t("remove_empty_rows"), variable=self.remove_empty_rows_var).pack(anchor="w", pady=5)
        
        self.normalize_numbers_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(col2, text=t("normalize_numbers"), variable=self.normalize_numbers_var).pack(anchor="w", pady=5)
        
        self.normalize_dates_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(col2, text=t("normalize_dates"), variable=self.normalize_dates_var).pack(anchor="w", pady=5)
        
        # Frame de substituições customizadas
        replace_frame = ctk.CTkFrame(self.tab_sanitize)
        replace_frame.pack(fill="x", padx=10, pady=10)
        
        replace_label = ctk.CTkLabel(replace_frame, text=t("custom_replacements") + ":", font=ctk.CTkFont(size=13, weight="bold"))
        replace_label.pack(anchor="w", padx=15, pady=10)
        
        replace_hint = ctk.CTkLabel(replace_frame, text=t("replace_hint"), font=ctk.CTkFont(size=11), text_color="gray50")
        replace_hint.pack(anchor="w", padx=15)
        
        self.replace_text = ctk.CTkTextbox(replace_frame, height=80)
        self.replace_text.pack(fill="x", padx=15, pady=10)
        self.replace_text.insert("1.0", "# Exemplo: valor_antigo=valor_novo\n# NULL=\n# N/A=")
        
        # Colunas específicas para higienização
        cols_frame = ctk.CTkFrame(self.tab_sanitize)
        cols_frame.pack(fill="x", padx=10, pady=10)
        
        cols_label = ctk.CTkLabel(cols_frame, text=t("sanitize_columns") + ":", font=ctk.CTkFont(size=13))
        cols_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.sanitize_cols_entry = ctk.CTkEntry(cols_frame, width=400, placeholder_text=t("sanitize_cols_hint"))
        self.sanitize_cols_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        cols_frame.columnconfigure(1, weight=1)
        
    def browse_file(self):
        """Abre diálogo para selecionar arquivo"""
        filepath = filedialog.askopenfilename(
            title=t("select_csv_file"),
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filepath:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filepath)
            
    def browse_output(self):
        """Abre diálogo para selecionar arquivo de saída"""
        filepath = filedialog.asksaveasfilename(
            title=t("select_output_file"),
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filepath:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, filepath)
            
    def load_file(self):
        """Carrega o arquivo CSV"""
        filepath = self.file_entry.get().strip()
        if not filepath:
            messagebox.showwarning(t("warning"), t("select_file_first"))
            return
            
        try:
            # Detectar encoding se auto
            encoding = self.enc_var.get()
            if encoding == "auto":
                with open(filepath, 'rb') as f:
                    result = chardet.detect(f.read(10000))
                    encoding = result['encoding'] or 'utf-8'
                    
            # Obter separador
            sep = self.sep_var.get()
            if sep == "\\t":
                sep = "\t"
                
            # Carregar arquivo
            self.df = pd.read_csv(filepath, sep=sep, encoding=encoding)
            self.input_file = filepath
            self.columns = list(self.df.columns)
            
            # Gerar nome de saída padrão
            base = os.path.splitext(filepath)[0]
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, f"{base}_processed.csv")
            
            # Log
            self.log(f"✅ {t('file_loaded')}: {filepath}")
            self.log(f"   → {len(self.df)} {t('rows')}, {len(self.columns)} {t('columns')}")
            self.log(f"   → {t('columns')}: {', '.join(self.columns[:10])}{'...' if len(self.columns) > 10 else ''}")
            
        except Exception as e:
            messagebox.showerror(t("error"), f"{t('load_error')}: {e}")
            self.log(f"❌ {t('error')}: {e}")
            
    def log(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        
    def execute(self):
        """Executa o processamento"""
        if self.df is None:
            messagebox.showwarning(t("warning"), t("load_file_first"))
            return
            
        output_path = self.output_entry.get().strip()
        if not output_path:
            messagebox.showwarning(t("warning"), t("select_output_first"))
            return
            
        # Executar em thread via pyaccelerate pool
        self.btn_execute.configure(state="disabled")
        pa_submit(self._execute_processing, output_path)
        
    def _execute_processing(self, output_path):
        """Executa o processamento em thread separada"""
        try:
            df = self.df.copy()
            current_tab = self.tabview.get()
            
            self.log(f"🔄 {t('processing_started')}...")
            
            # Aplicar verticalização se na aba de verticalização
            if current_tab == t("verticalization"):
                df = self._apply_verticalization(df)
                
            # Aplicar higienização (sempre, mas configurável)
            df = self._apply_sanitization(df)
            
            # Salvar resultado
            sep = self.sep_var.get()
            if sep == "\\t":
                sep = "\t"
                
            df.to_csv(output_path, sep=sep, index=False, encoding="utf-8")
            
            self.log(f"✅ {t('file_saved')}: {output_path}")
            self.log(f"   → {len(df)} {t('rows')}, {len(df.columns)} {t('columns')}")
            
            self.after(0, lambda: messagebox.showinfo(t("success"), f"{t('processing_complete')}\n{output_path}"))
            
        except Exception as e:
            self.log(f"❌ {t('error')}: {e}")
            self.after(0, lambda: messagebox.showerror(t("error"), str(e)))
        finally:
            self.btn_execute.configure(state="normal")
            
    def _apply_verticalization(self, df):
        """Aplica verticalização (unpivot)"""
        fixed_cols = [c.strip() for c in self.fixed_cols_entry.get().split(",") if c.strip()]
        vert_cols = [c.strip() for c in self.vert_cols_entry.get().split(",") if c.strip()]
        var_name = self.var_name_entry.get().strip() or "PERIODO"
        val_name = self.val_name_entry.get().strip() or "VALOR"
        pattern = self.pattern_entry.get().strip()
        
        # Se não especificou colunas, usar padrão regex
        if not vert_cols and pattern:
            regex = re.compile(pattern)
            vert_cols = [c for c in df.columns if regex.match(str(c))]
            self.log(f"   → {t('columns_matched')}: {len(vert_cols)}")
            
        # Se não especificou colunas fixas, usar as que não são verticalizáveis
        if not fixed_cols:
            fixed_cols = [c for c in df.columns if c not in vert_cols]
            
        if not vert_cols:
            self.log(f"⚠️ {t('no_columns_to_vertical')}")
            return df
            
        self.log(f"   → {t('fixed_columns')}: {', '.join(fixed_cols)}")
        self.log(f"   → {t('vertical_columns')}: {len(vert_cols)}")
        
        # Fazer unpivot (melt)
        df_melted = pd.melt(
            df,
            id_vars=fixed_cols,
            value_vars=vert_cols,
            var_name=var_name,
            value_name=val_name
        )
        
        # Remover valores vazios se configurado
        if self.drop_na_var.get():
            before = len(df_melted)
            df_melted = df_melted.dropna(subset=[val_name])
            df_melted = df_melted[df_melted[val_name] != ""]
            after = len(df_melted)
            if before != after:
                self.log(f"   → {t('removed_empty')}: {before - after}")
                
        # Ordenar se configurado
        if self.sort_result_var.get() and fixed_cols:
            df_melted = df_melted.sort_values(by=fixed_cols + [var_name])
            
        return df_melted
        
    def _apply_sanitization(self, df):
        """Aplica higienização aos dados"""
        # Obter colunas específicas ou todas
        sanitize_cols = [c.strip() for c in self.sanitize_cols_entry.get().split(",") if c.strip()]
        if not sanitize_cols:
            sanitize_cols = list(df.columns)
            
        cols_to_process = [c for c in sanitize_cols if c in df.columns]
        
        # Aplicar transformações
        for col in cols_to_process:
            if df[col].dtype == object:  # Apenas strings
                # Trim espaços
                if self.trim_spaces_var.get():
                    df[col] = df[col].astype(str).str.strip()
                    
                # Remover acentos
                if self.remove_accents_var.get():
                    df[col] = df[col].apply(lambda x: self._remove_accents(str(x)) if pd.notna(x) else x)
                    
                # Maiúsculas
                if self.upper_case_var.get():
                    df[col] = df[col].astype(str).str.upper()
                    
                # Minúsculas
                if self.lower_case_var.get():
                    df[col] = df[col].astype(str).str.lower()
                    
        # Normalizar números
        if self.normalize_numbers_var.get():
            for col in cols_to_process:
                try:
                    # Tentar converter para número
                    df[col] = df[col].astype(str).str.replace(",", ".").str.replace(" ", "")
                except:
                    pass
                    
        # Aplicar substituições customizadas
        replacements = self._parse_replacements()
        if replacements:
            for old, new in replacements.items():
                for col in cols_to_process:
                    df[col] = df[col].replace(old, new)
            self.log(f"   → {t('replacements_applied')}: {len(replacements)}")
                    
        # Remover linhas vazias
        if self.remove_empty_rows_var.get():
            before = len(df)
            df = df.dropna(how='all')
            after = len(df)
            if before != after:
                self.log(f"   → {t('empty_rows_removed')}: {before - after}")
                
        # Remover duplicatas
        if self.remove_duplicates_var.get():
            before = len(df)
            df = df.drop_duplicates()
            after = len(df)
            if before != after:
                self.log(f"   → {t('duplicates_removed')}: {before - after}")
                
        return df
        
    def _remove_accents(self, text):
        """Remove acentos de um texto"""
        if not isinstance(text, str):
            return text
        nfkd = unicodedata.normalize('NFKD', text)
        return ''.join([c for c in nfkd if not unicodedata.combining(c)])
        
    def _parse_replacements(self):
        """Parse as substituições customizadas do texto"""
        replacements = {}
        text = self.replace_text.get("1.0", "end").strip()
        for line in text.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                parts = line.split("=", 1)
                if len(parts) == 2:
                    old = parts[0].strip()
                    new = parts[1].strip()
                    replacements[old] = new
        return replacements
        
    def save_current_profile(self):
        """Salva o perfil atual"""
        from tkinter import simpledialog
        name = simpledialog.askstring(t("save_profile"), t("profile_name_prompt"))
        if name:
            settings = self.get_settings()
            self.profile_manager.save_profile(name, "verticalizer", settings)
            messagebox.showinfo(t("success"), t("profile_saved"))

    def add_to_workflow(self):
        """Adiciona a configuração atual como etapa do workflow"""
        input_file = self.file_entry.get().strip()
        output_file = self.output_entry.get().strip()
        
        if not input_file:
            messagebox.showwarning(t("warning"), t("select_input_first"))
            return
            
        if not output_file:
            messagebox.showwarning(t("warning"), t("select_output_first"))
            return
            
        # Perguntar se deve usar saída anterior
        use_previous = False
        if workflow_manager.get_step_count() > 0:
            use_previous = messagebox.askyesno(
                t("workflow"),
                t("use_previous_output_question")
            )
            
        # Adicionar ao workflow
        workflow_manager.add_step(
            tool_id="verticalizer",
            tool_name="📊 " + t("tool_verticalizer"),
            input_file=input_file if not use_previous else None,
            output_file=output_file,
            config=self.get_settings(),
            use_previous_output=use_previous
        )
        
        messagebox.showinfo(
            t("success"),
            f"{t('step_added_to_workflow')}\n{t('total_steps')}: {workflow_manager.get_step_count()}"
        )
            
    def get_settings(self):
        """Retorna as configurações atuais"""
        return {
            "separator": self.sep_var.get(),
            "encoding": self.enc_var.get(),
            "fixed_columns": self.fixed_cols_entry.get(),
            "vertical_columns": self.vert_cols_entry.get(),
            "var_name": self.var_name_entry.get(),
            "val_name": self.val_name_entry.get(),
            "pattern": self.pattern_entry.get(),
            "drop_na": self.drop_na_var.get(),
            "sort_result": self.sort_result_var.get(),
            "trim_spaces": self.trim_spaces_var.get(),
            "remove_accents": self.remove_accents_var.get(),
            "upper_case": self.upper_case_var.get(),
            "lower_case": self.lower_case_var.get(),
            "remove_duplicates": self.remove_duplicates_var.get(),
            "remove_empty_rows": self.remove_empty_rows_var.get(),
            "normalize_numbers": self.normalize_numbers_var.get(),
            "sanitize_columns": self.sanitize_cols_entry.get(),
            "replacements": self.replace_text.get("1.0", "end")
        }
        
    def load_settings(self, settings):
        """Carrega configurações de um perfil"""
        if "separator" in settings:
            self.sep_var.set(settings["separator"])
        if "encoding" in settings:
            self.enc_var.set(settings["encoding"])
        if "fixed_columns" in settings:
            self.fixed_cols_entry.delete(0, "end")
            self.fixed_cols_entry.insert(0, settings["fixed_columns"])
        if "vertical_columns" in settings:
            self.vert_cols_entry.delete(0, "end")
            self.vert_cols_entry.insert(0, settings["vertical_columns"])
        if "var_name" in settings:
            self.var_name_entry.delete(0, "end")
            self.var_name_entry.insert(0, settings["var_name"])
        if "val_name" in settings:
            self.val_name_entry.delete(0, "end")
            self.val_name_entry.insert(0, settings["val_name"])
        if "pattern" in settings:
            self.pattern_entry.delete(0, "end")
            self.pattern_entry.insert(0, settings["pattern"])
        if "drop_na" in settings:
            self.drop_na_var.set(settings["drop_na"])
        if "sort_result" in settings:
            self.sort_result_var.set(settings["sort_result"])
        if "trim_spaces" in settings:
            self.trim_spaces_var.set(settings["trim_spaces"])
        if "remove_accents" in settings:
            self.remove_accents_var.set(settings["remove_accents"])
        if "upper_case" in settings:
            self.upper_case_var.set(settings["upper_case"])
        if "lower_case" in settings:
            self.lower_case_var.set(settings["lower_case"])
        if "remove_duplicates" in settings:
            self.remove_duplicates_var.set(settings["remove_duplicates"])
        if "remove_empty_rows" in settings:
            self.remove_empty_rows_var.set(settings["remove_empty_rows"])
        if "normalize_numbers" in settings:
            self.normalize_numbers_var.set(settings["normalize_numbers"])
        if "sanitize_columns" in settings:
            self.sanitize_cols_entry.delete(0, "end")
            self.sanitize_cols_entry.insert(0, settings["sanitize_columns"])
        if "replacements" in settings:
            self.replace_text.delete("1.0", "end")
            self.replace_text.insert("1.0", settings["replacements"])
