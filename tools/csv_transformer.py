# CSV Transformer Tool - Ferramenta para Transformar Dados

import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
from pathlib import Path
import chardet


class CSVTransformerTool(ctk.CTkFrame):
    """Ferramenta para transformar dados CSV - substituição de valores, filtros, etc."""
    
    def __init__(self, parent, profile_manager):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.input_file = None
        self.df = None
        self.de_para_df = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Cria os widgets da ferramenta"""
        
        # === Cabeçalho ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="⚙️ Transformar Dados",
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
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        input_label = ctk.CTkLabel(
            input_frame,
            text="Arquivo CSV:",
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
            command=self.load_file,
            width=100,
            fg_color="blue"
        )
        btn_load.grid(row=0, column=3, padx=10, pady=15)
        
        # Separador e encoding na mesma linha
        sep_label = ctk.CTkLabel(input_frame, text="Sep:", font=ctk.CTkFont(size=12))
        sep_label.grid(row=1, column=0, padx=(20, 5), pady=5, sticky="e")
        
        self.sep_var = ctk.StringVar(value=";")
        sep_menu = ctk.CTkOptionMenu(
            input_frame,
            values=[";", ",", "|", "Tab"],
            variable=self.sep_var,
            width=80
        )
        sep_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        enc_label = ctk.CTkLabel(input_frame, text="Encoding:", font=ctk.CTkFont(size=12))
        enc_label.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        self.enc_var = ctk.StringVar(value="utf-8")
        enc_menu = ctk.CTkOptionMenu(
            input_frame,
            values=["utf-8", "latin-1", "windows-1252", "auto"],
            variable=self.enc_var,
            width=120
        )
        enc_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # === Abas de Transformações ===
        self.tabview = ctk.CTkTabview(self, height=350)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tab 1: Substituição DE-PARA
        self.tab_depara = self.tabview.add("📋 DE-PARA")
        self.create_depara_tab()
        
        # Tab 2: Filtrar Colunas
        self.tab_filter = self.tabview.add("🔍 Filtrar Colunas")
        self.create_filter_tab()
        
        # Tab 3: Transformar Valores
        self.tab_transform = self.tabview.add("🔄 Transformar")
        self.create_transform_tab()
        
        # === Frame de Saída ===
        output_frame = ctk.CTkFrame(self)
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
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=500)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Carregue um arquivo para começar",
            text_color="gray50"
        )
        self.status_label.pack()
        
        # === Botão Executar ===
        self.btn_execute = ctk.CTkButton(
            self,
            text="▶️ Executar Transformação",
            command=self.execute,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_execute.pack(pady=20)
        
    def create_depara_tab(self):
        """Cria o conteúdo da aba DE-PARA"""
        
        info_label = ctk.CTkLabel(
            self.tab_depara,
            text="Substitui valores em uma coluna usando uma tabela DE-PARA",
            text_color="gray50"
        )
        info_label.pack(pady=10)
        
        # Frame de configuração
        config_frame = ctk.CTkFrame(self.tab_depara)
        config_frame.pack(fill="x", padx=20, pady=10)
        
        # Coluna alvo
        col_label = ctk.CTkLabel(config_frame, text="Coluna alvo:", font=ctk.CTkFont(size=13))
        col_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.depara_column_var = ctk.StringVar(value="")
        self.depara_column_menu = ctk.CTkOptionMenu(
            config_frame,
            values=["Carregue um arquivo"],
            variable=self.depara_column_var,
            width=200
        )
        self.depara_column_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Arquivo DE-PARA
        depara_label = ctk.CTkLabel(config_frame, text="Arquivo DE-PARA:", font=ctk.CTkFont(size=13))
        depara_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.depara_file_entry = ctk.CTkEntry(config_frame, width=300)
        self.depara_file_entry.grid(row=1, column=1, padx=10, pady=10)
        
        btn_browse_depara = ctk.CTkButton(
            config_frame,
            text="Procurar...",
            command=self.browse_depara,
            width=100
        )
        btn_browse_depara.grid(row=1, column=2, padx=10, pady=10)
        
        # Coluna DE
        de_label = ctk.CTkLabel(config_frame, text="Coluna DE:", font=ctk.CTkFont(size=13))
        de_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.de_column_var = ctk.StringVar(value="")
        self.de_column_menu = ctk.CTkOptionMenu(
            config_frame,
            values=["Carregue o arquivo DE-PARA"],
            variable=self.de_column_var,
            width=150
        )
        self.de_column_menu.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Coluna PARA
        para_label = ctk.CTkLabel(config_frame, text="Coluna PARA:", font=ctk.CTkFont(size=13))
        para_label.grid(row=2, column=2, padx=20, pady=10, sticky="w")
        
        self.para_column_var = ctk.StringVar(value="")
        self.para_column_menu = ctk.CTkOptionMenu(
            config_frame,
            values=["Carregue o arquivo DE-PARA"],
            variable=self.para_column_var,
            width=150
        )
        self.para_column_menu.grid(row=2, column=3, padx=10, pady=10, sticky="w")
        
        # Habilitar DE-PARA
        self.enable_depara_var = ctk.BooleanVar(value=False)
        enable_depara = ctk.CTkCheckBox(
            self.tab_depara,
            text="Habilitar substituição DE-PARA",
            variable=self.enable_depara_var,
            font=ctk.CTkFont(size=14)
        )
        enable_depara.pack(pady=10)
        
    def create_filter_tab(self):
        """Cria o conteúdo da aba de Filtrar Colunas"""
        
        info_label = ctk.CTkLabel(
            self.tab_filter,
            text="Selecione as colunas que deseja manter no arquivo de saída",
            text_color="gray50"
        )
        info_label.pack(pady=10)
        
        # Frame para lista de colunas
        list_frame = ctk.CTkFrame(self.tab_filter)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Botões de seleção
        btn_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5)
        
        btn_select_all = ctk.CTkButton(
            btn_frame,
            text="Selecionar Todas",
            command=self.select_all_columns,
            width=120,
            height=28
        )
        btn_select_all.pack(side="left", padx=5)
        
        btn_deselect_all = ctk.CTkButton(
            btn_frame,
            text="Desmarcar Todas",
            command=self.deselect_all_columns,
            width=120,
            height=28
        )
        btn_deselect_all.pack(side="left", padx=5)
        
        # Frame scrollable para checkboxes das colunas
        self.columns_scroll = ctk.CTkScrollableFrame(list_frame, height=150)
        self.columns_scroll.pack(fill="both", expand=True, pady=10)
        
        self.column_vars = {}
        
        # Habilitar filtro
        self.enable_filter_var = ctk.BooleanVar(value=False)
        enable_filter = ctk.CTkCheckBox(
            self.tab_filter,
            text="Habilitar filtro de colunas",
            variable=self.enable_filter_var,
            font=ctk.CTkFont(size=14)
        )
        enable_filter.pack(pady=10)
        
    def create_transform_tab(self):
        """Cria o conteúdo da aba de Transformar"""
        
        info_label = ctk.CTkLabel(
            self.tab_transform,
            text="Aplique transformações nos valores das colunas",
            text_color="gray50"
        )
        info_label.pack(pady=10)
        
        # Frame de configuração
        config_frame = ctk.CTkFrame(self.tab_transform)
        config_frame.pack(fill="x", padx=20, pady=10)
        
        # Coluna alvo
        col_label = ctk.CTkLabel(config_frame, text="Coluna:", font=ctk.CTkFont(size=13))
        col_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.transform_column_var = ctk.StringVar(value="")
        self.transform_column_menu = ctk.CTkOptionMenu(
            config_frame,
            values=["Carregue um arquivo"],
            variable=self.transform_column_var,
            width=200
        )
        self.transform_column_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Transformações disponíveis
        self.uppercase_var = ctk.BooleanVar(value=False)
        uppercase = ctk.CTkCheckBox(
            config_frame,
            text="Converter para MAIÚSCULAS",
            variable=self.uppercase_var
        )
        uppercase.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        
        self.lowercase_var = ctk.BooleanVar(value=False)
        lowercase = ctk.CTkCheckBox(
            config_frame,
            text="Converter para minúsculas",
            variable=self.lowercase_var
        )
        lowercase.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        
        self.trim_var = ctk.BooleanVar(value=False)
        trim = ctk.CTkCheckBox(
            config_frame,
            text="Remover espaços (trim)",
            variable=self.trim_var
        )
        trim.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        
        self.remove_accents_var = ctk.BooleanVar(value=False)
        remove_accents = ctk.CTkCheckBox(
            config_frame,
            text="Remover acentos",
            variable=self.remove_accents_var
        )
        remove_accents.grid(row=4, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        
        # Prefixo/Sufixo
        prefix_label = ctk.CTkLabel(config_frame, text="Adicionar prefixo:", font=ctk.CTkFont(size=13))
        prefix_label.grid(row=1, column=2, padx=20, pady=5, sticky="w")
        
        self.prefix_entry = ctk.CTkEntry(config_frame, width=150)
        self.prefix_entry.grid(row=1, column=3, padx=10, pady=5)
        
        suffix_label = ctk.CTkLabel(config_frame, text="Adicionar sufixo:", font=ctk.CTkFont(size=13))
        suffix_label.grid(row=2, column=2, padx=20, pady=5, sticky="w")
        
        self.suffix_entry = ctk.CTkEntry(config_frame, width=150)
        self.suffix_entry.grid(row=2, column=3, padx=10, pady=5)
        
        # Habilitar transformação
        self.enable_transform_var = ctk.BooleanVar(value=False)
        enable_transform = ctk.CTkCheckBox(
            self.tab_transform,
            text="Habilitar transformações",
            variable=self.enable_transform_var,
            font=ctk.CTkFont(size=14)
        )
        enable_transform.pack(pady=10)
        
    def browse_input(self):
        """Seleciona o arquivo de entrada"""
        file = filedialog.askopenfilename(
            title="Selecionar arquivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
    def load_file(self):
        """Carrega o arquivo CSV"""
        filepath = self.input_entry.get()
        if not filepath:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro!")
            return
        
        try:
            sep = self.sep_var.get()
            if sep == "Tab":
                sep = "\t"
            
            enc = self.enc_var.get()
            if enc == "auto":
                with open(filepath, 'rb') as f:
                    result = chardet.detect(f.read(10000))
                    enc = result['encoding']
            
            self.df = pd.read_csv(filepath, sep=sep, encoding=enc, low_memory=False, dtype=str)
            
            # Atualizar menus de colunas
            columns = list(self.df.columns)
            
            self.depara_column_menu.configure(values=columns)
            self.transform_column_menu.configure(values=columns)
            
            if columns:
                self.depara_column_var.set(columns[0])
                self.transform_column_var.set(columns[0])
            
            # Atualizar checkboxes de colunas
            self.update_column_checkboxes(columns)
            
            # Sugerir saída
            base = os.path.splitext(filepath)[0]
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, f"{base}_transformado.csv")
            
            self.status_label.configure(text=f"Arquivo carregado: {len(self.df)} linhas, {len(columns)} colunas")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
            
    def update_column_checkboxes(self, columns):
        """Atualiza os checkboxes de colunas"""
        # Limpar checkboxes existentes
        for widget in self.columns_scroll.winfo_children():
            widget.destroy()
        
        self.column_vars = {}
        
        # Criar grid de checkboxes (3 colunas)
        for i, col in enumerate(columns):
            var = ctk.BooleanVar(value=True)
            self.column_vars[col] = var
            
            cb = ctk.CTkCheckBox(
                self.columns_scroll,
                text=col,
                variable=var,
                width=200
            )
            cb.grid(row=i//3, column=i%3, padx=10, pady=3, sticky="w")
            
    def select_all_columns(self):
        """Seleciona todas as colunas"""
        for var in self.column_vars.values():
            var.set(True)
            
    def deselect_all_columns(self):
        """Desmarca todas as colunas"""
        for var in self.column_vars.values():
            var.set(False)
            
    def browse_depara(self):
        """Seleciona o arquivo DE-PARA"""
        file = filedialog.askopenfilename(
            title="Selecionar arquivo DE-PARA",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file:
            self.depara_file_entry.delete(0, "end")
            self.depara_file_entry.insert(0, file)
            
            # Carregar e atualizar menus
            try:
                ext = os.path.splitext(file)[1].lower()
                if ext == '.xlsx':
                    self.de_para_df = pd.read_excel(file, dtype=str)
                else:
                    self.de_para_df = pd.read_csv(file, sep=';', encoding='utf-8', dtype=str)
                
                columns = list(self.de_para_df.columns)
                self.de_column_menu.configure(values=columns)
                self.para_column_menu.configure(values=columns)
                
                if len(columns) >= 2:
                    self.de_column_var.set(columns[0])
                    self.para_column_var.set(columns[1])
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar DE-PARA: {str(e)}")
                
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
            
    def remove_accents(self, text):
        """Remove acentos de um texto"""
        import unicodedata
        if pd.isna(text):
            return text
        text = str(text)
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
            
    def execute(self):
        """Executa as transformações"""
        if self.df is None:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro!")
            return
            
        output_file = self.output_entry.get()
        if not output_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo de saída!")
            return
        
        try:
            self.btn_execute.configure(state="disabled")
            self.status_label.configure(text="Processando...")
            self.progress_bar.set(0.1)
            self.update()
            
            result_df = self.df.copy()
            
            # 1. Substituição DE-PARA
            if self.enable_depara_var.get() and self.de_para_df is not None:
                self.status_label.configure(text="Aplicando DE-PARA...")
                self.progress_bar.set(0.3)
                self.update()
                
                col_alvo = self.depara_column_var.get()
                col_de = self.de_column_var.get()
                col_para = self.para_column_var.get()
                
                # Criar dicionário de substituição
                de_para_dict = dict(zip(
                    self.de_para_df[col_de].astype(str),
                    self.de_para_df[col_para].astype(str)
                ))
                
                result_df[col_alvo] = result_df[col_alvo].astype(str).map(
                    lambda x: de_para_dict.get(x, x)
                )
            
            # 2. Filtrar colunas
            if self.enable_filter_var.get():
                self.status_label.configure(text="Filtrando colunas...")
                self.progress_bar.set(0.5)
                self.update()
                
                selected_cols = [col for col, var in self.column_vars.items() if var.get()]
                result_df = result_df[selected_cols]
            
            # 3. Transformações
            if self.enable_transform_var.get():
                self.status_label.configure(text="Aplicando transformações...")
                self.progress_bar.set(0.7)
                self.update()
                
                col = self.transform_column_var.get()
                
                if col in result_df.columns:
                    if self.uppercase_var.get():
                        result_df[col] = result_df[col].astype(str).str.upper()
                    
                    if self.lowercase_var.get():
                        result_df[col] = result_df[col].astype(str).str.lower()
                    
                    if self.trim_var.get():
                        result_df[col] = result_df[col].astype(str).str.strip()
                    
                    if self.remove_accents_var.get():
                        result_df[col] = result_df[col].apply(self.remove_accents)
                    
                    prefix = self.prefix_entry.get()
                    if prefix:
                        result_df[col] = prefix + result_df[col].astype(str)
                    
                    suffix = self.suffix_entry.get()
                    if suffix:
                        result_df[col] = result_df[col].astype(str) + suffix
            
            # Salvar
            self.status_label.configure(text="Salvando...")
            self.progress_bar.set(0.9)
            self.update()
            
            sep = self.sep_var.get()
            if sep == "Tab":
                sep = "\t"
            
            result_df.to_csv(output_file, sep=sep, index=False, encoding='utf-8')
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Concluído! {len(result_df)} linhas salvas.")
            
            messagebox.showinfo(
                "Sucesso",
                f"Transformação concluída!\n\n"
                f"Linhas: {len(result_df)}\n"
                f"Colunas: {len(result_df.columns)}\n"
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
            "separator": self.sep_var.get(),
            "encoding": self.enc_var.get(),
            "enable_depara": self.enable_depara_var.get(),
            "depara_column": self.depara_column_var.get(),
            "de_column": self.de_column_var.get(),
            "para_column": self.para_column_var.get(),
            "enable_filter": self.enable_filter_var.get(),
            "selected_columns": [col for col, var in self.column_vars.items() if var.get()],
            "enable_transform": self.enable_transform_var.get(),
            "transform_column": self.transform_column_var.get(),
            "uppercase": self.uppercase_var.get(),
            "lowercase": self.lowercase_var.get(),
            "trim": self.trim_var.get(),
            "remove_accents": self.remove_accents_var.get(),
            "prefix": self.prefix_entry.get(),
            "suffix": self.suffix_entry.get()
        }
        
    def load_settings(self, settings):
        """Carrega configurações de um perfil"""
        if "separator" in settings:
            self.sep_var.set(settings["separator"])
        if "encoding" in settings:
            self.enc_var.set(settings["encoding"])
        if "enable_depara" in settings:
            self.enable_depara_var.set(settings["enable_depara"])
        if "depara_column" in settings:
            self.depara_column_var.set(settings["depara_column"])
        if "de_column" in settings:
            self.de_column_var.set(settings["de_column"])
        if "para_column" in settings:
            self.para_column_var.set(settings["para_column"])
        if "enable_filter" in settings:
            self.enable_filter_var.set(settings["enable_filter"])
        if "enable_transform" in settings:
            self.enable_transform_var.set(settings["enable_transform"])
        if "transform_column" in settings:
            self.transform_column_var.set(settings["transform_column"])
        if "uppercase" in settings:
            self.uppercase_var.set(settings["uppercase"])
        if "lowercase" in settings:
            self.lowercase_var.set(settings["lowercase"])
        if "trim" in settings:
            self.trim_var.set(settings["trim"])
        if "remove_accents" in settings:
            self.remove_accents_var.set(settings["remove_accents"])
        if "prefix" in settings:
            self.prefix_entry.delete(0, "end")
            self.prefix_entry.insert(0, settings["prefix"])
        if "suffix" in settings:
            self.suffix_entry.delete(0, "end")
            self.suffix_entry.insert(0, settings["suffix"])
            
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
                "transformer",
                self.get_settings()
            )
            messagebox.showinfo("Sucesso", f"Perfil '{profile_name}' salvo!")
