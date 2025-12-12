# CSVToolBox - Caixa de Ferramentas para Tratamento de CSVs
# Módulo Principal

import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os
from pathlib import Path

# Importar módulos de ferramentas
from tools.csv_merger import CSVMergerTool
from tools.csv_cleaner import CSVCleanerTool
from tools.csv_converter import CSVConverterTool
from tools.csv_transformer import CSVTransformerTool
from tools.csv_splitter import CSVSplitterTool
from tools.profile_manager import ProfileManager

class CSVToolBox(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuração da janela
        self.title("CSVToolBox - Caixa de Ferramentas CSV")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Carregar configurações
        self.config_path = Path(__file__).parent / "config.json"
        self.load_config()
        
        # Gerenciador de perfis
        self.profile_manager = ProfileManager(self.config)
        
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
                    "recent_files": [],
                    "settings": {
                        "theme": "dark-blue",
                        "default_encoding": "utf-8",
                        "default_separator": ";",
                        "max_recent_files": 10
                    }
                }
                self.save_config()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar configurações: {e}")
            self.config = {"profiles": {}, "recent_files": [], "settings": {}}
    
    def save_config(self):
        """Salva configurações no arquivo JSON"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
    
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        
        # === Frame Principal ===
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Sidebar (Menu de Ferramentas) ===
        self.sidebar = ctk.CTkFrame(self.main_frame, width=250)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Logo/Título
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="🛠️ CSVToolBox",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.pack(pady=20)
        
        # Separador
        self.separator1 = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray40")
        self.separator1.pack(fill="x", padx=20, pady=10)
        
        # Label Ferramentas
        self.tools_label = ctk.CTkLabel(
            self.sidebar,
            text="FERRAMENTAS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray60"
        )
        self.tools_label.pack(pady=(10, 5))
        
        # Botões de ferramentas
        self.tool_buttons = {}
        tools = [
            ("📊 Consolidar CSVs", "merger"),
            ("✂️ Dividir CSV", "splitter"),
            ("🧹 Limpar CSV", "cleaner"),
            ("🔄 Converter Formato", "converter"),
            ("⚙️ Transformar Dados", "transformer"),
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
        
        # Separador
        self.separator2 = ctk.CTkFrame(self.sidebar, height=2, fg_color="gray40")
        self.separator2.pack(fill="x", padx=20, pady=20)
        
        # Label Perfis
        self.profiles_label = ctk.CTkLabel(
            self.sidebar,
            text="PERFIS SALVOS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray60"
        )
        self.profiles_label.pack(pady=(0, 5))
        
        # Frame para lista de perfis
        self.profiles_frame = ctk.CTkScrollableFrame(self.sidebar, height=200)
        self.profiles_frame.pack(fill="x", padx=20, pady=5)
        
        self.update_profiles_list()
        
        # Botão Novo Perfil
        self.btn_new_profile = ctk.CTkButton(
            self.sidebar,
            text="+ Novo Perfil",
            command=self.create_new_profile,
            height=35,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_new_profile.pack(fill="x", padx=20, pady=10)
        
        # Espaçador
        self.spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.spacer.pack(fill="both", expand=True)
        
        # Configurações (bottom)
        self.btn_settings = ctk.CTkButton(
            self.sidebar,
            text="⚙️ Configurações",
            command=self.show_settings,
            height=35,
            fg_color="gray30",
            hover_color="gray40"
        )
        self.btn_settings.pack(fill="x", padx=20, pady=(0, 10))
        
        # === Área de Conteúdo Principal ===
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Criar frames para cada ferramenta (inicialmente ocultos)
        self.tool_frames = {}
        
        # Frame de boas-vindas (inicial)
        self.welcome_frame = self.create_welcome_frame()
        self.current_frame = self.welcome_frame
        
    def create_welcome_frame(self):
        """Cria o frame de boas-vindas"""
        frame = ctk.CTkFrame(self.content_frame)
        frame.pack(fill="both", expand=True)
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="Bem-vindo ao CSVToolBox!",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.pack(pady=(100, 20))
        
        # Subtítulo
        subtitle = ctk.CTkLabel(
            frame,
            text="Sua caixa de ferramentas para tratamento de arquivos CSV",
            font=ctk.CTkFont(size=16),
            text_color="gray60"
        )
        subtitle.pack(pady=(0, 40))
        
        # Cards de funcionalidades
        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(pady=20)
        
        features = [
            ("📊", "Consolidar CSVs", "Mescle múltiplos arquivos CSV em um único arquivo"),
            ("✂️", "Dividir CSV", "Divida arquivos grandes em partes menores"),
            ("🧹", "Limpar CSV", "Remova caracteres especiais, aspas e limpe dados"),
            ("🔄", "Converter", "Converta entre CSV, XLSX, XML e outros formatos"),
            ("⚙️", "Transformar", "Substitua valores, filtre colunas e transforme dados"),
        ]
        
        for i, (icon, title, desc) in enumerate(features):
            card = ctk.CTkFrame(cards_frame, width=220, height=140)
            card.grid(row=i//3, column=i%3, padx=10, pady=10)
            card.grid_propagate(False)
            
            icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=40))
            icon_label.pack(pady=(20, 10))
            
            title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold"))
            title_label.pack()
            
            desc_label = ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12), text_color="gray60", wraplength=220)
            desc_label.pack(pady=10)
        
        # Dica
        tip = ctk.CTkLabel(
            frame,
            text="💡 Dica: Salve perfis para reutilizar configurações em processos recorrentes",
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
        
        # Mostrar frame da ferramenta
        self.tool_frames[tool_id].pack(fill="both", expand=True)
        self.current_frame = self.tool_frames[tool_id]
        
        # Destacar botão ativo
        for btn_id, btn in self.tool_buttons.items():
            if btn_id == tool_id:
                btn.configure(fg_color=("gray70", "gray30"))
            else:
                btn.configure(fg_color=("gray70", "gray25"))
    
    def update_profiles_list(self):
        """Atualiza a lista de perfis na sidebar"""
        # Limpar lista atual
        for widget in self.profiles_frame.winfo_children():
            widget.destroy()
        
        # Adicionar perfis
        profiles = self.config.get("profiles", {})
        
        if not profiles:
            no_profiles = ctk.CTkLabel(
                self.profiles_frame,
                text="Nenhum perfil salvo",
                text_color="gray50"
            )
            no_profiles.pack(pady=10)
        else:
            for profile_name, profile_data in profiles.items():
                profile_btn = ctk.CTkButton(
                    self.profiles_frame,
                    text=f"📋 {profile_name}",
                    command=lambda p=profile_name: self.load_profile(p),
                    height=30,
                    fg_color="transparent",
                    hover_color="gray30",
                    anchor="w"
                )
                profile_btn.pack(fill="x", pady=2)
    
    def create_new_profile(self):
        """Abre diálogo para criar novo perfil"""
        dialog = ctk.CTkInputDialog(
            text="Nome do novo perfil:",
            title="Criar Perfil"
        )
        profile_name = dialog.get_input()
        
        if profile_name:
            if profile_name in self.config["profiles"]:
                messagebox.showwarning("Aviso", "Já existe um perfil com esse nome!")
            else:
                self.config["profiles"][profile_name] = {
                    "tool": None,
                    "settings": {}
                }
                self.save_config()
                self.update_profiles_list()
                messagebox.showinfo("Sucesso", f"Perfil '{profile_name}' criado!")
    
    def load_profile(self, profile_name):
        """Carrega um perfil salvo"""
        profile = self.config["profiles"].get(profile_name)
        if profile and profile.get("tool"):
            self.show_tool(profile["tool"])
            # Carregar configurações no frame da ferramenta
            if profile["tool"] in self.tool_frames:
                self.tool_frames[profile["tool"]].load_settings(profile.get("settings", {}))
    
    def show_settings(self):
        """Mostra janela de configurações"""
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Configurações")
        settings_window.geometry("500x400")
        settings_window.transient(self)
        settings_window.grab_set()
        
        # Título
        title = ctk.CTkLabel(
            settings_window,
            text="⚙️ Configurações",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Frame de configurações
        settings_frame = ctk.CTkFrame(settings_window)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tema
        theme_label = ctk.CTkLabel(settings_frame, text="Tema:", font=ctk.CTkFont(size=14))
        theme_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        theme_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["Dark", "Light", "System"],
            variable=theme_var,
            command=lambda v: ctk.set_appearance_mode(v.lower())
        )
        theme_menu.grid(row=0, column=1, padx=20, pady=15)
        
        # Encoding padrão
        enc_label = ctk.CTkLabel(settings_frame, text="Encoding Padrão:", font=ctk.CTkFont(size=14))
        enc_label.grid(row=1, column=0, padx=20, pady=15, sticky="w")
        
        enc_var = ctk.StringVar(value=self.config["settings"].get("default_encoding", "utf-8"))
        enc_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["utf-8", "latin-1", "windows-1252", "iso-8859-1"],
            variable=enc_var
        )
        enc_menu.grid(row=1, column=1, padx=20, pady=15)
        
        # Separador padrão
        sep_label = ctk.CTkLabel(settings_frame, text="Separador Padrão:", font=ctk.CTkFont(size=14))
        sep_label.grid(row=2, column=0, padx=20, pady=15, sticky="w")
        
        sep_var = ctk.StringVar(value=self.config["settings"].get("default_separator", ";"))
        sep_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=[";", ",", "|", "\\t"],
            variable=sep_var
        )
        sep_menu.grid(row=2, column=1, padx=20, pady=15)
        
        # Botão Salvar
        def save_settings():
            self.config["settings"]["default_encoding"] = enc_var.get()
            self.config["settings"]["default_separator"] = sep_var.get()
            self.save_config()
            settings_window.destroy()
            messagebox.showinfo("Sucesso", "Configurações salvas!")
        
        save_btn = ctk.CTkButton(
            settings_window,
            text="Salvar",
            command=save_settings,
            height=40
        )
        save_btn.pack(pady=20)


def main():
    app = CSVToolBox()
    app.mainloop()


if __name__ == "__main__":
    main()
