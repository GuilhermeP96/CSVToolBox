# CSV Merger Tool - Ferramenta para Consolidar CSVs

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from pathlib import Path
import chardet


class CSVMergerTool(ctk.CTkFrame):
    """Ferramenta para consolidar múltiplos arquivos CSV em um único arquivo"""
    
    def __init__(self, parent, profile_manager):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.selected_files = []
        
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
            text="📊 Consolidar CSVs",
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
        
        # === Frame de Configurações ===
        config_frame = ctk.CTkFrame(self.scroll_container)
        config_frame.pack(fill="x", padx=20, pady=10)
        
        # Grid de configurações
        config_frame.columnconfigure(1, weight=1)
        
        # Separador
        sep_label = ctk.CTkLabel(config_frame, text="Separador:", font=ctk.CTkFont(size=14))
        sep_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.sep_var = ctk.StringVar(value=";")
        sep_menu = ctk.CTkOptionMenu(
            config_frame,
            values=[";", ",", "|", "Tab (\\t)"],
            variable=self.sep_var,
            width=150
        )
        sep_menu.grid(row=0, column=1, padx=20, pady=10, sticky="w")
        
        # Encoding
        enc_label = ctk.CTkLabel(config_frame, text="Encoding:", font=ctk.CTkFont(size=14))
        enc_label.grid(row=0, column=2, padx=20, pady=10, sticky="w")
        
        self.enc_var = ctk.StringVar(value="utf-8")
        enc_menu = ctk.CTkOptionMenu(
            config_frame,
            values=["utf-8", "latin-1", "windows-1252", "iso-8859-1", "auto-detect"],
            variable=self.enc_var,
            width=150
        )
        enc_menu.grid(row=0, column=3, padx=20, pady=10, sticky="w")
        
        # Incluir cabeçalho
        self.header_var = ctk.BooleanVar(value=True)
        header_check = ctk.CTkCheckBox(
            config_frame,
            text="Incluir cabeçalho",
            variable=self.header_var
        )
        header_check.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="w")
        
        # Remover duplicatas
        self.dedup_var = ctk.BooleanVar(value=False)
        dedup_check = ctk.CTkCheckBox(
            config_frame,
            text="Remover linhas duplicadas",
            variable=self.dedup_var
        )
        dedup_check.grid(row=1, column=2, columnspan=2, padx=20, pady=10, sticky="w")
        
        # === Frame de Seleção de Arquivos ===
        files_frame = ctk.CTkFrame(self.scroll_container)
        files_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        files_header = ctk.CTkFrame(files_frame, fg_color="transparent")
        files_header.pack(fill="x", padx=10, pady=10)
        
        files_label = ctk.CTkLabel(
            files_header,
            text="Arquivos Selecionados:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        files_label.pack(side="left")
        
        # Botões de arquivo
        btn_frame = ctk.CTkFrame(files_header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        btn_add_files = ctk.CTkButton(
            btn_frame,
            text="+ Adicionar Arquivos",
            command=self.add_files,
            width=140,
            height=32
        )
        btn_add_files.pack(side="left", padx=5)
        
        btn_add_folder = ctk.CTkButton(
            btn_frame,
            text="📁 Adicionar Pasta",
            command=self.add_folder,
            width=140,
            height=32
        )
        btn_add_folder.pack(side="left", padx=5)
        
        btn_clear = ctk.CTkButton(
            btn_frame,
            text="🗑️ Limpar",
            command=self.clear_files,
            width=100,
            height=32,
            fg_color="gray40",
            hover_color="gray50"
        )
        btn_clear.pack(side="left", padx=5)
        
        # Lista de arquivos
        self.files_list = ctk.CTkScrollableFrame(files_frame, height=200)
        self.files_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.files_count_label = ctk.CTkLabel(
            files_frame,
            text="0 arquivos selecionados",
            text_color="gray50"
        )
        self.files_count_label.pack(pady=5)
        
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
            text="▶️ Executar Consolidação",
            command=self.execute,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_execute.pack(pady=20)
        
    def add_files(self):
        """Adiciona arquivos CSV à lista"""
        files = filedialog.askopenfilenames(
            title="Selecionar arquivos CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        for f in files:
            if f not in self.selected_files:
                self.selected_files.append(f)
        
        self.update_files_list()
        
    def add_folder(self):
        """Adiciona todos os CSVs de uma pasta"""
        folder = filedialog.askdirectory(title="Selecionar pasta")
        
        if folder:
            for f in Path(folder).glob("*.csv"):
                if str(f) not in self.selected_files:
                    self.selected_files.append(str(f))
        
        self.update_files_list()
        
    def clear_files(self):
        """Limpa a lista de arquivos"""
        self.selected_files = []
        self.update_files_list()
        
    def update_files_list(self):
        """Atualiza a exibição da lista de arquivos"""
        # Limpar lista atual
        for widget in self.files_list.winfo_children():
            widget.destroy()
        
        # Adicionar arquivos
        for i, f in enumerate(self.selected_files):
            file_frame = ctk.CTkFrame(self.files_list)
            file_frame.pack(fill="x", pady=2)
            
            # Nome do arquivo
            name_label = ctk.CTkLabel(
                file_frame,
                text=os.path.basename(f),
                anchor="w"
            )
            name_label.pack(side="left", padx=10, pady=5)
            
            # Caminho
            path_label = ctk.CTkLabel(
                file_frame,
                text=os.path.dirname(f),
                text_color="gray50",
                anchor="w"
            )
            path_label.pack(side="left", padx=10, pady=5)
            
            # Botão remover
            btn_remove = ctk.CTkButton(
                file_frame,
                text="✖",
                width=30,
                height=25,
                fg_color="red",
                hover_color="darkred",
                command=lambda idx=i: self.remove_file(idx)
            )
            btn_remove.pack(side="right", padx=10, pady=5)
        
        # Atualizar contador
        self.files_count_label.configure(text=f"{len(self.selected_files)} arquivos selecionados")
        
    def remove_file(self, index):
        """Remove um arquivo da lista"""
        if 0 <= index < len(self.selected_files):
            self.selected_files.pop(index)
            self.update_files_list()
            
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
        
    def execute(self):
        """Executa a consolidação dos CSVs"""
        if not self.selected_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado!")
            return
            
        output_file = self.output_entry.get()
        if not output_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo de saída!")
            return
        
        try:
            self.btn_execute.configure(state="disabled")
            self.status_label.configure(text="Processando...")
            self.progress_bar.set(0)
            self.update()
            
            dfs = []
            total = len(self.selected_files)
            sep = self.get_separator()
            
            for i, filepath in enumerate(self.selected_files):
                # Encoding
                if self.enc_var.get() == "auto-detect":
                    encoding = self.detect_encoding(filepath)
                else:
                    encoding = self.enc_var.get()
                
                # Ler arquivo
                df = pd.read_csv(
                    filepath,
                    sep=sep,
                    encoding=encoding,
                    low_memory=False
                )
                dfs.append(df)
                
                # Atualizar progresso
                progress = (i + 1) / total * 0.8
                self.progress_bar.set(progress)
                self.status_label.configure(text=f"Lendo arquivo {i+1}/{total}...")
                self.update()
            
            # Concatenar DataFrames
            self.status_label.configure(text="Consolidando dados...")
            self.update()
            
            result = pd.concat(dfs, ignore_index=True)
            
            # Remover duplicatas se solicitado
            if self.dedup_var.get():
                result = result.drop_duplicates()
            
            # Salvar resultado
            self.status_label.configure(text="Salvando arquivo...")
            self.progress_bar.set(0.9)
            self.update()
            
            result.to_csv(
                output_file,
                sep=sep,
                index=False,
                encoding=self.enc_var.get() if self.enc_var.get() != "auto-detect" else "utf-8"
            )
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Concluído! {len(result)} linhas salvas.")
            
            messagebox.showinfo(
                "Sucesso",
                f"Consolidação concluída!\n\n"
                f"Arquivos processados: {total}\n"
                f"Total de linhas: {len(result)}\n"
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
            "include_header": self.header_var.get(),
            "remove_duplicates": self.dedup_var.get()
        }
        
    def load_settings(self, settings):
        """Carrega configurações de um perfil"""
        if "separator" in settings:
            self.sep_var.set(settings["separator"])
        if "encoding" in settings:
            self.enc_var.set(settings["encoding"])
        if "include_header" in settings:
            self.header_var.set(settings["include_header"])
        if "remove_duplicates" in settings:
            self.dedup_var.set(settings["remove_duplicates"])
            
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
                "merger",
                self.get_settings()
            )
            messagebox.showinfo("Sucesso", f"Perfil '{profile_name}' salvo!")


