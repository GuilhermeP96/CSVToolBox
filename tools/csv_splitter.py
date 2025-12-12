# CSV Splitter Tool - Ferramenta para Dividir CSVs

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from pathlib import Path
import chardet


class CSVSplitterTool(ctk.CTkFrame):
    """Ferramenta para dividir arquivos CSV grandes em partes menores"""
    
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
            text="✂️ Dividir CSV",
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
        
        self.input_entry = ctk.CTkEntry(input_frame, width=450)
        self.input_entry.grid(row=0, column=1, padx=10, pady=15)
        
        btn_browse_input = ctk.CTkButton(
            input_frame,
            text="Procurar...",
            command=self.browse_input,
            width=100
        )
        btn_browse_input.grid(row=0, column=2, padx=10, pady=15)
        
        # Info do arquivo
        self.file_info_label = ctk.CTkLabel(
            input_frame,
            text="",
            text_color="gray50"
        )
        self.file_info_label.grid(row=0, column=3, padx=10, pady=15)
        
        # === Frame de Configurações de Origem ===
        origin_frame = ctk.CTkFrame(self)
        origin_frame.pack(fill="x", padx=20, pady=10)
        
        origin_label = ctk.CTkLabel(
            origin_frame,
            text="Configurações de Origem",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        origin_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        # Charset de origem
        charset_label = ctk.CTkLabel(origin_frame, text="Charset:", font=ctk.CTkFont(size=13))
        charset_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.charset_var = ctk.StringVar(value="auto")
        charset_menu = ctk.CTkOptionMenu(
            origin_frame,
            values=["auto", "utf-8", "latin-1", "windows-1252", "iso-8859-1"],
            variable=self.charset_var,
            width=140
        )
        charset_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Separador de origem
        sep_label = ctk.CTkLabel(origin_frame, text="Separador:", font=ctk.CTkFont(size=13))
        sep_label.grid(row=1, column=2, padx=20, pady=10, sticky="w")
        
        self.sep_var = ctk.StringVar(value="auto")
        sep_menu = ctk.CTkOptionMenu(
            origin_frame,
            values=["auto", ";", ",", "|", "Tab (\\t)"],
            variable=self.sep_var,
            width=120
        )
        sep_menu.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # === Frame de Divisão ===
        split_frame = ctk.CTkFrame(self)
        split_frame.pack(fill="x", padx=20, pady=10)
        
        split_label = ctk.CTkLabel(
            split_frame,
            text="Configurações de Divisão",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        split_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        # Máximo de registros por arquivo
        max_rows_label = ctk.CTkLabel(split_frame, text="Máx. registros por arquivo:", font=ctk.CTkFont(size=13))
        max_rows_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.max_rows_entry = ctk.CTkEntry(split_frame, width=150)
        self.max_rows_entry.insert(0, "100000")
        self.max_rows_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Presets de quantidade
        presets_label = ctk.CTkLabel(split_frame, text="Presets:", font=ctk.CTkFont(size=12), text_color="gray50")
        presets_label.grid(row=1, column=2, padx=(30, 5), pady=10, sticky="w")
        
        presets_frame = ctk.CTkFrame(split_frame, fg_color="transparent")
        presets_frame.grid(row=1, column=3, padx=5, pady=10, sticky="w")
        
        for text, value in [("10K", "10000"), ("50K", "50000"), ("100K", "100000"), ("500K", "500000"), ("1M", "1000000")]:
            btn = ctk.CTkButton(
                presets_frame,
                text=text,
                width=50,
                height=28,
                command=lambda v=value: self.set_max_rows(v)
            )
            btn.pack(side="left", padx=2)
        
        # === Frame de Configurações de Destino ===
        dest_frame = ctk.CTkFrame(self)
        dest_frame.pack(fill="x", padx=20, pady=10)
        
        dest_label = ctk.CTkLabel(
            dest_frame,
            text="Configurações de Destino",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        dest_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        # Charset de destino
        dest_charset_label = ctk.CTkLabel(dest_frame, text="Charset:", font=ctk.CTkFont(size=13))
        dest_charset_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.dest_charset_var = ctk.StringVar(value="utf-8")
        dest_charset_menu = ctk.CTkOptionMenu(
            dest_frame,
            values=["utf-8", "latin-1", "windows-1252", "iso-8859-1"],
            variable=self.dest_charset_var,
            width=140
        )
        dest_charset_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Separador de destino
        dest_sep_label = ctk.CTkLabel(dest_frame, text="Separador:", font=ctk.CTkFont(size=13))
        dest_sep_label.grid(row=1, column=2, padx=20, pady=10, sticky="w")
        
        self.dest_sep_var = ctk.StringVar(value=";")
        dest_sep_menu = ctk.CTkOptionMenu(
            dest_frame,
            values=[";", ",", "|", "Tab (\\t)"],
            variable=self.dest_sep_var,
            width=120
        )
        dest_sep_menu.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # === Frame de Formato de Dados ===
        format_frame = ctk.CTkFrame(self)
        format_frame.pack(fill="x", padx=20, pady=10)
        
        format_label = ctk.CTkLabel(
            format_frame,
            text="Formato de Dados",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        format_label.grid(row=0, column=0, columnspan=6, padx=20, pady=10, sticky="w")
        
        # Formato de dados
        data_format_label = ctk.CTkLabel(format_frame, text="Formato:", font=ctk.CTkFont(size=13))
        data_format_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.format_var = ctk.StringVar(value="Manter Original")
        format_menu = ctk.CTkOptionMenu(
            format_frame,
            values=["Manter Original", "BR", "EUA", "EU", "UK"],
            variable=self.format_var,
            command=self.on_format_change,
            width=150
        )
        format_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Exemplos de formato
        self.format_examples_label = ctk.CTkLabel(
            format_frame,
            text="",
            text_color="gray50",
            font=ctk.CTkFont(size=11)
        )
        self.format_examples_label.grid(row=1, column=2, columnspan=3, padx=20, pady=10, sticky="w")
        
        # Opções adicionais
        self.quote_all_var = ctk.BooleanVar(value=True)
        quote_all = ctk.CTkCheckBox(
            format_frame,
            text="Colocar aspas em todos os campos",
            variable=self.quote_all_var
        )
        quote_all.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="w")
        
        self.keep_header_var = ctk.BooleanVar(value=True)
        keep_header = ctk.CTkCheckBox(
            format_frame,
            text="Incluir cabeçalho em cada arquivo",
            variable=self.keep_header_var
        )
        keep_header.grid(row=2, column=2, columnspan=2, padx=20, pady=10, sticky="w")
        
        # === Frame de Saída ===
        output_frame = ctk.CTkFrame(self)
        output_frame.pack(fill="x", padx=20, pady=10)
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="Pasta de Saída:",
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
        
        # Prefixo do arquivo
        prefix_label = ctk.CTkLabel(output_frame, text="Prefixo:", font=ctk.CTkFont(size=13))
        prefix_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.prefix_entry = ctk.CTkEntry(output_frame, width=200)
        self.prefix_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        prefix_hint = ctk.CTkLabel(
            output_frame,
            text="Resultado: prefixo_1.csv, prefixo_2.csv, ...",
            text_color="gray50",
            font=ctk.CTkFont(size=11)
        )
        prefix_hint.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        
        # === Log de Processo ===
        log_frame = ctk.CTkFrame(self)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="Log do Processo:",
            font=ctk.CTkFont(size=12)
        )
        log_label.pack(anchor="w", padx=10, pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, height=100)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
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
            text="▶️ Executar Divisão",
            command=self.execute,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_execute.pack(pady=20)
        
    def set_max_rows(self, value):
        """Define o valor máximo de registros"""
        self.max_rows_entry.delete(0, "end")
        self.max_rows_entry.insert(0, value)
        
    def on_format_change(self, value):
        """Atualiza exemplos quando o formato muda"""
        examples = {
            "Manter Original": "Mantém os valores originais",
            "BR": "Decimal: 1.234,56 | Data: 31/12/2023 | Hora: 23:59",
            "EUA": "Decimal: 1,234.56 | Data: 12/31/2023 | Hora: 11:59 PM",
            "EU": "Decimal: 1 234,56 | Data: 2023-12-31 | Hora: 23:59",
            "UK": "Decimal: 1,234.56 | Data: 31-12-2023 | Hora: 23:59"
        }
        self.format_examples_label.configure(text=examples.get(value, ""))
        
    def browse_input(self):
        """Seleciona o arquivo de entrada"""
        file = filedialog.askopenfilename(
            title="Selecionar arquivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
            # Detectar configurações automaticamente
            self.detect_file_config(file)
            
            # Sugerir pasta e prefixo
            file_dir = os.path.dirname(file)
            file_name = os.path.splitext(os.path.basename(file))[0]
            
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, file_dir)
            
            self.prefix_entry.delete(0, "end")
            self.prefix_entry.insert(0, file_name)
            
    def detect_file_config(self, filepath):
        """Detecta charset e separador do arquivo"""
        try:
            # Detectar charset
            if self.charset_var.get() == "auto":
                with open(filepath, 'rb') as f:
                    result = chardet.detect(f.read(100000))
                    detected_charset = result['encoding']
                    self.charset_var.set(detected_charset or "utf-8")
            
            # Detectar separador
            if self.sep_var.get() == "auto":
                encoding = self.charset_var.get()
                with open(filepath, 'r', encoding=encoding) as f:
                    first_line = f.readline()
                
                separators = [',', ';', '\t', '|']
                detected_sep = max(separators, key=first_line.count)
                
                if detected_sep == '\t':
                    self.sep_var.set("Tab (\\t)")
                else:
                    self.sep_var.set(detected_sep)
            
            # Contar linhas
            with open(filepath, 'r', encoding=self.charset_var.get()) as f:
                line_count = sum(1 for _ in f) - 1  # -1 para cabeçalho
            
            self.file_info_label.configure(text=f"~{line_count:,} linhas")
            
        except Exception as e:
            self.log_text.insert("end", f"Erro na detecção: {str(e)}\n")
            
    def browse_output(self):
        """Seleciona a pasta de saída"""
        folder = filedialog.askdirectory(title="Selecionar pasta de saída")
        
        if folder:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, folder)
            
    def get_separator(self, sep_var):
        """Retorna o separador real"""
        sep = sep_var.get()
        if sep == "Tab (\\t)":
            return "\t"
        if sep == "auto":
            return ";"
        return sep
    
    def convert_data_format(self, df, target_format):
        """Converte dados para o formato alvo"""
        if target_format == "Manter Original":
            return df
        
        for col in df.columns:
            try:
                # Tentar converter datas
                if any(x in col.lower() for x in ['date', 'data', 'dt_', 'dat']):
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    
                    if target_format == "BR":
                        df[col] = df[col].dt.strftime('%d/%m/%Y')
                    elif target_format == "EUA":
                        df[col] = df[col].dt.strftime('%m/%d/%Y')
                    elif target_format == "EU":
                        df[col] = df[col].dt.strftime('%Y-%m-%d')
                    elif target_format == "UK":
                        df[col] = df[col].dt.strftime('%d-%m-%Y')
                else:
                    # Conversão de decimais
                    if target_format in ["BR", "EU"]:
                        df[col] = df[col].astype(str).str.replace(".", ",", regex=False)
                    elif target_format in ["EUA", "UK"]:
                        df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
            except Exception:
                pass
        
        return df
            
    def execute(self):
        """Executa a divisão do CSV"""
        input_file = self.input_entry.get()
        output_dir = self.output_entry.get()
        prefix = self.prefix_entry.get()
        
        if not input_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo de entrada!")
            return
            
        if not output_dir:
            messagebox.showwarning("Aviso", "Selecione uma pasta de saída!")
            return
            
        if not prefix:
            prefix = "parte"
        
        try:
            max_rows = int(self.max_rows_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Número máximo de registros inválido!")
            return
        
        try:
            self.btn_execute.configure(state="disabled")
            self.log_text.delete("1.0", "end")
            self.status_label.configure(text="Lendo arquivo...")
            self.progress_bar.set(0)
            self.update()
            
            # Ler arquivo
            sep = self.get_separator(self.sep_var)
            charset = self.charset_var.get()
            if charset == "auto":
                charset = "utf-8"
            
            self.log_text.insert("end", f"Lendo arquivo com charset={charset}, sep='{sep}'\n")
            self.update()
            
            df = pd.read_csv(input_file, sep=sep, encoding=charset, dtype=str, low_memory=False)
            
            total_rows = len(df)
            self.log_text.insert("end", f"Total de linhas: {total_rows:,}\n")
            
            # Aplicar formato de dados
            format_option = self.format_var.get()
            if format_option != "Manter Original":
                self.log_text.insert("end", f"Convertendo formato para: {format_option}\n")
                df = self.convert_data_format(df, format_option)
            
            # Calcular número de arquivos
            total_chunks = (total_rows // max_rows) + (1 if total_rows % max_rows != 0 else 0)
            self.log_text.insert("end", f"Arquivos a gerar: {total_chunks}\n\n")
            
            # Configurações de saída
            dest_sep = self.get_separator(self.dest_sep_var)
            dest_charset = self.dest_charset_var.get()
            quoting = 1 if self.quote_all_var.get() else 0  # csv.QUOTE_ALL ou csv.QUOTE_MINIMAL
            
            # Dividir e salvar
            file_count = 1
            for i in range(0, total_rows, max_rows):
                chunk = df.iloc[i:i + max_rows]
                
                output_file = os.path.join(output_dir, f"{prefix}_{file_count}.csv")
                
                chunk.to_csv(
                    output_file,
                    sep=dest_sep,
                    encoding=dest_charset,
                    index=False,
                    header=self.keep_header_var.get(),
                    quoting=quoting
                )
                
                self.log_text.insert("end", f"✓ Salvo: {os.path.basename(output_file)} ({len(chunk):,} linhas)\n")
                self.log_text.see("end")
                
                progress = file_count / total_chunks
                self.progress_bar.set(progress)
                self.status_label.configure(text=f"Processando arquivo {file_count}/{total_chunks}...")
                self.update()
                
                file_count += 1
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Concluído! {total_chunks} arquivos gerados.")
            
            self.log_text.insert("end", f"\n✅ Divisão concluída!\n")
            self.log_text.insert("end", f"Total: {total_chunks} arquivos em {output_dir}\n")
            
            messagebox.showinfo(
                "Sucesso",
                f"CSV dividido com sucesso!\n\n"
                f"Arquivos gerados: {total_chunks}\n"
                f"Linhas por arquivo: até {max_rows:,}\n"
                f"Pasta: {output_dir}"
            )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar: {str(e)}")
            self.log_text.insert("end", f"\n❌ Erro: {str(e)}\n")
            self.status_label.configure(text=f"Erro: {str(e)}")
        finally:
            self.btn_execute.configure(state="normal")
            
    def get_settings(self):
        """Retorna as configurações atuais"""
        return {
            "source_charset": self.charset_var.get(),
            "source_separator": self.sep_var.get(),
            "max_rows": self.max_rows_entry.get(),
            "dest_charset": self.dest_charset_var.get(),
            "dest_separator": self.dest_sep_var.get(),
            "data_format": self.format_var.get(),
            "quote_all": self.quote_all_var.get(),
            "keep_header": self.keep_header_var.get()
        }
        
    def load_settings(self, settings):
        """Carrega configurações de um perfil"""
        if "source_charset" in settings:
            self.charset_var.set(settings["source_charset"])
        if "source_separator" in settings:
            self.sep_var.set(settings["source_separator"])
        if "max_rows" in settings:
            self.max_rows_entry.delete(0, "end")
            self.max_rows_entry.insert(0, settings["max_rows"])
        if "dest_charset" in settings:
            self.dest_charset_var.set(settings["dest_charset"])
        if "dest_separator" in settings:
            self.dest_sep_var.set(settings["dest_separator"])
        if "data_format" in settings:
            self.format_var.set(settings["data_format"])
            self.on_format_change(settings["data_format"])
        if "quote_all" in settings:
            self.quote_all_var.set(settings["quote_all"])
        if "keep_header" in settings:
            self.keep_header_var.set(settings["keep_header"])
            
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
                "splitter",
                self.get_settings()
            )
            messagebox.showinfo("Sucesso", f"Perfil '{profile_name}' salvo!")
