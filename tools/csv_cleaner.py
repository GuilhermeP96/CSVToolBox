# CSV Cleaner Tool - Ferramenta para Limpar CSVs

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from pathlib import Path
import chardet
import re


class CSVCleanerTool(ctk.CTkFrame):
    """Ferramenta para limpar arquivos CSV - remover caracteres, aspas, espaços, etc."""
    
    def __init__(self, parent, profile_manager):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.input_file = None
        
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
            text="🧹 Limpar CSV",
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
            text="Arquivo de Entrada:",
            font=ctk.CTkFont(size=14)
        )
        input_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.input_entry = ctk.CTkEntry(input_frame, width=500)
        self.input_entry.grid(row=0, column=1, padx=10, pady=15)
        
        btn_browse_input = ctk.CTkButton(
            input_frame,
            text="Procurar...",
            command=self.browse_input,
            width=100
        )
        btn_browse_input.grid(row=0, column=2, padx=10, pady=15)
        
        # === Frame de Configurações de Leitura ===
        read_frame = ctk.CTkFrame(self.scroll_container)
        read_frame.pack(fill="x", padx=20, pady=10)
        
        read_label = ctk.CTkLabel(
            read_frame,
            text="Configurações de Leitura",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        read_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        # Separador
        sep_label = ctk.CTkLabel(read_frame, text="Separador:", font=ctk.CTkFont(size=13))
        sep_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.sep_var = ctk.StringVar(value=";")
        sep_menu = ctk.CTkOptionMenu(
            read_frame,
            values=[";", ",", "|", "Tab (\\t)"],
            variable=self.sep_var,
            width=120
        )
        sep_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Encoding
        enc_label = ctk.CTkLabel(read_frame, text="Encoding:", font=ctk.CTkFont(size=13))
        enc_label.grid(row=1, column=2, padx=20, pady=10, sticky="w")
        
        self.enc_var = ctk.StringVar(value="utf-8")
        enc_menu = ctk.CTkOptionMenu(
            read_frame,
            values=["utf-8", "latin-1", "windows-1252", "iso-8859-1", "auto-detect"],
            variable=self.enc_var,
            width=140
        )
        enc_menu.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # === Frame de Opções de Limpeza ===
        clean_frame = ctk.CTkFrame(self.scroll_container)
        clean_frame.pack(fill="x", padx=20, pady=10)
        
        clean_label = ctk.CTkLabel(
            clean_frame,
            text="Opções de Limpeza",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        clean_label.pack(pady=10, anchor="w", padx=20)
        
        options_grid = ctk.CTkFrame(clean_frame, fg_color="transparent")
        options_grid.pack(fill="x", padx=20, pady=10)
        
        # Coluna 1
        self.remove_quotes_var = ctk.BooleanVar(value=True)
        remove_quotes = ctk.CTkCheckBox(
            options_grid,
            text="Remover aspas (\", ')",
            variable=self.remove_quotes_var
        )
        remove_quotes.grid(row=0, column=0, padx=20, pady=8, sticky="w")
        
        self.remove_spaces_var = ctk.BooleanVar(value=True)
        remove_spaces = ctk.CTkCheckBox(
            options_grid,
            text="Remover espaços extras",
            variable=self.remove_spaces_var
        )
        remove_spaces.grid(row=1, column=0, padx=20, pady=8, sticky="w")
        
        self.remove_linebreaks_var = ctk.BooleanVar(value=False)
        remove_linebreaks = ctk.CTkCheckBox(
            options_grid,
            text="Remover quebras de linha",
            variable=self.remove_linebreaks_var
        )
        remove_linebreaks.grid(row=2, column=0, padx=20, pady=8, sticky="w")
        
        # Coluna 2
        self.remove_special_var = ctk.BooleanVar(value=False)
        remove_special = ctk.CTkCheckBox(
            options_grid,
            text="Remover caracteres especiais",
            variable=self.remove_special_var
        )
        remove_special.grid(row=0, column=1, padx=40, pady=8, sticky="w")
        
        self.trim_columns_var = ctk.BooleanVar(value=True)
        trim_columns = ctk.CTkCheckBox(
            options_grid,
            text="Trim em todas as colunas",
            variable=self.trim_columns_var
        )
        trim_columns.grid(row=1, column=1, padx=40, pady=8, sticky="w")
        
        self.remove_empty_rows_var = ctk.BooleanVar(value=False)
        remove_empty_rows = ctk.CTkCheckBox(
            options_grid,
            text="Remover linhas vazias",
            variable=self.remove_empty_rows_var
        )
        remove_empty_rows.grid(row=2, column=1, padx=40, pady=8, sticky="w")
        
        # === Frame de Substituição Customizada ===
        custom_frame = ctk.CTkFrame(self.scroll_container)
        custom_frame.pack(fill="x", padx=20, pady=10)
        
        self.custom_replace_var = ctk.BooleanVar(value=False)
        custom_check = ctk.CTkCheckBox(
            custom_frame,
            text="Substituição customizada:",
            variable=self.custom_replace_var,
            font=ctk.CTkFont(size=14)
        )
        custom_check.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        find_label = ctk.CTkLabel(custom_frame, text="Encontrar:", font=ctk.CTkFont(size=13))
        find_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.find_entry = ctk.CTkEntry(custom_frame, width=300)
        self.find_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        replace_label = ctk.CTkLabel(custom_frame, text="Substituir por:", font=ctk.CTkFont(size=13))
        replace_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        self.replace_entry = ctk.CTkEntry(custom_frame, width=300)
        self.replace_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        self.regex_var = ctk.BooleanVar(value=False)
        regex_check = ctk.CTkCheckBox(
            custom_frame,
            text="Usar Regex",
            variable=self.regex_var
        )
        regex_check.grid(row=1, column=2, padx=20, pady=5, sticky="w")
        
        # === Frame de Saída ===
        output_frame = ctk.CTkFrame(self.scroll_container)
        output_frame.pack(fill="x", padx=20, pady=10)
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="Arquivo de Saída:",
            font=ctk.CTkFont(size=14)
        )
        output_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.output_entry = ctk.CTkEntry(output_frame, width=500)
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
            text="Pronto para processar",
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
        
    def browse_input(self):
        """Seleciona o arquivo de entrada"""
        file = filedialog.askopenfilename(
            title="Selecionar arquivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
            # Sugerir nome de saída
            base = os.path.splitext(file)[0]
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, f"{base}_limpo.csv")
            
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
            
    def detect_encoding(self, filepath):
        """Detecta o encoding de um arquivo"""
        with open(filepath, 'rb') as f:
            raw = f.read(10000)
            result = chardet.detect(raw)
            return result['encoding']
            
    def get_separator(self):
        """Retorna o separador selecionado"""
        sep = self.sep_var.get()
        if sep == "Tab (\\t)":
            return "\t"
        return sep
    
    def clean_text(self, text):
        """Aplica as limpezas em um texto"""
        if pd.isna(text):
            return text
        
        text = str(text)
        
        # Remover aspas
        if self.remove_quotes_var.get():
            text = text.replace('"', '').replace("'", '')
        
        # Remover espaços extras
        if self.remove_spaces_var.get():
            text = ' '.join(text.split())
        
        # Remover quebras de linha
        if self.remove_linebreaks_var.get():
            text = text.replace('\n', ' ').replace('\r', '')
        
        # Remover caracteres especiais
        if self.remove_special_var.get():
            text = re.sub(r'[^\w\s\-.,;:@/\\]', '', text)
        
        # Trim
        if self.trim_columns_var.get():
            text = text.strip()
        
        return text
        
    def execute(self):
        """Executa a limpeza do CSV"""
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        
        if not input_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo de entrada!")
            return
            
        if not output_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo de saída!")
            return
        
        try:
            self.btn_execute.configure(state="disabled")
            self.status_label.configure(text="Lendo arquivo...")
            self.progress_bar.set(0.1)
            self.update()
            
            sep = self.get_separator()
            
            # Encoding
            if self.enc_var.get() == "auto-detect":
                encoding = self.detect_encoding(input_file)
            else:
                encoding = self.enc_var.get()
            
            # Ler arquivo
            df = pd.read_csv(
                input_file,
                sep=sep,
                encoding=encoding,
                low_memory=False,
                dtype=str  # Manter tudo como string para limpeza
            )
            
            self.status_label.configure(text="Aplicando limpeza...")
            self.progress_bar.set(0.3)
            self.update()
            
            # Aplicar limpeza em todas as colunas
            total_cols = len(df.columns)
            for i, col in enumerate(df.columns):
                df[col] = df[col].apply(self.clean_text)
                progress = 0.3 + (0.5 * (i + 1) / total_cols)
                self.progress_bar.set(progress)
                self.update()
            
            # Substituição customizada
            if self.custom_replace_var.get():
                find_text = self.find_entry.get()
                replace_text = self.replace_entry.get()
                
                if find_text:
                    self.status_label.configure(text="Aplicando substituição customizada...")
                    self.update()
                    
                    if self.regex_var.get():
                        df = df.replace(find_text, replace_text, regex=True)
                    else:
                        df = df.replace(find_text, replace_text)
            
            # Remover linhas vazias
            if self.remove_empty_rows_var.get():
                df = df.dropna(how='all')
            
            self.status_label.configure(text="Salvando arquivo...")
            self.progress_bar.set(0.9)
            self.update()
            
            # Salvar resultado
            df.to_csv(
                output_file,
                sep=sep,
                index=False,
                encoding=self.enc_var.get() if self.enc_var.get() != "auto-detect" else "utf-8"
            )
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Concluído! {len(df)} linhas processadas.")
            
            messagebox.showinfo(
                "Sucesso",
                f"Limpeza concluída!\n\n"
                f"Linhas processadas: {len(df)}\n"
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
            "remove_quotes": self.remove_quotes_var.get(),
            "remove_spaces": self.remove_spaces_var.get(),
            "remove_linebreaks": self.remove_linebreaks_var.get(),
            "remove_special": self.remove_special_var.get(),
            "trim_columns": self.trim_columns_var.get(),
            "remove_empty_rows": self.remove_empty_rows_var.get(),
            "custom_replace": self.custom_replace_var.get(),
            "find_text": self.find_entry.get(),
            "replace_text": self.replace_entry.get(),
            "use_regex": self.regex_var.get()
        }
        
    def load_settings(self, settings):
        """Carrega configurações de um perfil"""
        if "separator" in settings:
            self.sep_var.set(settings["separator"])
        if "encoding" in settings:
            self.enc_var.set(settings["encoding"])
        if "remove_quotes" in settings:
            self.remove_quotes_var.set(settings["remove_quotes"])
        if "remove_spaces" in settings:
            self.remove_spaces_var.set(settings["remove_spaces"])
        if "remove_linebreaks" in settings:
            self.remove_linebreaks_var.set(settings["remove_linebreaks"])
        if "remove_special" in settings:
            self.remove_special_var.set(settings["remove_special"])
        if "trim_columns" in settings:
            self.trim_columns_var.set(settings["trim_columns"])
        if "remove_empty_rows" in settings:
            self.remove_empty_rows_var.set(settings["remove_empty_rows"])
        if "custom_replace" in settings:
            self.custom_replace_var.set(settings["custom_replace"])
        if "find_text" in settings:
            self.find_entry.delete(0, "end")
            self.find_entry.insert(0, settings["find_text"])
        if "replace_text" in settings:
            self.replace_entry.delete(0, "end")
            self.replace_entry.insert(0, settings["replace_text"])
        if "use_regex" in settings:
            self.regex_var.set(settings["use_regex"])
            
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
                "cleaner",
                self.get_settings()
            )
            messagebox.showinfo("Sucesso", f"Perfil '{profile_name}' salvo!")


