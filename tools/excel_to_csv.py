# Excel to CSV Tool - Ferramenta para Converter Excel para CSV com Configuração

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import json
import re
import unicodedata
from pathlib import Path
import threading


class ExcelToCSVTool(ctk.CTkFrame):
    """Ferramenta para converter Excel para CSV com configurações avançadas"""
    
    def __init__(self, parent, profile_manager):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.input_file = None
        self.sheets = []
        self.columns = []
        
        self.create_widgets()
        
    def create_widgets(self):
        """Cria os widgets da ferramenta"""
        
        
        # === Container com Scroll ===
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True)
        # === Cabeçalho ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="📑 Excel para CSV",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Botão salvar perfil
        self.btn_save_profile = ctk.CTkButton(
            header,
            text="💾 Salvar Perfil",
            command=self.save_current_profile,
            width=120,
            height=32
        )
        self.btn_save_profile.pack(side="right", padx=5)
        
        # === Frame de Arquivo de Entrada ===
        input_frame = ctk.CTkFrame(self.scroll_container)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        input_label = ctk.CTkLabel(
            input_frame,
            text="Arquivo Excel:",
            font=ctk.CTkFont(size=14)
        )
        input_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.input_entry = ctk.CTkEntry(input_frame, width=400)
        self.input_entry.grid(row=0, column=1, padx=10, pady=15)
        
        btn_browse_input = ctk.CTkButton(
            input_frame,
            text="Procurar...",
            command=self.browse_input,
            width=100
        )
        btn_browse_input.grid(row=0, column=2, padx=10, pady=15)
        
        btn_load = ctk.CTkButton(
            input_frame,
            text="Carregar",
            command=self.load_excel,
            width=100,
            fg_color="blue"
        )
        btn_load.grid(row=0, column=3, padx=10, pady=15)
        
        # Planilha
        sheet_label = ctk.CTkLabel(input_frame, text="Planilha:", font=ctk.CTkFont(size=13))
        sheet_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.sheet_var = ctk.StringVar(value="")
        self.sheet_menu = ctk.CTkOptionMenu(
            input_frame,
            values=["Carregue o arquivo"],
            variable=self.sheet_var,
            command=self.on_sheet_change,
            width=250
        )
        self.sheet_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Info
        self.info_label = ctk.CTkLabel(
            input_frame,
            text="",
            text_color="gray50"
        )
        self.info_label.grid(row=1, column=2, columnspan=2, padx=10, pady=10)
        
        # === Frame de Seleção de Colunas ===
        columns_frame = ctk.CTkFrame(self.scroll_container)
        columns_frame.pack(fill="x", padx=20, pady=10)
        
        columns_header = ctk.CTkFrame(columns_frame, fg_color="transparent")
        columns_header.pack(fill="x", padx=10, pady=10)
        
        columns_label = ctk.CTkLabel(
            columns_header,
            text="Selecionar Colunas:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        columns_label.pack(side="left")
        
        btn_select_all = ctk.CTkButton(
            columns_header,
            text="Todas",
            command=self.select_all_columns,
            width=80,
            height=28
        )
        btn_select_all.pack(side="right", padx=5)
        
        btn_deselect_all = ctk.CTkButton(
            columns_header,
            text="Nenhuma",
            command=self.deselect_all_columns,
            width=80,
            height=28
        )
        btn_deselect_all.pack(side="right", padx=5)
        
        # Frame scrollable para colunas
        self.columns_scroll = ctk.CTkScrollableFrame(columns_frame, height=120)
        self.columns_scroll.pack(fill="x", padx=10, pady=5)
        
        self.column_vars = {}
        
        # === Frame de Normalização de Cabeçalhos ===
        header_frame = ctk.CTkFrame(self.scroll_container)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="Normalização de Cabeçalhos",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        self.normalize_header_var = ctk.BooleanVar(value=True)
        normalize_check = ctk.CTkCheckBox(
            header_frame,
            text="Normalizar cabeçalhos",
            variable=self.normalize_header_var
        )
        normalize_check.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.uppercase_var = ctk.BooleanVar(value=True)
        uppercase_check = ctk.CTkCheckBox(
            header_frame,
            text="MAIÚSCULAS",
            variable=self.uppercase_var
        )
        uppercase_check.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        self.remove_accents_var = ctk.BooleanVar(value=True)
        remove_accents_check = ctk.CTkCheckBox(
            header_frame,
            text="Remover acentos",
            variable=self.remove_accents_var
        )
        remove_accents_check.grid(row=1, column=2, padx=20, pady=5, sticky="w")
        
        self.space_to_underscore_var = ctk.BooleanVar(value=True)
        space_check = ctk.CTkCheckBox(
            header_frame,
            text="Espaço → _",
            variable=self.space_to_underscore_var
        )
        space_check.grid(row=1, column=3, padx=20, pady=5, sticky="w")
        
        # === Frame de Configurações de Saída ===
        output_config = ctk.CTkFrame(self.scroll_container)
        output_config.pack(fill="x", padx=20, pady=10)
        
        output_config_label = ctk.CTkLabel(
            output_config,
            text="Configurações de Saída",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        output_config_label.grid(row=0, column=0, columnspan=6, padx=20, pady=10, sticky="w")
        
        # Encoding
        enc_label = ctk.CTkLabel(output_config, text="Encoding:", font=ctk.CTkFont(size=13))
        enc_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.enc_var = ctk.StringVar(value="utf-8")
        enc_menu = ctk.CTkOptionMenu(
            output_config,
            values=["utf-8", "utf-8-sig", "windows-1252", "latin-1"],
            variable=self.enc_var,
            width=130
        )
        enc_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Separador
        sep_label = ctk.CTkLabel(output_config, text="Separador:", font=ctk.CTkFont(size=13))
        sep_label.grid(row=1, column=2, padx=20, pady=10, sticky="w")
        
        self.sep_var = ctk.StringVar(value=";")
        sep_menu = ctk.CTkOptionMenu(
            output_config,
            values=[";", ",", "|", "Tab (\\t)"],
            variable=self.sep_var,
            width=100
        )
        sep_menu.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # Decimal
        dec_label = ctk.CTkLabel(output_config, text="Decimal:", font=ctk.CTkFont(size=13))
        dec_label.grid(row=1, column=4, padx=20, pady=10, sticky="w")
        
        self.dec_var = ctk.StringVar(value=".")
        dec_menu = ctk.CTkOptionMenu(
            output_config,
            values=[".", ","],
            variable=self.dec_var,
            width=60
        )
        dec_menu.grid(row=1, column=5, padx=10, pady=10, sticky="w")
        
        # Opções
        self.quote_all_var = ctk.BooleanVar(value=True)
        quote_check = ctk.CTkCheckBox(
            output_config,
            text="Aspas em todos os campos",
            variable=self.quote_all_var
        )
        quote_check.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="w")
        
        self.drop_empty_var = ctk.BooleanVar(value=True)
        drop_check = ctk.CTkCheckBox(
            output_config,
            text="Remover linhas vazias",
            variable=self.drop_empty_var
        )
        drop_check.grid(row=2, column=2, columnspan=2, padx=20, pady=10, sticky="w")
        
        # === Frame de Saída ===
        output_frame = ctk.CTkFrame(self.scroll_container)
        output_frame.pack(fill="x", padx=20, pady=10)
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="Arquivo de Saída:",
            font=ctk.CTkFont(size=14)
        )
        output_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.output_entry = ctk.CTkEntry(output_frame, width=450)
        self.output_entry.grid(row=0, column=1, padx=10, pady=15)
        
        btn_browse_output = ctk.CTkButton(
            output_frame,
            text="Procurar...",
            command=self.browse_output,
            width=100
        )
        btn_browse_output.grid(row=0, column=2, padx=10, pady=15)
        
        # === Barra de Progresso ===
        self.progress_frame = ctk.CTkFrame(self.scroll_container)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=500)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Carregue um arquivo Excel para começar",
            text_color="gray50"
        )
        self.status_label.pack()
        
        # === Botão Executar ===
        self.btn_execute = ctk.CTkButton(
            self.scroll_container,
            text="▶️ Executar Conversão",
            command=self.execute,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_execute.pack(pady=20)
        
    def browse_input(self):
        """Seleciona o arquivo de entrada"""
        file = filedialog.askopenfilename(
            title="Selecionar arquivo Excel",
            filetypes=[
                ("Excel files", "*.xlsx;*.xls;*.xlsb"),
                ("XLSX", "*.xlsx"),
                ("XLSB", "*.xlsb"),
                ("XLS", "*.xls"),
                ("All files", "*.*")
            ]
        )
        
        if file:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
    def load_excel(self):
        """Carrega o arquivo Excel e lista planilhas"""
        filepath = self.input_entry.get()
        if not filepath:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro!")
            return
        
        try:
            self.status_label.configure(text="Carregando arquivo...")
            self.update()
            
            # Determinar engine
            ext = os.path.splitext(filepath)[1].lower()
            engine = 'pyxlsb' if ext == '.xlsb' else None
            
            # Listar planilhas
            excel_file = pd.ExcelFile(filepath, engine=engine)
            self.sheets = excel_file.sheet_names
            
            self.sheet_menu.configure(values=self.sheets)
            if self.sheets:
                self.sheet_var.set(self.sheets[0])
                self.on_sheet_change(self.sheets[0])
            
            # Sugerir saída
            base = os.path.splitext(filepath)[0]
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, f"{base}.csv")
            
            self.status_label.configure(text=f"Arquivo carregado: {len(self.sheets)} planilha(s)")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
            self.status_label.configure(text=f"Erro: {str(e)}")
            
    def on_sheet_change(self, sheet_name):
        """Atualiza colunas quando a planilha muda"""
        filepath = self.input_entry.get()
        if not filepath:
            return
        
        try:
            ext = os.path.splitext(filepath)[1].lower()
            engine = 'pyxlsb' if ext == '.xlsb' else None
            
            # Ler apenas cabeçalhos
            df = pd.read_excel(filepath, sheet_name=sheet_name, engine=engine, nrows=5)
            self.columns = list(df.columns)
            
            self.update_column_checkboxes()
            self.info_label.configure(text=f"{len(self.columns)} colunas")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler planilha: {str(e)}")
            
    def update_column_checkboxes(self):
        """Atualiza os checkboxes de colunas"""
        for widget in self.columns_scroll.winfo_children():
            widget.destroy()
        
        self.column_vars = {}
        
        for i, col in enumerate(self.columns):
            var = ctk.BooleanVar(value=True)
            self.column_vars[col] = var
            
            cb = ctk.CTkCheckBox(
                self.columns_scroll,
                text=str(col)[:40],
                variable=var,
                width=200
            )
            cb.grid(row=i//3, column=i%3, padx=10, pady=3, sticky="w")
            
    def select_all_columns(self):
        for var in self.column_vars.values():
            var.set(True)
            
    def deselect_all_columns(self):
        for var in self.column_vars.values():
            var.set(False)
            
    def browse_output(self):
        """Seleciona o arquivo de saída"""
        file = filedialog.asksaveasfilename(
            title="Salvar como",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)
            
    def get_separator(self):
        sep = self.sep_var.get()
        if sep == "Tab (\\t)":
            return "\t"
        return sep
    
    def normalize_column_name(self, name):
        """Normaliza nome de coluna"""
        if not self.normalize_header_var.get():
            return str(name)
        
        name = str(name)
        
        # Remover acentos
        if self.remove_accents_var.get():
            name = unicodedata.normalize('NFD', name)
            name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
        
        # Maiúsculas
        if self.uppercase_var.get():
            name = name.upper()
        
        # Espaços para underscore
        if self.space_to_underscore_var.get():
            name = re.sub(r'\s+', '_', name)
            # Remover caracteres especiais
            name = re.sub(r'[^\w]', '_', name)
            # Colapsar underscores múltiplos
            name = re.sub(r'_+', '_', name)
            # Trim underscores
            name = name.strip('_')
        
        return name
            
    def execute(self):
        """Executa a conversão"""
        filepath = self.input_entry.get()
        output_file = self.output_entry.get()
        
        if not filepath:
            messagebox.showwarning("Aviso", "Carregue um arquivo Excel!")
            return
            
        if not output_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo de saída!")
            return
        
        thread = threading.Thread(target=self._execute_conversion, args=(filepath, output_file))
        thread.start()
        
    def _execute_conversion(self, filepath, output_file):
        """Executa a conversão em thread"""
        try:
            self.btn_execute.configure(state="disabled")
            self.status_label.configure(text="Lendo arquivo Excel...")
            self.progress_bar.set(0.2)
            self.update()
            
            # Determinar engine
            ext = os.path.splitext(filepath)[1].lower()
            engine = 'pyxlsb' if ext == '.xlsb' else None
            
            # Ler planilha
            sheet_name = self.sheet_var.get()
            df = pd.read_excel(filepath, sheet_name=sheet_name, engine=engine)
            
            self.progress_bar.set(0.4)
            self.status_label.configure(text="Processando dados...")
            self.update()
            
            # Filtrar colunas selecionadas
            selected_cols = [col for col, var in self.column_vars.items() if var.get()]
            if selected_cols:
                df = df[[col for col in selected_cols if col in df.columns]]
            
            # Normalizar cabeçalhos
            if self.normalize_header_var.get():
                df.columns = [self.normalize_column_name(col) for col in df.columns]
            
            # Remover linhas vazias
            if self.drop_empty_var.get():
                df = df.dropna(how='all')
            
            self.progress_bar.set(0.7)
            self.status_label.configure(text="Salvando CSV...")
            self.update()
            
            # Configurações de saída
            sep = self.get_separator()
            encoding = self.enc_var.get()
            decimal = self.dec_var.get()
            quoting = 1 if self.quote_all_var.get() else 0
            
            df.to_csv(
                output_file,
                sep=sep,
                encoding=encoding,
                index=False,
                decimal=decimal,
                quoting=quoting
            )
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Concluído! {len(df)} linhas salvas.")
            
            messagebox.showinfo(
                "Sucesso",
                f"Conversão concluída!\n\n"
                f"Linhas: {len(df)}\n"
                f"Colunas: {len(df.columns)}\n"
                f"Arquivo: {output_file}"
            )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar: {str(e)}")
            self.status_label.configure(text=f"Erro: {str(e)}")
        finally:
            self.btn_execute.configure(state="normal")
            
    def get_settings(self):
        """Retorna as configurações atuais"""
        return {
            "sheet_name": self.sheet_var.get(),
            "normalize_header": self.normalize_header_var.get(),
            "uppercase": self.uppercase_var.get(),
            "remove_accents": self.remove_accents_var.get(),
            "space_to_underscore": self.space_to_underscore_var.get(),
            "encoding": self.enc_var.get(),
            "separator": self.sep_var.get(),
            "decimal": self.dec_var.get(),
            "quote_all": self.quote_all_var.get(),
            "drop_empty": self.drop_empty_var.get()
        }
        
    def load_settings(self, settings):
        """Carrega configurações de um perfil"""
        if "normalize_header" in settings:
            self.normalize_header_var.set(settings["normalize_header"])
        if "uppercase" in settings:
            self.uppercase_var.set(settings["uppercase"])
        if "remove_accents" in settings:
            self.remove_accents_var.set(settings["remove_accents"])
        if "space_to_underscore" in settings:
            self.space_to_underscore_var.set(settings["space_to_underscore"])
        if "encoding" in settings:
            self.enc_var.set(settings["encoding"])
        if "separator" in settings:
            self.sep_var.set(settings["separator"])
        if "decimal" in settings:
            self.dec_var.set(settings["decimal"])
        if "quote_all" in settings:
            self.quote_all_var.set(settings["quote_all"])
        if "drop_empty" in settings:
            self.drop_empty_var.set(settings["drop_empty"])
            
    def save_current_profile(self):
        """Salva as configurações atuais como perfil"""
        dialog = ctk.CTkInputDialog(
            text="Nome do perfil:",
            title="Salvar Perfil"
        )
        profile_name = dialog.get_input()
        
        if profile_name:
            self.profile_manager.save_profile(
                profile_name,
                "excel_to_csv",
                self.get_settings()
            )
            messagebox.showinfo("Sucesso", f"Perfil '{profile_name}' salvo!")


