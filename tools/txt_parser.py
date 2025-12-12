# TXT Parser Tool - Ferramenta para Converter TXT para CSV

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import re
import chardet
import threading


class TxtParserTool(ctk.CTkFrame):
    """Ferramenta para converter arquivos TXT em CSV"""
    
    def __init__(self, parent, profile_manager):
        super().__init__(parent)
        self.profile_manager = profile_manager
        
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
            text="📝 TXT para CSV",
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
            text="Arquivo TXT:",
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
        
        # === Frame de Tipo de Arquivo ===
        type_frame = ctk.CTkFrame(self.scroll_container)
        type_frame.pack(fill="x", padx=20, pady=10)
        
        type_label = ctk.CTkLabel(
            type_frame,
            text="Tipo de Arquivo TXT",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        type_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        self.file_type_var = ctk.StringVar(value="delimited")
        
        delimited_radio = ctk.CTkRadioButton(
            type_frame,
            text="Delimitado (separador)",
            variable=self.file_type_var,
            value="delimited",
            command=self.toggle_options
        )
        delimited_radio.grid(row=1, column=0, padx=20, pady=8, sticky="w")
        
        fixed_radio = ctk.CTkRadioButton(
            type_frame,
            text="Largura Fixa",
            variable=self.file_type_var,
            value="fixed",
            command=self.toggle_options
        )
        fixed_radio.grid(row=1, column=1, padx=40, pady=8, sticky="w")
        
        regex_radio = ctk.CTkRadioButton(
            type_frame,
            text="Regex (padrão)",
            variable=self.file_type_var,
            value="regex",
            command=self.toggle_options
        )
        regex_radio.grid(row=1, column=2, padx=40, pady=8, sticky="w")
        
        # === Frame Opções Delimitado ===
        self.delimited_frame = ctk.CTkFrame(self.scroll_container)
        self.delimited_frame.pack(fill="x", padx=20, pady=10)
        
        sep_label = ctk.CTkLabel(
            self.delimited_frame,
            text="Separador:",
            font=ctk.CTkFont(size=14)
        )
        sep_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.sep_var = ctk.StringVar(value="|")
        sep_menu = ctk.CTkOptionMenu(
            self.delimited_frame,
            values=["|", ";", ",", "Tab", "Espaço", "Outro"],
            variable=self.sep_var,
            width=100
        )
        sep_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        custom_sep_label = ctk.CTkLabel(
            self.delimited_frame,
            text="Outro:",
            font=ctk.CTkFont(size=12)
        )
        custom_sep_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        self.custom_sep_entry = ctk.CTkEntry(self.delimited_frame, width=50)
        self.custom_sep_entry.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # === Frame Opções Largura Fixa ===
        self.fixed_frame = ctk.CTkFrame(self.scroll_container)
        
        fixed_label = ctk.CTkLabel(
            self.fixed_frame,
            text="Posições das Colunas (ex: 0-10, 10-25, 25-50):",
            font=ctk.CTkFont(size=14)
        )
        fixed_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.positions_entry = ctk.CTkEntry(self.fixed_frame, width=400)
        self.positions_entry.insert(0, "0-10, 10-20, 20-30")
        self.positions_entry.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        positions_hint = ctk.CTkLabel(
            self.fixed_frame,
            text="Separe os ranges com vírgula. Exemplo: 0-5, 5-15, 15-30, 30-50",
            text_color="gray50",
            font=ctk.CTkFont(size=11)
        )
        positions_hint.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        # === Frame Opções Regex ===
        self.regex_frame = ctk.CTkFrame(self.scroll_container)
        
        regex_label = ctk.CTkLabel(
            self.regex_frame,
            text="Padrão Regex:",
            font=ctk.CTkFont(size=14)
        )
        regex_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.regex_entry = ctk.CTkEntry(self.regex_frame, width=500)
        self.regex_entry.insert(0, r"(\d+)\s+(\w+)\s+(.*)")
        self.regex_entry.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        regex_hint = ctk.CTkLabel(
            self.regex_frame,
            text="Use grupos de captura () para definir colunas. Ex: (\\d+)\\s+(\\w+)",
            text_color="gray50",
            font=ctk.CTkFont(size=11)
        )
        regex_hint.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        # === Frame de Configurações ===
        config_frame = ctk.CTkFrame(self.scroll_container)
        config_frame.pack(fill="x", padx=20, pady=10)
        
        config_label = ctk.CTkLabel(
            config_frame,
            text="Configurações",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        config_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        # Coluna 1
        enc_label = ctk.CTkLabel(config_frame, text="Encoding:", font=ctk.CTkFont(size=12))
        enc_label.grid(row=1, column=0, padx=20, pady=8, sticky="w")
        
        self.enc_var = ctk.StringVar(value="auto")
        enc_menu = ctk.CTkOptionMenu(
            config_frame,
            values=["auto", "utf-8", "latin-1", "windows-1252", "ascii"],
            variable=self.enc_var,
            width=130
        )
        enc_menu.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        
        # Coluna 2
        self.has_header_var = ctk.BooleanVar(value=False)
        has_header_check = ctk.CTkCheckBox(
            config_frame,
            text="Primeira linha é cabeçalho",
            variable=self.has_header_var
        )
        has_header_check.grid(row=1, column=2, padx=30, pady=8, sticky="w")
        
        # Linha 2
        header_names_label = ctk.CTkLabel(
            config_frame,
            text="Nomes das Colunas:",
            font=ctk.CTkFont(size=12)
        )
        header_names_label.grid(row=2, column=0, padx=20, pady=8, sticky="w")
        
        self.header_names_entry = ctk.CTkEntry(config_frame, width=400)
        self.header_names_entry.insert(0, "Coluna1, Coluna2, Coluna3")
        self.header_names_entry.grid(row=2, column=1, columnspan=3, padx=10, pady=8, sticky="w")
        
        header_hint = ctk.CTkLabel(
            config_frame,
            text="Separe os nomes com vírgula. Deixe vazio para usar Col1, Col2...",
            text_color="gray50",
            font=ctk.CTkFont(size=11)
        )
        header_hint.grid(row=3, column=1, columnspan=3, padx=10, pady=2, sticky="w")
        
        # Opções adicionais
        self.skip_empty_var = ctk.BooleanVar(value=True)
        skip_empty_check = ctk.CTkCheckBox(
            config_frame,
            text="Ignorar linhas vazias",
            variable=self.skip_empty_var
        )
        skip_empty_check.grid(row=4, column=0, padx=20, pady=8, sticky="w")
        
        self.skip_comments_var = ctk.BooleanVar(value=False)
        skip_comments_check = ctk.CTkCheckBox(
            config_frame,
            text="Ignorar linhas com #",
            variable=self.skip_comments_var
        )
        skip_comments_check.grid(row=4, column=1, padx=10, pady=8, sticky="w")
        
        skip_lines_label = ctk.CTkLabel(
            config_frame,
            text="Pular linhas iniciais:",
            font=ctk.CTkFont(size=12)
        )
        skip_lines_label.grid(row=4, column=2, padx=20, pady=8, sticky="w")
        
        self.skip_lines_entry = ctk.CTkEntry(config_frame, width=60)
        self.skip_lines_entry.insert(0, "0")
        self.skip_lines_entry.grid(row=4, column=3, padx=10, pady=8, sticky="w")
        
        # === Frame de Saída ===
        output_frame = ctk.CTkFrame(self.scroll_container)
        output_frame.pack(fill="x", padx=20, pady=10)
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="Arquivo de Saída:",
            font=ctk.CTkFont(size=14)
        )
        output_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        self.output_entry = ctk.CTkEntry(output_frame, width=400)
        self.output_entry.grid(row=0, column=1, padx=10, pady=15)
        
        btn_browse_output = ctk.CTkButton(
            output_frame,
            text="Procurar...",
            command=self.browse_output,
            width=100
        )
        btn_browse_output.grid(row=0, column=2, padx=10, pady=15)
        
        out_sep_label = ctk.CTkLabel(output_frame, text="Separador CSV:", font=ctk.CTkFont(size=12))
        out_sep_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.out_sep_var = ctk.StringVar(value=";")
        out_sep_menu = ctk.CTkOptionMenu(
            output_frame,
            values=[";", ",", "|", "Tab"],
            variable=self.out_sep_var,
            width=80
        )
        out_sep_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # === Barra de Progresso ===
        self.progress_frame = ctk.CTkFrame(self.scroll_container)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=500)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Selecione um arquivo TXT para converter",
            text_color="gray50"
        )
        self.status_label.pack()
        
        # === Botão Executar ===
        self.btn_execute = ctk.CTkButton(
            self.scroll_container,
            text="▶️ Converter para CSV",
            command=self.execute,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_execute.pack(pady=20)
        
    def toggle_options(self):
        """Mostra/esconde frames de opções baseado no tipo selecionado"""
        # Esconder todos
        self.delimited_frame.pack_forget()
        self.fixed_frame.pack_forget()
        self.regex_frame.pack_forget()
        
        file_type = self.file_type_var.get()
        
        # Reposicionar frames
        if file_type == "delimited":
            self.delimited_frame.pack(fill="x", padx=20, pady=10, after=self.winfo_children()[2])
        elif file_type == "fixed":
            self.fixed_frame.pack(fill="x", padx=20, pady=10, after=self.winfo_children()[2])
        elif file_type == "regex":
            self.regex_frame.pack(fill="x", padx=20, pady=10, after=self.winfo_children()[2])
            
    def browse_input(self):
        """Seleciona o arquivo de entrada"""
        file = filedialog.askopenfilename(
            title="Selecionar arquivo TXT",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
            # Sugerir arquivo de saída
            base = os.path.splitext(file)[0]
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, f"{base}.csv")
            
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
        """Retorna o separador do TXT"""
        sep = self.sep_var.get()
        if sep == "Tab":
            return "\t"
        elif sep == "Espaço":
            return " "
        elif sep == "Outro":
            return self.custom_sep_entry.get() or "|"
        return sep
    
    def parse_positions(self):
        """Parseia as posições de largura fixa"""
        positions_str = self.positions_entry.get().strip()
        positions = []
        
        for part in positions_str.split(","):
            part = part.strip()
            if "-" in part:
                start, end = map(int, part.split("-"))
                positions.append((start, end))
        
        return positions
    
    def parse_delimited(self, lines, sep):
        """Parseia arquivo delimitado"""
        data = []
        for line in lines:
            parts = line.split(sep)
            data.append([p.strip() for p in parts])
        return data
    
    def parse_fixed_width(self, lines, positions):
        """Parseia arquivo com largura fixa"""
        data = []
        for line in lines:
            row = []
            for start, end in positions:
                value = line[start:end].strip() if len(line) > start else ""
                row.append(value)
            data.append(row)
        return data
    
    def parse_regex(self, lines, pattern):
        """Parseia arquivo com regex"""
        data = []
        regex = re.compile(pattern)
        for line in lines:
            match = regex.match(line)
            if match:
                data.append(list(match.groups()))
        return data
            
    def execute(self):
        """Executa a conversão"""
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        
        if not input_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo TXT!")
            return
        
        if not output_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo de saída!")
            return
        
        thread = threading.Thread(target=self._execute_convert, args=(input_file, output_file))
        thread.start()
        
    def _execute_convert(self, input_file, output_file):
        """Executa a conversão em thread"""
        try:
            self.btn_execute.configure(state="disabled")
            self.status_label.configure(text="Lendo arquivo...")
            self.progress_bar.set(0.1)
            self.update()
            
            # Detectar encoding
            enc = self.enc_var.get()
            if enc == "auto":
                with open(input_file, 'rb') as f:
                    result = chardet.detect(f.read(10000))
                    enc = result['encoding'] or 'utf-8'
            
            # Ler arquivo
            with open(input_file, 'r', encoding=enc, errors='replace') as f:
                lines = f.readlines()
            
            self.status_label.configure(text=f"Processando {len(lines)} linhas...")
            self.progress_bar.set(0.3)
            self.update()
            
            # Pular linhas iniciais
            skip_lines = int(self.skip_lines_entry.get() or 0)
            lines = lines[skip_lines:]
            
            # Filtrar linhas
            if self.skip_empty_var.get():
                lines = [l for l in lines if l.strip()]
            
            if self.skip_comments_var.get():
                lines = [l for l in lines if not l.strip().startswith("#")]
            
            # Remover newlines
            lines = [l.rstrip('\n\r') for l in lines]
            
            # Parsear baseado no tipo
            file_type = self.file_type_var.get()
            
            if file_type == "delimited":
                sep = self.get_separator()
                data = self.parse_delimited(lines, sep)
            elif file_type == "fixed":
                positions = self.parse_positions()
                data = self.parse_fixed_width(lines, positions)
            else:  # regex
                pattern = self.regex_entry.get()
                data = self.parse_regex(lines, pattern)
            
            self.status_label.configure(text="Criando DataFrame...")
            self.progress_bar.set(0.6)
            self.update()
            
            # Definir cabeçalho
            header_names = self.header_names_entry.get().strip()
            
            if self.has_header_var.get() and data:
                columns = data[0]
                data = data[1:]
            elif header_names:
                columns = [c.strip() for c in header_names.split(",")]
            else:
                max_cols = max(len(row) for row in data) if data else 1
                columns = [f"Col{i+1}" for i in range(max_cols)]
            
            # Ajustar número de colunas
            for i, row in enumerate(data):
                while len(row) < len(columns):
                    row.append("")
                data[i] = row[:len(columns)]
            
            # Criar DataFrame
            df = pd.DataFrame(data, columns=columns[:len(columns)])
            
            self.status_label.configure(text="Salvando CSV...")
            self.progress_bar.set(0.8)
            self.update()
            
            # Salvar
            out_sep = self.out_sep_var.get()
            if out_sep == "Tab":
                out_sep = "\t"
            
            df.to_csv(output_file, sep=out_sep, index=False, encoding='utf-8')
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Concluído! {len(df)} linhas, {len(df.columns)} colunas")
            
            messagebox.showinfo(
                "Sucesso",
                f"Conversão concluída!\n\n"
                f"Linhas: {len(df)}\n"
                f"Colunas: {len(df.columns)}\n"
                f"Arquivo: {output_file}"
            )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao converter: {str(e)}")
            self.status_label.configure(text=f"Erro: {str(e)}")
        finally:
            self.btn_execute.configure(state="normal")
            
    def get_settings(self):
        """Retorna as configurações atuais"""
        return {
            "file_type": self.file_type_var.get(),
            "separator": self.sep_var.get(),
            "custom_separator": self.custom_sep_entry.get(),
            "positions": self.positions_entry.get(),
            "regex_pattern": self.regex_entry.get(),
            "encoding": self.enc_var.get(),
            "has_header": self.has_header_var.get(),
            "header_names": self.header_names_entry.get(),
            "skip_empty": self.skip_empty_var.get(),
            "skip_comments": self.skip_comments_var.get(),
            "skip_lines": self.skip_lines_entry.get(),
            "output_separator": self.out_sep_var.get()
        }
        
    def load_settings(self, settings):
        """Carrega configurações de um perfil"""
        if "file_type" in settings:
            self.file_type_var.set(settings["file_type"])
        if "separator" in settings:
            self.sep_var.set(settings["separator"])
        if "custom_separator" in settings:
            self.custom_sep_entry.delete(0, "end")
            self.custom_sep_entry.insert(0, settings["custom_separator"])
        if "positions" in settings:
            self.positions_entry.delete(0, "end")
            self.positions_entry.insert(0, settings["positions"])
        if "regex_pattern" in settings:
            self.regex_entry.delete(0, "end")
            self.regex_entry.insert(0, settings["regex_pattern"])
        if "encoding" in settings:
            self.enc_var.set(settings["encoding"])
        if "has_header" in settings:
            self.has_header_var.set(settings["has_header"])
        if "header_names" in settings:
            self.header_names_entry.delete(0, "end")
            self.header_names_entry.insert(0, settings["header_names"])
        if "skip_empty" in settings:
            self.skip_empty_var.set(settings["skip_empty"])
        if "skip_comments" in settings:
            self.skip_comments_var.set(settings["skip_comments"])
        if "skip_lines" in settings:
            self.skip_lines_entry.delete(0, "end")
            self.skip_lines_entry.insert(0, settings["skip_lines"])
        if "output_separator" in settings:
            self.out_sep_var.set(settings["output_separator"])
        
        self.toggle_options()
            
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
                "txt_parser",
                self.get_settings()
            )
            messagebox.showinfo("Sucesso", f"Perfil '{profile_name}' salvo!")


