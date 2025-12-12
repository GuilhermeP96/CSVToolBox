# CSVToolBox - CSV Toolkit / Caixa de Ferramentas para Tratamento de CSVs
# Main Module / Módulo Principal

import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os
from pathlib import Path
from datetime import datetime

# Importar módulos de ferramentas
from tools.csv_merger import CSVMergerTool
from tools.csv_cleaner import CSVCleanerTool
from tools.csv_converter import CSVConverterTool
from tools.csv_transformer import CSVTransformerTool
from tools.csv_splitter import CSVSplitterTool
from tools.xml_parser import XMLParserTool
from tools.excel_to_csv import ExcelToCSVTool
from tools.column_cleaner import ColumnCleanerTool
from tools.txt_parser import TxtParserTool
from tools.profile_manager import ProfileManager

# Internationalization
from i18n import t, get_language, set_language, TRANSLATIONS


def get_user_data_dir():
    """Retorna o diretório de dados do usuário em Documentos\\CSVToolBox"""
    documents = Path(os.path.expanduser("~")) / "OneDrive - Claro SA" / "Documentos"
    if not documents.exists():
        # Fallback para Documentos padrão
        documents = Path(os.path.expanduser("~")) / "Documents"
    
    data_dir = documents / "CSVToolBox"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


class CSVToolBox(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuração da janela
        self.title(t("app_title"))
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Diretório de dados do usuário
        self.data_dir = get_user_data_dir()
        self.config_path = self.data_dir / "config.json"
        self.history_path = self.data_dir / "history.json"
        
        # Carregar configurações
        self.load_config()
        self.load_history()
        
        # Aplicar idioma salvo nas configurações (se houver)
        saved_lang = self.config.get("settings", {}).get("language")
        if saved_lang in ["pt", "en"]:
            set_language(saved_lang)
        
        # Gerenciador de perfis
        self.profile_manager = ProfileManager(self.config, self.save_config)
        
        # Criar interface
        self.create_widgets()
        
    def load_config(self):
        """Carrega configurações do arquivo JSON"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "profiles": {},
                    "settings": {
                        "theme": "dark-blue",
                        "default_encoding": "utf-8",
                        "default_separator": ";",
                        "max_recent": 20,
                        "language": get_language()
                    }
                }
                self.save_config()
        except Exception as e:
            messagebox.showerror(t("error"), f"{t('error')}: {e}")
            self.config = {"profiles": {}, "settings": {}}
    
    def save_config(self, update_ui=True):
        """Save settings to JSON file / Salva configurações no arquivo JSON"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            # Atualizar lista de perfis na UI se necessário
            if update_ui and hasattr(self, 'profiles_frame'):
                self.update_profiles_list()
        except Exception as e:
            messagebox.showerror(t("error"), f"{t('error')}: {e}")
    
    def load_history(self):
        """Carrega histórico de processos recentes"""
        try:
            if self.history_path.exists():
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except Exception:
            self.history = []
    
    def save_history(self):
        """Salva histórico de processos recentes"""
        try:
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def add_to_history(self, tool_id: str, tool_name: str, settings: dict, input_file: str = None, output_file: str = None):
        """Adiciona um processo ao histórico"""
        entry = {
            "tool_id": tool_id,
            "tool_name": tool_name,
            "settings": settings,
            "input_file": input_file,
            "output_file": output_file,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Inserir no início
        self.history.insert(0, entry)
        
        # Limitar tamanho
        max_recent = self.config.get("settings", {}).get("max_recent", 20)
        self.history = self.history[:max_recent]
        
        self.save_history()
        self.update_history_list()
    
    def clear_history(self):
        """Clear process history / Limpa o histórico de processos"""
        if messagebox.askyesno(t("confirm"), t("clear_history_confirm")):
            self.history = []
            self.save_history()
            self.update_history_list()
            messagebox.showinfo(t("success"), t("history_cleared"))
    
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        
        # === Frame Principal ===
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Sidebar (Menu de Ferramentas) ===
        self.sidebar = ctk.CTkFrame(self.main_frame, width=220)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Frame do Logo com botão Home
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(15, 5))
        
        # Botão Home (clique no logo volta para tela inicial)
        self.btn_home = ctk.CTkButton(
            logo_frame,
            text="🏠",
            command=self.show_home,
            width=40,
            height=40,
            fg_color="transparent",
            hover_color="gray30",
            font=ctk.CTkFont(size=20)
        )
        self.btn_home.pack(side="left", padx=(20, 5))
        
        # Logo/Título
        self.logo_label = ctk.CTkLabel(
            logo_frame, 
            text="CSVToolBox",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.pack(side="left", padx=5)
        
        # Separador
        self.separator1 = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray40")
        self.separator1.pack(fill="x", padx=20, pady=10)
        
        # Label Ferramentas
        self.tools_label = ctk.CTkLabel(
            self.sidebar,
            text=t("tools"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray60"
        )
        self.tools_label.pack(pady=(10, 5))
        
        # Botões de ferramentas
        self.tool_buttons = {}
        tools = [
            (t("tool_merger"), "merger"),
            (t("tool_splitter"), "splitter"),
            (t("tool_cleaner"), "cleaner"),
            (t("tool_converter"), "converter"),
            (t("tool_transformer"), "transformer"),
            (t("tool_xml_parser"), "xml_parser"),
            (t("tool_excel_to_csv"), "excel_to_csv"),
            (t("tool_column_cleaner"), "column_cleaner"),
            (t("tool_txt_parser"), "txt_parser"),
        ]
        
        for text, tool_id in tools:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda t=tool_id: self.show_tool(t),
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14)
            )
            btn.pack(fill="x", padx=20, pady=5)
            self.tool_buttons[tool_id] = btn
        
        # Espaçador
        self.spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.spacer.pack(fill="both", expand=True)
        
        # Configurações (bottom)
        self.btn_settings = ctk.CTkButton(
            self.sidebar,
            text=t("settings"),
            command=self.show_settings,
            height=35,
            fg_color="gray30",
            hover_color="gray40"
        )
        self.btn_settings.pack(fill="x", padx=20, pady=(0, 10))
        
        # === Área Central (conteúdo + barra inferior) ===
        center_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        center_frame.pack(side="right", fill="both", expand=True)
        
        # === Área de Conteúdo Principal ===
        self.content_frame = ctk.CTkFrame(center_frame)
        self.content_frame.pack(fill="both", expand=True)
        
        # === Barra Inferior (Perfis e Recentes lado a lado) ===
        bottom_bar = ctk.CTkFrame(center_frame, height=150)
        bottom_bar.pack(fill="x", pady=(10, 0))
        bottom_bar.pack_propagate(False)
        
        # --- Coluna Perfis Salvos ---
        profiles_col = ctk.CTkFrame(bottom_bar)
        profiles_col.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        profiles_header = ctk.CTkFrame(profiles_col, fg_color="transparent")
        profiles_header.pack(fill="x", padx=10, pady=5)
        
        self.profiles_label = ctk.CTkLabel(
            profiles_header,
            text=t("profiles_saved"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray60"
        )
        self.profiles_label.pack(side="left")
        
        self.btn_new_profile = ctk.CTkButton(
            profiles_header,
            text=t("new_profile"),
            command=self.create_new_profile,
            width=60,
            height=24,
            fg_color="green",
            hover_color="darkgreen",
            font=ctk.CTkFont(size=11)
        )
        self.btn_new_profile.pack(side="right")
        
        self.profiles_frame = ctk.CTkScrollableFrame(profiles_col, height=100)
        self.profiles_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.update_profiles_list()
        
        # --- Coluna Recentes ---
        history_col = ctk.CTkFrame(bottom_bar)
        history_col.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        history_header = ctk.CTkFrame(history_col, fg_color="transparent")
        history_header.pack(fill="x", padx=10, pady=5)
        
        self.history_label = ctk.CTkLabel(
            history_header,
            text=t("recent"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray60"
        )
        self.history_label.pack(side="left")
        
        self.btn_clear_history = ctk.CTkButton(
            history_header,
            text=t("clear"),
            command=self.clear_history,
            width=70,
            height=24,
            fg_color="gray30",
            hover_color="gray40",
            font=ctk.CTkFont(size=11)
        )
        self.btn_clear_history.pack(side="right")
        
        self.history_frame = ctk.CTkScrollableFrame(history_col, height=100)
        self.history_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.update_history_list()
        
        # Criar frames para cada ferramenta (inicialmente ocultos)
        self.tool_frames = {}
        
        # Frame de boas-vindas (inicial)
        self.welcome_frame = self.create_welcome_frame()
        self.current_frame = self.welcome_frame
        
    def create_welcome_frame(self):
        """Create welcome frame / Cria o frame de boas-vindas"""
        frame = ctk.CTkFrame(self.content_frame)
        frame.pack(fill="both", expand=True)
        
        # Scrollable container for smaller windows
        scroll_container = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title = ctk.CTkLabel(
            scroll_container,
            text=t("welcome_title"),
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(50, 20))
        
        # Subtítulo
        subtitle = ctk.CTkLabel(
            scroll_container,
            text=t("welcome_subtitle"),
            font=ctk.CTkFont(size=16),
            text_color="gray60"
        )
        subtitle.pack(pady=(0, 30))
        
        # Cards de funcionalidades (clicáveis)
        cards_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        cards_frame.pack(pady=10)
        
        # Mapeamento de tool_id para keys de tradução
        features = [
            ("📊", "tool_merger", "desc_merger", "merger"),
            ("✂️", "tool_splitter", "desc_splitter", "splitter"),
            ("🧹", "tool_cleaner", "desc_cleaner", "cleaner"),
            ("🔄", "tool_converter", "desc_converter", "converter"),
            ("⚙️", "tool_transformer", "desc_transformer", "transformer"),
            ("📄", "tool_xml_parser", "desc_xml_parser", "xml_parser"),
            ("📑", "tool_excel_to_csv", "desc_excel_to_csv", "excel_to_csv"),
            ("🔤", "tool_column_cleaner", "desc_column_cleaner", "column_cleaner"),
            ("📝", "tool_txt_parser", "desc_txt_parser", "txt_parser"),
        ]
        
        for i, (icon, title_key, desc_key, tool_id) in enumerate(features):
            # Card como botão clicável
            card = ctk.CTkFrame(cards_frame, width=220, height=140)
            card.grid(row=i//3, column=i%3, padx=10, pady=10)
            card.grid_propagate(False)
            
            # Bind para fazer o card inteiro ser clicável
            card.bind("<Button-1>", lambda e, tid=tool_id: self.show_tool(tid))
            card.bind("<Enter>", lambda e, c=card: c.configure(fg_color="gray30"))
            card.bind("<Leave>", lambda e, c=card: c.configure(fg_color=("gray86", "gray17")))
            card.configure(cursor="hand2")
            
            # Remover emoji do título traduzido para exibição separada
            tool_title = t(title_key).replace("📊 ", "").replace("✂️ ", "").replace("🧹 ", "").replace("🔄 ", "").replace("⚙️ ", "").replace("📄 ", "").replace("📑 ", "").replace("🔤 ", "").replace("📝 ", "")
            
            icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=40))
            icon_label.pack(pady=(20, 10))
            icon_label.bind("<Button-1>", lambda e, tid=tool_id: self.show_tool(tid))
            
            title_label = ctk.CTkLabel(card, text=tool_title, font=ctk.CTkFont(size=16, weight="bold"))
            title_label.pack()
            title_label.bind("<Button-1>", lambda e, tid=tool_id: self.show_tool(tid))
            
            desc_label = ctk.CTkLabel(card, text=t(desc_key), font=ctk.CTkFont(size=12), text_color="gray60", wraplength=200)
            desc_label.pack(pady=10)
            desc_label.bind("<Button-1>", lambda e, tid=tool_id: self.show_tool(tid))
        
        # Dica
        tip = ctk.CTkLabel(
            scroll_container,
            text=t("tip_profiles"),
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        )
        tip.pack(pady=30)
        
        return frame
    
    def show_tool(self, tool_id):
        """Mostra a ferramenta selecionada"""
        # Esconder frame atual
        if self.current_frame:
            self.current_frame.pack_forget()
        
        # Criar frame da ferramenta se não existir
        if tool_id not in self.tool_frames:
            if tool_id == "merger":
                self.tool_frames[tool_id] = CSVMergerTool(self.content_frame, self.profile_manager)
            elif tool_id == "splitter":
                self.tool_frames[tool_id] = CSVSplitterTool(self.content_frame, self.profile_manager)
            elif tool_id == "cleaner":
                self.tool_frames[tool_id] = CSVCleanerTool(self.content_frame, self.profile_manager)
            elif tool_id == "converter":
                self.tool_frames[tool_id] = CSVConverterTool(self.content_frame, self.profile_manager)
            elif tool_id == "transformer":
                self.tool_frames[tool_id] = CSVTransformerTool(self.content_frame, self.profile_manager)
            elif tool_id == "xml_parser":
                self.tool_frames[tool_id] = XMLParserTool(self.content_frame, self.profile_manager)
            elif tool_id == "excel_to_csv":
                self.tool_frames[tool_id] = ExcelToCSVTool(self.content_frame, self.profile_manager)
            elif tool_id == "column_cleaner":
                self.tool_frames[tool_id] = ColumnCleanerTool(self.content_frame, self.profile_manager)
            elif tool_id == "txt_parser":
                self.tool_frames[tool_id] = TxtParserTool(self.content_frame, self.profile_manager)
        
        # Mostrar frame da ferramenta
        self.tool_frames[tool_id].pack(fill="both", expand=True)
        self.current_frame = self.tool_frames[tool_id]
        
        # Destacar botão ativo
        for btn_id, btn in self.tool_buttons.items():
            if btn_id == tool_id:
                btn.configure(fg_color=("gray70", "gray30"))
            else:
                btn.configure(fg_color=("gray70", "gray25"))
    
    def show_home(self):
        """Volta para a tela inicial"""
        # Esconder frame atual
        if self.current_frame:
            self.current_frame.pack_forget()
        
        # Mostrar frame de boas-vindas
        self.welcome_frame.pack(fill="both", expand=True)
        self.current_frame = self.welcome_frame
        
        # Resetar destaque dos botões
        for btn in self.tool_buttons.values():
            btn.configure(fg_color=("gray70", "gray25"))
    
    def update_history_list(self):
        """Update recent processes list / Atualiza a lista de processos recentes"""
        # Limpar lista atual
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        if not self.history:
            no_history = ctk.CTkLabel(
                self.history_frame,
                text=t("no_recent"),
                text_color="gray50",
                font=ctk.CTkFont(size=11)
            )
            no_history.pack(pady=10)
        else:
            for i, entry in enumerate(self.history[:10]):  # Mostrar apenas 10
                tool_name = entry.get("tool_name", "Processo")
                timestamp = entry.get("timestamp", "")
                
                # Truncar nome se muito longo
                display_name = tool_name[:20] + "..." if len(tool_name) > 20 else tool_name
                
                btn_frame = ctk.CTkFrame(self.history_frame, fg_color="transparent")
                btn_frame.pack(fill="x", pady=1)
                
                history_btn = ctk.CTkButton(
                    btn_frame,
                    text=f"🕐 {display_name}",
                    command=lambda e=entry: self.load_history_entry(e),
                    height=26,
                    fg_color="transparent",
                    hover_color="gray30",
                    anchor="w",
                    font=ctk.CTkFont(size=11)
                )
                history_btn.pack(fill="x")
    
    def load_history_entry(self, entry):
        """Carrega uma entrada do histórico"""
        tool_id = entry.get("tool_id")
        settings = entry.get("settings", {})
        
        if tool_id:
            self.show_tool(tool_id)
            # Carregar configurações no frame da ferramenta
            if tool_id in self.tool_frames and hasattr(self.tool_frames[tool_id], 'load_settings'):
                self.tool_frames[tool_id].load_settings(settings)
    
    def update_profiles_list(self):
        """Update profiles list / Atualiza a lista de perfis"""
        # Limpar lista atual
        for widget in self.profiles_frame.winfo_children():
            widget.destroy()
        
        # Adicionar perfis
        profiles = self.config.get("profiles", {})
        
        # Mapeamento de tool_id para nome completo (traduzido)
        tool_names = {
            "merger": t("profile_merger"),
            "splitter": t("profile_splitter"),
            "cleaner": t("profile_cleaner"),
            "converter": t("profile_converter"),
            "transformer": t("profile_transformer"),
            "xml_parser": t("profile_xml_parser"),
            "excel_to_csv": t("profile_excel_to_csv"),
            "column_cleaner": t("profile_column_cleaner"),
            "txt_parser": t("profile_txt_parser"),
        }
        
        if not profiles:
            no_profiles = ctk.CTkLabel(
                self.profiles_frame,
                text=t("no_profiles"),
                text_color="gray50"
            )
            no_profiles.pack(pady=10)
        else:
            for profile_name, profile_data in profiles.items():
                tool_id = profile_data.get("tool", "")
                tool_label = tool_names.get(tool_id, "[?]")
                
                profile_btn = ctk.CTkButton(
                    self.profiles_frame,
                    text=f"{tool_label} {profile_name}",
                    command=lambda p=profile_name: self.load_profile(p),
                    height=28,
                    fg_color="transparent",
                    hover_color="gray30",
                    anchor="w",
                    font=ctk.CTkFont(size=11)
                )
                profile_btn.pack(fill="x", pady=1)
    
    def create_new_profile(self):
        """Open dialog to create new profile / Abre diálogo para criar novo perfil"""
        dialog = ctk.CTkInputDialog(
            text=t("profile_name_prompt"),
            title=t("create_profile_title")
        )
        profile_name = dialog.get_input()
        
        if profile_name:
            if profile_name in self.config["profiles"]:
                messagebox.showwarning(t("warning"), t("profile_exists"))
            else:
                self.config["profiles"][profile_name] = {
                    "tool": None,
                    "settings": {}
                }
                self.save_config()
                self.update_profiles_list()
                messagebox.showinfo(t("success"), t("profile_created").format(profile_name))
    
    def load_profile(self, profile_name):
        """Carrega um perfil salvo"""
        profile = self.config["profiles"].get(profile_name)
        if profile and profile.get("tool"):
            self.show_tool(profile["tool"])
            # Carregar configurações no frame da ferramenta
            if profile["tool"] in self.tool_frames:
                self.tool_frames[profile["tool"]].load_settings(profile.get("settings", {}))
    
    def show_settings(self):
        """Show settings window / Mostra janela de configurações"""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title(t("settings_title"))
        settings_window.geometry("500x450")
        settings_window.transient(self)
        settings_window.grab_set()
        
        # Título
        title = ctk.CTkLabel(
            settings_window,
            text=t("settings_title"),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame de configurações
        settings_frame = ctk.CTkFrame(settings_window)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tema
        theme_label = ctk.CTkLabel(settings_frame, text=t("theme"), font=ctk.CTkFont(size=14))
        theme_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        theme_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["Dark", "Light", "System"],
            variable=theme_var,
            command=lambda v: ctk.set_appearance_mode(v.lower())
        )
        theme_menu.grid(row=0, column=1, padx=20, pady=15)
        
        # Idioma / Language
        lang_label = ctk.CTkLabel(settings_frame, text=t("language"), font=ctk.CTkFont(size=14))
        lang_label.grid(row=1, column=0, padx=20, pady=15, sticky="w")
        
        current_lang = self.config.get("settings", {}).get("language", get_language())
        lang_var = ctk.StringVar(value="Português" if current_lang == "pt" else "English")
        lang_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["Português", "English"],
            variable=lang_var
        )
        lang_menu.grid(row=1, column=1, padx=20, pady=15)
        
        # Encoding padrão
        enc_label = ctk.CTkLabel(settings_frame, text=t("default_encoding"), font=ctk.CTkFont(size=14))
        enc_label.grid(row=2, column=0, padx=20, pady=15, sticky="w")
        
        enc_var = ctk.StringVar(value=self.config["settings"].get("default_encoding", "utf-8"))
        enc_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["utf-8", "latin-1", "windows-1252", "iso-8859-1"],
            variable=enc_var
        )
        enc_menu.grid(row=2, column=1, padx=20, pady=15)
        
        # Separador padrão
        sep_label = ctk.CTkLabel(settings_frame, text=t("default_separator"), font=ctk.CTkFont(size=14))
        sep_label.grid(row=3, column=0, padx=20, pady=15, sticky="w")
        
        sep_var = ctk.StringVar(value=self.config["settings"].get("default_separator", ";"))
        sep_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=[";", ",", "|", "\\t"],
            variable=sep_var
        )
        sep_menu.grid(row=3, column=1, padx=20, pady=15)
        
        # Nota de reinício
        restart_note = ctk.CTkLabel(
            settings_frame,
            text="* Language changes require restart\n* Alterações de idioma requerem reinício",
            font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        restart_note.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Botão Salvar
        def save_settings():
            self.config["settings"]["default_encoding"] = enc_var.get()
            self.config["settings"]["default_separator"] = sep_var.get()
            # Salvar idioma
            new_lang = "pt" if lang_var.get() == "Português" else "en"
            self.config["settings"]["language"] = new_lang
            set_language(new_lang)
            self.save_config()
            settings_window.destroy()
            # Restart application to apply changes
            self.restart_application()
        
        save_btn = ctk.CTkButton(
            settings_window,
            text=t("save"),
            command=save_settings,
            height=40
        )
        save_btn.pack(pady=20)

    def restart_application(self):
        """Restart the application / Reinicia a aplicação"""
        import sys
        import subprocess
        
        # Get the current Python executable and script
        python = sys.executable
        script = sys.argv[0]
        
        # Start new instance
        subprocess.Popen([python, script])
        
        # Close current instance
        self.destroy()


def main():
    app = CSVToolBox()
    app.mainloop()


if __name__ == "__main__":
    main()
