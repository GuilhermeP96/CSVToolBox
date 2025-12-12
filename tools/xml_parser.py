# XML Parser Tool - Ferramenta para Converter XML para CSV

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import xml.etree.ElementTree as ET
import os
from pathlib import Path
import threading


class XMLParserTool(ctk.CTkFrame):
    """Ferramenta para converter arquivos XML para CSV"""
    
    def __init__(self, parent, profile_manager):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.input_file = None
        self.is_processing = False
        
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
            text="📄 XML para CSV",
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
            text="Arquivo XML:",
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
        
        # === Frame de Configurações de Parsing ===
        parse_frame = ctk.CTkFrame(self.scroll_container)
        parse_frame.pack(fill="x", padx=20, pady=10)
        
        parse_label = ctk.CTkLabel(
            parse_frame,
            text="Configurações de Parsing",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        parse_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        # Elemento raiz para parsear
        root_label = ctk.CTkLabel(parse_frame, text="Elemento a extrair:", font=ctk.CTkFont(size=13))
        root_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.root_element_entry = ctk.CTkEntry(parse_frame, width=200)
        self.root_element_entry.insert(0, "*")
        self.root_element_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        root_hint = ctk.CTkLabel(
            parse_frame,
            text="Use * para todos ou nome específico (ex: oferta, item, registro)",
            text_color="gray50",
            font=ctk.CTkFont(size=11)
        )
        root_hint.grid(row=1, column=2, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Modo de parsing
        mode_label = ctk.CTkLabel(parse_frame, text="Modo:", font=ctk.CTkFont(size=13))
        mode_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.parse_mode_var = ctk.StringVar(value="auto")
        mode_menu = ctk.CTkOptionMenu(
            parse_frame,
            values=["auto", "flat", "nested"],
            variable=self.parse_mode_var,
            width=120
        )
        mode_menu.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        mode_hint = ctk.CTkLabel(
            parse_frame,
            text="auto: detecta | flat: só folhas | nested: mantém hierarquia",
            text_color="gray50",
            font=ctk.CTkFont(size=11)
        )
        mode_hint.grid(row=2, column=2, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Concatenar listas
        self.concat_lists_var = ctk.BooleanVar(value=True)
        concat_lists = ctk.CTkCheckBox(
            parse_frame,
            text="Concatenar valores repetidos com |",
            variable=self.concat_lists_var
        )
        concat_lists.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="w")
        
        # Ignorar namespaces
        self.ignore_ns_var = ctk.BooleanVar(value=True)
        ignore_ns = ctk.CTkCheckBox(
            parse_frame,
            text="Ignorar namespaces XML",
            variable=self.ignore_ns_var
        )
        ignore_ns.grid(row=3, column=2, columnspan=2, padx=20, pady=10, sticky="w")
        
        # === Frame de Configurações de Saída ===
        output_config = ctk.CTkFrame(self.scroll_container)
        output_config.pack(fill="x", padx=20, pady=10)
        
        output_config_label = ctk.CTkLabel(
            output_config,
            text="Configurações de Saída",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        output_config_label.grid(row=0, column=0, columnspan=4, padx=20, pady=10, sticky="w")
        
        # Encoding
        enc_label = ctk.CTkLabel(output_config, text="Encoding:", font=ctk.CTkFont(size=13))
        enc_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.enc_var = ctk.StringVar(value="utf-8")
        enc_menu = ctk.CTkOptionMenu(
            output_config,
            values=["utf-8", "utf-8-sig", "windows-1252", "latin-1"],
            variable=self.enc_var,
            width=140
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
        
        # Quoting
        quote_label = ctk.CTkLabel(output_config, text="Quoting:", font=ctk.CTkFont(size=13))
        quote_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        
        self.quote_var = ctk.StringVar(value="QUOTE_ALL")
        quote_menu = ctk.CTkOptionMenu(
            output_config,
            values=["QUOTE_MINIMAL", "QUOTE_ALL", "QUOTE_NONNUMERIC", "QUOTE_NONE"],
            variable=self.quote_var,
            width=180
        )
        quote_menu.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
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
        
        # === Log de Processo ===
        log_frame = ctk.CTkFrame(self.scroll_container)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="Log do Processo:",
            font=ctk.CTkFont(size=12)
        )
        log_label.pack(anchor="w", padx=10, pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, height=120)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
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
            title="Selecionar arquivo XML",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if file:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, file)
            
            # Sugerir nome de saída
            base = os.path.splitext(file)[0]
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, f"{base}.csv")
            
            # Tentar detectar estrutura
            self.detect_xml_structure(file)
            
    def detect_xml_structure(self, filepath):
        """Detecta a estrutura do XML"""
        try:
            self.log_text.insert("end", f"Analisando estrutura do XML...\n")
            self.update()
            
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Encontrar elementos repetidos (prováveis registros)
            child_counts = {}
            for child in root:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                child_counts[tag] = child_counts.get(tag, 0) + 1
            
            # Elemento mais frequente provavelmente é o registro
            if child_counts:
                most_common = max(child_counts, key=child_counts.get)
                count = child_counts[most_common]
                
                self.log_text.insert("end", f"Estrutura detectada:\n")
                self.log_text.insert("end", f"  - Raiz: {root.tag.split('}')[-1]}\n")
                self.log_text.insert("end", f"  - Elemento mais comum: '{most_common}' ({count}x)\n")
                
                if count > 1:
                    self.root_element_entry.delete(0, "end")
                    self.root_element_entry.insert(0, most_common)
                    self.log_text.insert("end", f"  → Sugestão: usar '{most_common}' como elemento\n")
                    
        except Exception as e:
            self.log_text.insert("end", f"Erro ao analisar XML: {str(e)}\n")
            
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
        """Retorna o separador real"""
        sep = self.sep_var.get()
        if sep == "Tab (\\t)":
            return "\t"
        return sep
    
    def get_quoting(self):
        """Retorna o valor de quoting"""
        import csv
        quote_map = {
            "QUOTE_MINIMAL": csv.QUOTE_MINIMAL,
            "QUOTE_ALL": csv.QUOTE_ALL,
            "QUOTE_NONNUMERIC": csv.QUOTE_NONNUMERIC,
            "QUOTE_NONE": csv.QUOTE_NONE
        }
        return quote_map.get(self.quote_var.get(), csv.QUOTE_ALL)
    
    def parse_element(self, element):
        """Converte um elemento XML em dicionário"""
        data = {}
        
        # Atributos do elemento
        for attr_name, attr_value in element.attrib.items():
            if self.ignore_ns_var.get() and '{' in attr_name:
                attr_name = attr_name.split('}')[-1]
            data[f"@{attr_name}"] = attr_value
        
        # Processar filhos
        for child in element:
            tag = child.tag
            if self.ignore_ns_var.get() and '}' in tag:
                tag = tag.split('}')[-1]
            
            # Se tem filhos, é complexo - pegar só texto ou recursivo
            if len(child) == 0:
                value = (child.text or '').strip()
            else:
                # Modo nested: criar sub-dicionário
                if self.parse_mode_var.get() == "nested":
                    value = self.parse_element(child)
                else:
                    # Modo flat: concatenar valores dos filhos
                    value = (child.text or '').strip()
            
            # Concatenar valores repetidos
            if tag in data:
                if self.concat_lists_var.get():
                    data[tag] = f"{data[tag]}|{value}"
                else:
                    # Criar lista
                    if not isinstance(data[tag], list):
                        data[tag] = [data[tag]]
                    data[tag].append(value)
            else:
                data[tag] = value
        
        return data
    
    def flatten_dict(self, d, parent_key='', sep='_'):
        """Achata um dicionário aninhado"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
            
    def execute(self):
        """Executa a conversão"""
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        
        if not input_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo XML!")
            return
            
        if not output_file:
            messagebox.showwarning("Aviso", "Selecione um arquivo de saída!")
            return
        
        # Executar em thread separada para não travar a UI
        thread = threading.Thread(target=self._execute_conversion, args=(input_file, output_file))
        thread.start()
        
    def _execute_conversion(self, input_file, output_file):
        """Executa a conversão (em thread)"""
        try:
            self.btn_execute.configure(state="disabled")
            self.is_processing = True
            self.log_text.delete("1.0", "end")
            self.status_label.configure(text="Parseando XML...")
            self.progress_bar.set(0.1)
            self.update()
            
            element_name = self.root_element_entry.get().strip()
            
            self.log_text.insert("end", f"Abrindo arquivo XML...\n")
            self.update()
            
            # Parsear XML
            tree = ET.parse(input_file)
            root = tree.getroot()
            
            self.log_text.insert("end", f"XML carregado. Raiz: {root.tag}\n")
            self.progress_bar.set(0.3)
            self.update()
            
            # Encontrar elementos
            if element_name == "*":
                # Pegar todos os filhos diretos da raiz
                elements = list(root)
            else:
                # Buscar elementos específicos
                if self.ignore_ns_var.get():
                    # Busca sem namespace
                    elements = [e for e in root.iter() if e.tag.split('}')[-1] == element_name]
                else:
                    elements = root.findall(f".//{element_name}")
            
            total_elements = len(elements)
            self.log_text.insert("end", f"Encontrados {total_elements} elementos para processar\n")
            self.update()
            
            if total_elements == 0:
                messagebox.showwarning("Aviso", f"Nenhum elemento '{element_name}' encontrado no XML!")
                return
            
            # Converter elementos
            records = []
            for i, element in enumerate(elements):
                data = self.parse_element(element)
                
                # Achatar se necessário
                if self.parse_mode_var.get() != "nested":
                    data = self.flatten_dict(data)
                
                records.append(data)
                
                if (i + 1) % 1000 == 0:
                    progress = 0.3 + (0.5 * (i + 1) / total_elements)
                    self.progress_bar.set(progress)
                    self.status_label.configure(text=f"Processando elemento {i+1}/{total_elements}...")
                    self.update()
            
            self.log_text.insert("end", f"Convertendo para DataFrame...\n")
            self.progress_bar.set(0.85)
            self.update()
            
            # Criar DataFrame
            df = pd.DataFrame(records)
            
            self.log_text.insert("end", f"Salvando CSV...\n")
            self.progress_bar.set(0.95)
            self.update()
            
            # Salvar
            sep = self.get_separator()
            encoding = self.enc_var.get()
            quoting = self.get_quoting()
            
            df.to_csv(output_file, sep=sep, encoding=encoding, index=False, quoting=quoting)
            
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Concluído! {len(df)} registros salvos.")
            
            self.log_text.insert("end", f"\n✅ Conversão concluída!\n")
            self.log_text.insert("end", f"   Registros: {len(df)}\n")
            self.log_text.insert("end", f"   Colunas: {len(df.columns)}\n")
            self.log_text.insert("end", f"   Arquivo: {output_file}\n")
            
            messagebox.showinfo(
                "Sucesso",
                f"Conversão concluída!\n\n"
                f"Registros: {len(df)}\n"
                f"Colunas: {len(df.columns)}\n"
                f"Arquivo: {output_file}"
            )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar: {str(e)}")
            self.log_text.insert("end", f"\n❌ Erro: {str(e)}\n")
            self.status_label.configure(text=f"Erro: {str(e)}")
        finally:
            self.btn_execute.configure(state="normal")
            self.is_processing = False
            
    def get_settings(self):
        """Retorna as configurações atuais"""
        return {
            "root_element": self.root_element_entry.get(),
            "parse_mode": self.parse_mode_var.get(),
            "concat_lists": self.concat_lists_var.get(),
            "ignore_namespaces": self.ignore_ns_var.get(),
            "encoding": self.enc_var.get(),
            "separator": self.sep_var.get(),
            "quoting": self.quote_var.get()
        }
        
    def load_settings(self, settings):
        """Carrega configurações de um perfil"""
        if "root_element" in settings:
            self.root_element_entry.delete(0, "end")
            self.root_element_entry.insert(0, settings["root_element"])
        if "parse_mode" in settings:
            self.parse_mode_var.set(settings["parse_mode"])
        if "concat_lists" in settings:
            self.concat_lists_var.set(settings["concat_lists"])
        if "ignore_namespaces" in settings:
            self.ignore_ns_var.set(settings["ignore_namespaces"])
        if "encoding" in settings:
            self.enc_var.set(settings["encoding"])
        if "separator" in settings:
            self.sep_var.set(settings["separator"])
        if "quoting" in settings:
            self.quote_var.set(settings["quoting"])
            
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
                "xml_parser",
                self.get_settings()
            )
            messagebox.showinfo("Sucesso", f"Perfil '{profile_name}' salvo!")


