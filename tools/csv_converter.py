# CSV Converter Tool - Ferramenta para Converter Formatos

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from pathlib import Path
import chardet
import json
import xml.etree.ElementTree as ET


class CSVConverterTool(ctk.CTkFrame):
    """Ferramenta para converter entre formatos CSV, XLSX, JSON, XML, TXT"""
    
    def __init__(self, parent, profile_manager):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.input_file = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Cria os widgets da ferramenta"""
        
        # === Cabeçalho ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            header,
            text="🔄 Converter Formato",
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
            text="Arquivo de Entrada:",
            font=ctk.CTkFont(size=14)
        )
        input_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.input_entry = ctk.CTkEntry(input_frame, width=450)
        self.input_entry.grid(row=0, column=1, padx=10, pady=15)
        
        btn_browse_input = ctk.CTkButton(
            input_frame,
            text="Procurar...",
            command=self.browse_input,
            width=100
        )
        btn_browse_input.grid(row=0, column=2, padx=10, pady=15)
        
        # Formato de entrada detectado
        self.input_format_label = ctk.CTkLabel(
            input_frame,
            text="Formato: -",
            text_color="gray50"
        )
        self.input_format_label.grid(row=0, column=3, padx=20, pady=15)
        
        # === Frame de Configurações de Entrada ===
        input_config = ctk.CTkFrame(self)
        input_config.pack(fill="x", padx=20, pady=10)
        
        input_config_label = ctk.CTkLabel(
            input_config,
            text="Configurações de Leitura (para CSV/TXT)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        input_config_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        # Separador de entrada
        sep_in_label = ctk.CTkLabel(input_config, text="Separador:", font=ctk.CTkFont(size=13))
        sep_in_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.sep_in_var = ctk.StringVar(value=";")
        sep_in_menu = ctk.CTkOptionMenu(
            input_config,
            values=[";", ",", "|", "Tab (\\t)", "Espaço"],
            variable=self.sep_in_var,
            width=120
        )
        sep_in_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Encoding de entrada
        enc_in_label = ctk.CTkLabel(input_config, text="Encoding:", font=ctk.CTkFont(size=13))
        enc_in_label.grid(row=1, column=2, padx=20, pady=10, sticky="w")
        
        self.enc_in_var = ctk.StringVar(value="utf-8")
        enc_in_menu = ctk.CTkOptionMenu(
            input_config,
            values=["utf-8", "latin-1", "windows-1252", "iso-8859-1", "auto-detect"],
            variable=self.enc_in_var,
            width=140
        )
        enc_in_menu.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # Tem cabeçalho
        self.has_header_var = ctk.BooleanVar(value=True)
        has_header = ctk.CTkCheckBox(
            input_config,
            text="Primeira linha é cabeçalho",
            variable=self.has_header_var
        )
        has_header.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="w")
        
        # === Frame de Formato de Saída ===
        output_format_frame = ctk.CTkFrame(self)
        output_format_frame.pack(fill="x", padx=20, pady=10)
        
        output_format_label = ctk.CTkLabel(
            output_format_frame,
            text="Formato de Saída",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        output_format_label.pack(pady=10, anchor="w", padx=20)
        
        # Botões de formato
        formats_frame = ctk.CTkFrame(output_format_frame, fg_color="transparent")
        formats_frame.pack(fill="x", padx=20, pady=10)
        
        self.format_var = ctk.StringVar(value="csv")
        formats = [
            ("CSV", "csv"),
            ("Excel (XLSX)", "xlsx"),
            ("JSON", "json"),
            ("XML", "xml"),
            ("TXT", "txt")
        ]
        
        for i, (text, value) in enumerate(formats):
            btn = ctk.CTkRadioButton(
                formats_frame,
                text=text,
                variable=self.format_var,
                value=value,
                command=self.on_format_change
            )
            btn.grid(row=0, column=i, padx=20, pady=10)
        
        # === Frame de Configurações de Saída ===
        self.output_config = ctk.CTkFrame(self)
        self.output_config.pack(fill="x", padx=20, pady=10)
        
        output_config_label = ctk.CTkLabel(
            self.output_config,
            text="Configurações de Saída",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        output_config_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        # Separador de saída (para CSV/TXT)
        self.sep_out_label = ctk.CTkLabel(self.output_config, text="Separador:", font=ctk.CTkFont(size=13))
        self.sep_out_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.sep_out_var = ctk.StringVar(value=";")
        self.sep_out_menu = ctk.CTkOptionMenu(
            self.output_config,
            values=[";", ",", "|", "Tab (\\t)"],
            variable=self.sep_out_var,
            width=120
        )
        self.sep_out_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Encoding de saída
        self.enc_out_label = ctk.CTkLabel(self.output_config, text="Encoding:", font=ctk.CTkFont(size=13))
        self.enc_out_label.grid(row=1, column=2, padx=20, pady=10, sticky="w")
        
        self.enc_out_var = ctk.StringVar(value="utf-8")
        self.enc_out_menu = ctk.CTkOptionMenu(
            self.output_config,
            values=["utf-8", "latin-1", "windows-1252", "iso-8859-1"],
            variable=self.enc_out_var,
            width=140
        )
        self.enc_out_menu.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # Incluir cabeçalho
        self.include_header_var = ctk.BooleanVar(value=True)
        self.include_header_check = ctk.CTkCheckBox(
            self.output_config,
            text="Incluir cabeçalho",
            variable=self.include_header_var
        )
        self.include_header_check.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="w")
        
        # Incluir índice
        self.include_index_var = ctk.BooleanVar(value=False)
        self.include_index_check = ctk.CTkCheckBox(
            self.output_config,
            text="Incluir índice",
            variable=self.include_index_var
        )
        self.include_index_check.grid(row=2, column=2, columnspan=2, padx=20, pady=10, sticky="w")
        
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
            text="Pronto para processar",
            text_color="gray50"
        )
        self.status_label.pack()
        
        # === Botão Executar ===
        self.btn_execute = ctk.CTkButton(
            self,
            text="▶️ Executar Conversão",
            command=self.execute,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_execute.pack(pady=20)
        
    def on_format_change(self):
        """Atualiza opções baseado no formato selecionado"""
        format_type = self.format_var.get()
        
        # Habilitar/desabilitar opções conforme formato
        if format_type in ["csv", "txt"]:
            self.sep_out_menu.configure(state="normal")
        else:
            self.sep_out_menu.configure(state="disabled")
        
        # Atualizar sugestão de arquivo de saída
        input_file = self.input_entry.get()
        if input_file:
            base = os.path.splitext(input_file)[0]
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, f"{base}.{format_type}")
        
    def browse_input(self):
        """Seleciona o arquivo de entrada"""
        file = filedialog.askopenfilename(
            title="Selecionar arquivo",
            filetypes=[
                ("All supported", "*.csv;*.xlsx;*.xls;*.json;*.xml;*.txt"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx;*.xls"),
                ("JSON files", "*.json"),
                ("XML files", "*.xml"),
                ("TXT files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
            # Detectar formato
            ext = os.path.splitext(file)[1].lower()
            format_map = {
                '.csv': 'CSV',
                '.xlsx': 'Excel',
                '.xls': 'Excel',
                '.json': 'JSON',
                '.xml': 'XML',
                '.txt': 'TXT'
            }
            self.input_format_label.configure(text=f"Formato: {format_map.get(ext, 'Desconhecido')}")
            
            # Sugerir nome de saída
            base = os.path.splitext(file)[0]
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, f"{base}.{self.format_var.get()}")
            
    def browse_output(self):
        """Seleciona o arquivo de saída"""
        format_type = self.format_var.get()
        filetypes = [("All files", "*.*")]
        
        if format_type == "csv":
            filetypes = [("CSV files", "*.csv")]
            default_ext = ".csv"
        elif format_type == "xlsx":
            filetypes = [("Excel files", "*.xlsx")]
            default_ext = ".xlsx"
        elif format_type == "json":
            filetypes = [("JSON files", "*.json")]
            default_ext = ".json"
        elif format_type == "xml":
            filetypes = [("XML files", "*.xml")]
            default_ext = ".xml"
        else:
            filetypes = [("TXT files", "*.txt")]
            default_ext = ".txt"
        
        file = filedialog.asksaveasfilename(
            title="Salvar como",
            defaultextension=default_ext,
            filetypes=filetypes
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
            
    def get_separator(self, sep_var):
        """Retorna o separador selecionado"""
        sep = sep_var.get()
        if sep == "Tab (\\t)":
            return "\t"
        elif sep == "Espaço":
            return " "
        return sep
    
    def read_input_file(self, filepath):
        """Lê o arquivo de entrada em um DataFrame"""
        ext = os.path.splitext(filepath)[1].lower()
        
        # Encoding
        if self.enc_in_var.get() == "auto-detect":
            encoding = self.detect_encoding(filepath)
        else:
            encoding = self.enc_in_var.get()
        
        if ext in ['.csv', '.txt']:
            sep = self.get_separator(self.sep_in_var)
            header = 0 if self.has_header_var.get() else None
            return pd.read_csv(filepath, sep=sep, encoding=encoding, header=header, low_memory=False)
        
        elif ext in ['.xlsx', '.xls']:
            header = 0 if self.has_header_var.get() else None
            return pd.read_excel(filepath, header=header)
        
        elif ext == '.json':
            return pd.read_json(filepath, encoding=encoding)
        
        elif ext == '.xml':
            return pd.read_xml(filepath, encoding=encoding)
        
        else:
            raise ValueError(f"Formato não suportado: {ext}")
    
    def save_output_file(self, df, filepath):
        """Salva o DataFrame no formato de saída"""
        format_type = self.format_var.get()
        encoding = self.enc_out_var.get()
        index = self.include_index_var.get()
        
        if format_type == "csv":
            sep = self.get_separator(self.sep_out_var)
            header = self.include_header_var.get()
            df.to_csv(filepath, sep=sep, encoding=encoding, index=index, header=header)
        
        elif format_type == "txt":
            sep = self.get_separator(self.sep_out_var)
            header = self.include_header_var.get()
            df.to_csv(filepath, sep=sep, encoding=encoding, index=index, header=header)
        
        elif format_type == "xlsx":
            df.to_excel(filepath, index=index, header=self.include_header_var.get())
        
        elif format_type == "json":
            df.to_json(filepath, orient='records', force_ascii=False, indent=2)
        
        elif format_type == "xml":
            df.to_xml(filepath, index=index)
        
    def execute(self):
        """Executa a conversão"""
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
            self.status_label.configure(text="Lendo arquivo de entrada...")
            self.progress_bar.set(0.2)
            self.update()
            
            # Ler arquivo
            df = self.read_input_file(input_file)
            
            self.status_label.configure(text="Convertendo...")
            self.progress_bar.set(0.6)
            self.update()
            
            # Salvar no formato de saída
            self.status_label.configure(text="Salvando arquivo...")
            self.progress_bar.set(0.8)
            self.update()
            
            self.save_output_file(df, output_file)
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Concluído! {len(df)} linhas convertidas.")
            
            messagebox.showinfo(
                "Sucesso",
                f"Conversão concluída!\n\n"
                f"Linhas: {len(df)}\n"
                f"Formato: {self.format_var.get().upper()}\n"
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
            "input_separator": self.sep_in_var.get(),
            "input_encoding": self.enc_in_var.get(),
            "has_header": self.has_header_var.get(),
            "output_format": self.format_var.get(),
            "output_separator": self.sep_out_var.get(),
            "output_encoding": self.enc_out_var.get(),
            "include_header": self.include_header_var.get(),
            "include_index": self.include_index_var.get()
        }
        
    def load_settings(self, settings):
        """Carrega configurações de um perfil"""
        if "input_separator" in settings:
            self.sep_in_var.set(settings["input_separator"])
        if "input_encoding" in settings:
            self.enc_in_var.set(settings["input_encoding"])
        if "has_header" in settings:
            self.has_header_var.set(settings["has_header"])
        if "output_format" in settings:
            self.format_var.set(settings["output_format"])
            self.on_format_change()
        if "output_separator" in settings:
            self.sep_out_var.set(settings["output_separator"])
        if "output_encoding" in settings:
            self.enc_out_var.set(settings["output_encoding"])
        if "include_header" in settings:
            self.include_header_var.set(settings["include_header"])
        if "include_index" in settings:
            self.include_index_var.set(settings["include_index"])
            
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
                "converter",
                self.get_settings()
            )
            messagebox.showinfo("Sucesso", f"Perfil '{profile_name}' salvo!")
