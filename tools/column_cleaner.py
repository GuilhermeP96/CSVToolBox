# Column Cleaner Tool - Ferramenta para Limpeza Avançada de Colunas

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import re
import unicodedata
import chardet
from pathlib import Path
import threading

# Importar workflow manager
from tools.workflow_manager import workflow_manager

# Importar sistema de internacionalização
try:
    from i18n import t
except ImportError:
    def t(key):
        return key


class ColumnCleanerTool(ctk.CTkFrame):
    """Ferramenta para limpeza avançada de colunas com unidecode e normalização"""
    
    def __init__(self, parent, profile_manager):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.df = None
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
            text="🧹 Limpar Colunas",
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
        
        # Config de leitura
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
        
        self.enc_var = ctk.StringVar(value="auto")
        enc_menu = ctk.CTkOptionMenu(
            input_frame,
            values=["auto", "utf-8", "latin-1", "windows-1252"],
            variable=self.enc_var,
            width=120
        )
        enc_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # === Frame de Seleão de Colunas ===
        columns_frame = ctk.CTkFrame(self.scroll_container)
        columns_frame.pack(fill="x", padx=20, pady=10)
        
        columns_header = ctk.CTkFrame(columns_frame, fg_color="transparent")
        columns_header.pack(fill="x", padx=10, pady=10)
        
        columns_label = ctk.CTkLabel(
            columns_header,
            text="Colunas a Limpar:",
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
        
        self.columns_scroll = ctk.CTkScrollableFrame(columns_frame, height=100)
        self.columns_scroll.pack(fill="x", padx=10, pady=5)
        
        self.column_vars = {}
        
        # === Frame de Opões de Limpeza ===
        clean_frame = ctk.CTkFrame(self.scroll_container)
        clean_frame.pack(fill="x", padx=20, pady=10)
        
        clean_label = ctk.CTkLabel(
            clean_frame,
            text="Opões de Limpeza",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        clean_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        # Coluna 1
        self.uppercase_var = ctk.BooleanVar(value=True)
        uppercase_check = ctk.CTkCheckBox(
            clean_frame,
            text="Converter para MAIçÚSCULAS",
            variable=self.uppercase_var
        )
        uppercase_check.grid(row=1, column=0, padx=20, pady=8, sticky="w")
        
        self.remove_accents_var = ctk.BooleanVar(value=True)
        remove_accents_check = ctk.CTkCheckBox(
            clean_frame,
            text="Remover acentos (unidecode)",
            variable=self.remove_accents_var
        )
        remove_accents_check.grid(row=2, column=0, padx=20, pady=8, sticky="w")
        
        self.trim_var = ctk.BooleanVar(value=True)
        trim_check = ctk.CTkCheckBox(
            clean_frame,
            text="Trim (remover espaços)",
            variable=self.trim_var
        )
        trim_check.grid(row=3, column=0, padx=20, pady=8, sticky="w")
        
        # Coluna 2
        self.collapse_spaces_var = ctk.BooleanVar(value=True)
        collapse_check = ctk.CTkCheckBox(
            clean_frame,
            text="Colapsar espaços múltiplos",
            variable=self.collapse_spaces_var
        )
        collapse_check.grid(row=1, column=1, padx=40, pady=8, sticky="w")
        
        self.remove_special_var = ctk.BooleanVar(value=False)
        remove_special_check = ctk.CTkCheckBox(
            clean_frame,
            text="Remover caracteres especiais",
            variable=self.remove_special_var
        )
        remove_special_check.grid(row=2, column=1, padx=40, pady=8, sticky="w")
        
        self.fix_cedilla_var = ctk.BooleanVar(value=True)
        fix_cedilla_check = ctk.CTkCheckBox(
            clean_frame,
            text="Corrigir ç → C",
            variable=self.fix_cedilla_var
        )
        fix_cedilla_check.grid(row=3, column=1, padx=40, pady=8, sticky="w")
        
        # === Frame de Coluna de Destino ===
        dest_frame = ctk.CTkFrame(self.scroll_container)
        dest_frame.pack(fill="x", padx=20, pady=10)
        
        dest_label = ctk.CTkLabel(
            dest_frame,
            text="Coluna de Destino",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        dest_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        self.dest_mode_var = ctk.StringVar(value="replace")
        
        replace_radio = ctk.CTkRadioButton(
            dest_frame,
            text="Sobrescrever coluna original",
            variable=self.dest_mode_var,
            value="replace"
        )
        replace_radio.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        new_col_radio = ctk.CTkRadioButton(
            dest_frame,
            text="Criar nova coluna:",
            variable=self.dest_mode_var,
            value="new"
        )
        new_col_radio.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        self.new_col_entry = ctk.CTkEntry(dest_frame, width=200)
        self.new_col_entry.insert(0, "COLUNA_LIMPA")
        self.new_col_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        new_col_hint = ctk.CTkLabel(
            dest_frame,
            text="(se múltiplas colunas, adiciona sufixo _LIMPO)",
            text_color="gray50",
            font=ctk.CTkFont(size=11)
        )
        new_col_hint.grid(row=2, column=2, padx=10, pady=5, sticky="w")
        
        # === Frame de Saçida ===
        output_frame = ctk.CTkFrame(self.scroll_container)
        output_frame.pack(fill="x", padx=20, pady=10)
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="Arquivo de Saçida:",
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
            text="Carregue um arquivo para começar",
            text_color="gray50"
        )
        self.status_label.pack()
        
        # === Botão Executar ===
        self.btn_execute = ctk.CTkButton(
            self.scroll_container,
            text="▶️ Executar Limpeza",
            command=self.execute,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_execute.pack(pady=20)
        
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
        self.btn_add_workflow.pack(pady=(0, 20))
        
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
            self.columns = list(self.df.columns)
            
            self.update_column_checkboxes()
            
            # Sugerir saçida
            base = os.path.splitext(filepath)[0]
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, f"{base}_limpo.csv")
            
            self.status_label.configure(text=f"Arquivo carregado: {len(self.df)} linhas, {len(self.columns)} colunas")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
            
    def update_column_checkboxes(self):
        """Atualiza os checkboxes de colunas"""
        for widget in self.columns_scroll.winfo_children():
            widget.destroy()
        
        self.column_vars = {}
        
        for i, col in enumerate(self.columns):
            var = ctk.BooleanVar(value=False)
            self.column_vars[col] = var
            
            cb = ctk.CTkCheckBox(
                self.columns_scroll,
                text=str(col)[:35],
                variable=var,
                width=180
            )
            cb.grid(row=i//4, column=i%4, padx=8, pady=3, sticky="w")
            
    def select_all_columns(self):
        for var in self.column_vars.values():
            var.set(True)
            
    def deselect_all_columns(self):
        for var in self.column_vars.values():
            var.set(False)
            
    def browse_output(self):
        """Seleciona o arquivo de saçida"""
        file = filedialog.asksaveasfilename(
            title="Salvar como",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file)
    
    def clean_value(self, value):
        """Aplica todas as limpezas em um valor"""
        if pd.isna(value):
            return value
        
        text = str(value)
        
        # Corrigir cedilha antes de remover acentos
        if self.fix_cedilla_var.get():
            text = text.replace("ç", "C").replace("ç", "c")
        
        # Remover acentos (unidecode style)
        if self.remove_accents_var.get():
            text = unicodedata.normalize('NFD', text)
            text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Maiúsculas
        if self.uppercase_var.get():
            text = text.upper()
        
        # Trim
        if self.trim_var.get():
            text = text.strip()
        
        # Colapsar espaços
        if self.collapse_spaces_var.get():
            text = re.sub(r'\s+', ' ', text)
        
        # Remover caracteres especiais
        if self.remove_special_var.get():
            text = re.sub(r'[^\w\s\-.,;:@/\\]', '', text)
        
        return text
            
    def execute(self):
        """Executa a limpeza"""
        if self.df is None:
            messagebox.showwarning("Aviso", "Carregue um arquivo primeiro!")
            return
            
        output_file = self.output_entry.get()
        if not output_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo de saçida!")
            return
        
        # Verificar se hça colunas selecionadas
        selected_cols = [col for col, var in self.column_vars.items() if var.get()]
        if not selected_cols:
            messagebox.showwarning("Aviso", "Selecione ao menos uma coluna para limpar!")
            return
        
        thread = threading.Thread(target=self._execute_clean, args=(output_file, selected_cols))
        thread.start()
        
    def _execute_clean(self, output_file, selected_cols):
        """Executa a limpeza em thread"""
        try:
            self.btn_execute.configure(state="disabled")
            self.status_label.configure(text="Processando...")
            self.progress_bar.set(0.1)
            self.update()
            
            result_df = self.df.copy()
            total_cols = len(selected_cols)
            
            for i, col in enumerate(selected_cols):
                self.status_label.configure(text=f"Limpando coluna: {col}")
                self.update()
                
                if self.dest_mode_var.get() == "replace":
                    # Sobrescrever
                    result_df[col] = result_df[col].apply(self.clean_value)
                else:
                    # Nova coluna
                    if len(selected_cols) == 1:
                        new_col_name = self.new_col_entry.get()
                    else:
                        new_col_name = f"{col}_LIMPO"
                    
                    result_df[new_col_name] = result_df[col].apply(self.clean_value)
                
                progress = 0.1 + (0.7 * (i + 1) / total_cols)
                self.progress_bar.set(progress)
                self.update()
            
            self.status_label.configure(text="Salvando arquivo...")
            self.progress_bar.set(0.9)
            self.update()
            
            # Salvar
            sep = self.sep_var.get()
            if sep == "Tab":
                sep = "\t"
            
            result_df.to_csv(output_file, sep=sep, index=False, encoding='utf-8')
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Concluçido! {len(result_df)} linhas, {total_cols} colunas limpas")
            
            messagebox.showinfo(
                "Sucesso",
                f"Limpeza concluçida!\n\n"
                f"Linhas: {len(result_df)}\n"
                f"Colunas limpas: {total_cols}\n"
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
            "uppercase": self.uppercase_var.get(),
            "remove_accents": self.remove_accents_var.get(),
            "trim": self.trim_var.get(),
            "collapse_spaces": self.collapse_spaces_var.get(),
            "remove_special": self.remove_special_var.get(),
            "fix_cedilla": self.fix_cedilla_var.get(),
            "dest_mode": self.dest_mode_var.get(),
            "new_col_name": self.new_col_entry.get()
        }
        
    def load_settings(self, settings):
        """Carrega configurações de um perfil"""
        if "separator" in settings:
            self.sep_var.set(settings["separator"])
        if "encoding" in settings:
            self.enc_var.set(settings["encoding"])
        if "uppercase" in settings:
            self.uppercase_var.set(settings["uppercase"])
        if "remove_accents" in settings:
            self.remove_accents_var.set(settings["remove_accents"])
        if "trim" in settings:
            self.trim_var.set(settings["trim"])
        if "collapse_spaces" in settings:
            self.collapse_spaces_var.set(settings["collapse_spaces"])
        if "remove_special" in settings:
            self.remove_special_var.set(settings["remove_special"])
        if "fix_cedilla" in settings:
            self.fix_cedilla_var.set(settings["fix_cedilla"])
        if "dest_mode" in settings:
            self.dest_mode_var.set(settings["dest_mode"])
        if "new_col_name" in settings:
            self.new_col_entry.delete(0, "end")
            self.new_col_entry.insert(0, settings["new_col_name"])
            
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
                "column_cleaner",
                self.get_settings()
            )
            messagebox.showinfo("Sucesso", f"Perfil '{profile_name}' salvo!")

    def add_to_workflow(self):
        """Adiciona a configuração atual como etapa do workflow"""
        input_file = self.input_entry.get().strip()
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
            tool_id="column_cleaner",
            tool_name="🔧 " + t("tool_column_cleaner"),
            input_file=input_file if not use_previous else None,
            output_file=output_file,
            config=self.get_settings(),
            use_previous_output=use_previous
        )
        
        messagebox.showinfo(
            t("success"),
            f"{t('step_added_to_workflow')}\n{t('total_steps')}: {workflow_manager.get_step_count()}"
        )


