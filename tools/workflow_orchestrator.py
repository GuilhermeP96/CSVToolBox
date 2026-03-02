# Workflow Orchestrator Tool - Visualizador e Executor de Workflows

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime

# PyAccelerate — thread pool
from pyaccelerate.threads import submit as pa_submit

# Importar gerenciador de workflow
from tools.workflow_manager import workflow_manager

# Importar sistema de internacionalização
try:
    from i18n import t
except ImportError:
    def t(key):
        return key


class WorkflowOrchestratorTool(ctk.CTkFrame):
    """Ferramenta para visualizar e executar workflows"""
    
    def __init__(self, parent, profile_manager):
        super().__init__(parent)
        self.profile_manager = profile_manager
        self.is_running = False
        self.current_step = 0
        
        # Registrar como listener do WorkflowManager
        workflow_manager.add_listener(self.on_workflow_changed)
        
        self.create_widgets()
        self.update_queue_display()
        
    def create_widgets(self):
        """Cria os widgets da ferramenta"""
        
        # === Container Principal Scrollable ===
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Cabeçalho ===
        header = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        title = ctk.CTkLabel(
            header,
            text="🔀 " + t("tool_workflow"),
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(side="left")
        
        # Contador de etapas
        self.step_counter = ctk.CTkLabel(
            header,
            text=f"({workflow_manager.get_step_count()} {t('steps')})",
            font=ctk.CTkFont(size=14),
            text_color="gray50"
        )
        self.step_counter.pack(side="left", padx=15)
        
        # === Instruções ===
        instructions_frame = ctk.CTkFrame(self.main_scroll, fg_color="gray20")
        instructions_frame.pack(fill="x", pady=(0, 15))
        
        instructions = ctk.CTkLabel(
            instructions_frame,
            text="💡 " + t("workflow_instructions"),
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            wraplength=800,
            justify="left"
        )
        instructions.pack(padx=15, pady=10, anchor="w")
        
        # === Gerenciamento de Workflows ===
        mgmt_frame = ctk.CTkFrame(self.main_scroll)
        mgmt_frame.pack(fill="x", pady=(0, 15))
        
        mgmt_label = ctk.CTkLabel(
            mgmt_frame, 
            text=t("workflow_management"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        mgmt_label.pack(anchor="w", padx=15, pady=10)
        
        btn_frame = ctk.CTkFrame(mgmt_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.btn_load_workflow = ctk.CTkButton(
            btn_frame,
            text="📂 " + t("load_workflow"),
            command=self.load_workflow,
            width=140,
            height=32
        )
        self.btn_load_workflow.pack(side="left", padx=5)
        
        self.btn_save_workflow = ctk.CTkButton(
            btn_frame,
            text="💾 " + t("save_workflow"),
            command=self.save_workflow,
            width=140,
            height=32,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_save_workflow.pack(side="left", padx=5)
        
        self.btn_clear_queue = ctk.CTkButton(
            btn_frame,
            text="🗑️ " + t("clear_queue"),
            command=self.clear_queue,
            width=140,
            height=32,
            fg_color="gray30",
            hover_color="gray40"
        )
        self.btn_clear_queue.pack(side="left", padx=5)
        
        # Nome do workflow
        name_frame = ctk.CTkFrame(mgmt_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        name_label = ctk.CTkLabel(name_frame, text=t("workflow_name") + ":")
        name_label.pack(side="left")
        
        self.workflow_name_entry = ctk.CTkEntry(name_frame, width=300, placeholder_text=t("workflow_name_hint"))
        self.workflow_name_entry.pack(side="left", padx=10)
        
        # === Fila de Execução ===
        queue_label = ctk.CTkLabel(
            self.main_scroll,
            text="📋 " + t("execution_queue"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        queue_label.pack(anchor="w", pady=(10, 5))
        
        # Container da fila
        self.queue_container = ctk.CTkFrame(self.main_scroll)
        self.queue_container.pack(fill="x", pady=(0, 15))
        
        # Lista de etapas (será preenchida dinamicamente)
        self.queue_frame = ctk.CTkFrame(self.queue_container, fg_color="transparent")
        self.queue_frame.pack(fill="x", padx=10, pady=10)
        
        # === Controles de Execução ===
        exec_frame = ctk.CTkFrame(self.main_scroll)
        exec_frame.pack(fill="x", pady=(0, 15))
        
        exec_label = ctk.CTkLabel(
            exec_frame,
            text=t("execution_controls"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        exec_label.pack(anchor="w", padx=15, pady=10)
        
        # Botões de controle
        ctrl_frame = ctk.CTkFrame(exec_frame, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.btn_run_all = ctk.CTkButton(
            ctrl_frame,
            text="▶️ " + t("run_all"),
            command=self.run_all_steps,
            height=45,
            width=180,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_run_all.pack(side="left", padx=5)
        
        self.btn_stop = ctk.CTkButton(
            ctrl_frame,
            text="⏹️ " + t("stop"),
            command=self.stop_execution,
            height=45,
            width=120,
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.btn_stop.pack(side="left", padx=5)
        
        # Barra de progresso
        progress_frame = ctk.CTkFrame(exec_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=10)
        
        self.progress_var = ctk.DoubleVar(value=0)
        self.progress_bar = ctk.CTkProgressBar(progress_frame, variable=self.progress_var, height=20)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text=t("ready"), text_color="gray50")
        self.progress_label.pack()
        
        # === Log de Execução ===
        log_frame = ctk.CTkFrame(self.main_scroll)
        log_frame.pack(fill="x", pady=(0, 10))
        
        log_label = ctk.CTkLabel(
            log_frame,
            text=t("execution_log"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        log_label.pack(anchor="w", padx=15, pady=10)
        
        self.log_text = ctk.CTkTextbox(log_frame, height=150)
        self.log_text.pack(fill="x", padx=15, pady=(0, 15))
        
    def on_workflow_changed(self):
        """Callback quando o workflow é modificado"""
        self.after(0, self.update_queue_display)
        
    def update_queue_display(self):
        """Atualiza a exibição da fila"""
        # Limpar widgets existentes
        for widget in self.queue_frame.winfo_children():
            widget.destroy()
            
        steps = workflow_manager.get_steps()
        
        # Atualizar contador
        self.step_counter.configure(text=f"({len(steps)} {t('steps')})")
        
        if not steps:
            placeholder = ctk.CTkLabel(
                self.queue_frame,
                text=t("queue_empty_instruction"),
                text_color="gray50",
                font=ctk.CTkFont(size=12),
                wraplength=600
            )
            placeholder.pack(pady=30)
            return
            
        # Criar cards para cada etapa
        for i, step in enumerate(steps):
            self._create_step_card(i, step)
            
    def _create_step_card(self, index, step):
        """Cria um card para uma etapa"""
        # Cores baseadas no status
        status_colors = {
            "pending": ("gray25", "⏳"),
            "running": ("blue", "🔄"),
            "completed": ("green", "✅"),
            "error": ("red", "❌")
        }
        
        bg_color, status_icon = status_colors.get(step["status"], ("gray25", "⏳"))
        
        card = ctk.CTkFrame(self.queue_frame, fg_color=bg_color)
        card.pack(fill="x", pady=5)
        
        # Header do card
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=10)
        
        # Número e nome
        step_info = ctk.CTkFrame(header, fg_color="transparent")
        step_info.pack(side="left", fill="x", expand=True)
        
        step_num = ctk.CTkLabel(
            step_info,
            text=f"#{step['id']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=35
        )
        step_num.pack(side="left")
        
        tool_label = ctk.CTkLabel(
            step_info,
            text=step["tool_name"],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        tool_label.pack(side="left", padx=10)
        
        status_label = ctk.CTkLabel(
            step_info,
            text=status_icon,
            font=ctk.CTkFont(size=18)
        )
        status_label.pack(side="left", padx=10)
        
        # Botões de ação
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        btn_up = ctk.CTkButton(
            btn_frame,
            text="↑",
            command=lambda idx=index: self.move_step_up(idx),
            width=30,
            height=30,
            fg_color="gray40"
        )
        btn_up.pack(side="left", padx=2)
        
        btn_down = ctk.CTkButton(
            btn_frame,
            text="↓",
            command=lambda idx=index: self.move_step_down(idx),
            width=30,
            height=30,
            fg_color="gray40"
        )
        btn_down.pack(side="left", padx=2)
        
        btn_remove = ctk.CTkButton(
            btn_frame,
            text="✖",
            command=lambda idx=index: self.remove_step(idx),
            width=30,
            height=30,
            fg_color="red",
            hover_color="darkred"
        )
        btn_remove.pack(side="left", padx=2)
        
        # Detalhes
        details = ctk.CTkFrame(card, fg_color="transparent")
        details.pack(fill="x", padx=15, pady=(0, 10))
        
        input_text = t("previous_output") if step.get("use_previous_output") else os.path.basename(step.get("input_file", "-") or "-")
        output_text = os.path.basename(step.get("output_file", "-") or "-")
        
        ctk.CTkLabel(details, text=f"📥 {t('input')}: {input_text}", font=ctk.CTkFont(size=11), text_color="gray60").pack(anchor="w")
        ctk.CTkLabel(details, text=f"📤 {t('output')}: {output_text}", font=ctk.CTkFont(size=11), text_color="gray60").pack(anchor="w")
        
        # Mostrar algumas configurações
        config = step.get("config", {})
        if config:
            config_preview = ", ".join([f"{k}: {v}" for k, v in list(config.items())[:3]])
            if len(config) > 3:
                config_preview += "..."
            ctk.CTkLabel(details, text=f"⚙️ {config_preview}", font=ctk.CTkFont(size=10), text_color="gray50").pack(anchor="w")
        
    def move_step_up(self, index):
        """Move etapa para cima"""
        workflow_manager.move_step_up(index)
        
    def move_step_down(self, index):
        """Move etapa para baixo"""
        workflow_manager.move_step_down(index)
        
    def remove_step(self, index):
        """Remove uma etapa"""
        removed = workflow_manager.remove_step(index)
        if removed:
            self.log(f"🗑️ {t('step_removed')}: {removed['tool_name']}")
            
    def clear_queue(self):
        """Limpa a fila de execução"""
        if workflow_manager.get_step_count() > 0:
            if messagebox.askyesno(t("confirm"), t("clear_queue_confirm")):
                workflow_manager.clear_steps()
                self.log(f"🗑️ {t('queue_cleared')}")
                
    def save_workflow(self):
        """Salva o workflow atual"""
        name = self.workflow_name_entry.get().strip()
        if not name:
            messagebox.showwarning(t("warning"), t("enter_workflow_name"))
            return
            
        if workflow_manager.get_step_count() == 0:
            messagebox.showwarning(t("warning"), t("add_steps_first"))
            return
            
        try:
            filepath = workflow_manager.save_workflow(name)
            self.log(f"💾 {t('workflow_saved')}: {filepath}")
            messagebox.showinfo(t("success"), f"{t('workflow_saved')}\n{filepath}")
        except Exception as e:
            messagebox.showerror(t("error"), str(e))
            
    def load_workflow(self):
        """Carrega um workflow salvo"""
        filepath = filedialog.askopenfilename(
            title=t("load_workflow"),
            initialdir=str(workflow_manager.workflows_dir),
            filetypes=[("Workflow files", "*.workflow.json"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return
            
        try:
            workflow = workflow_manager.load_workflow(filepath)
            self.workflow_name_entry.delete(0, "end")
            self.workflow_name_entry.insert(0, workflow.get("name", ""))
            self.log(f"📂 {t('workflow_loaded')}: {workflow.get('name', 'Unknown')}")
        except Exception as e:
            messagebox.showerror(t("error"), str(e))
            
    def run_all_steps(self):
        """Executa todas as etapas"""
        if workflow_manager.get_step_count() == 0:
            messagebox.showwarning(t("warning"), t("add_steps_first"))
            return
            
        # Resetar status
        workflow_manager.reset_all_status()
        
        # Iniciar execução em thread
        self.is_running = True
        self.btn_stop.configure(state="normal")
        self.btn_run_all.configure(state="disabled")
        
        pa_submit(self._execute_all_steps)
        
    def _execute_all_steps(self):
        """Executa todas as etapas em sequência"""
        steps = workflow_manager.get_steps()
        total = len(steps)
        previous_output = None
        
        for i, step in enumerate(steps):
            if not self.is_running:
                self.log(f"⏹️ {t('execution_stopped')}")
                break
                
            self.current_step = i
            workflow_manager.update_step_status(i, "running")
            
            # Atualizar progresso
            progress = (i / total)
            self.after(0, lambda p=progress: self.progress_var.set(p))
            self.after(0, lambda s=step, idx=i: self.progress_label.configure(
                text=f"{t('running')}: {s['tool_name']} ({idx+1}/{total})"
            ))
            
            # Determinar arquivo de entrada
            input_file = previous_output if step.get("use_previous_output") else step.get("input_file")
            
            self.log(f"🔄 {t('executing_step')} #{step['id']}: {step['tool_name']}")
            
            try:
                result = self._execute_single_step(step, input_file)
                
                if result["success"]:
                    workflow_manager.update_step_status(i, "completed")
                    previous_output = step.get("output_file")
                    self.log(f"✅ {t('step_completed')}: {step['tool_name']} ({result.get('rows', '?')} {t('rows')})")
                else:
                    workflow_manager.update_step_status(i, "error")
                    self.log(f"❌ {t('step_failed')}: {result.get('error', 'Unknown error')}")
                    break
                    
            except Exception as e:
                workflow_manager.update_step_status(i, "error")
                self.log(f"❌ {t('error')}: {e}")
                break
                
        # Finalizar
        all_completed = all(s["status"] == "completed" for s in workflow_manager.get_steps())
        self.after(0, lambda: self.progress_var.set(1 if all_completed else self.progress_var.get()))
        self.after(0, lambda: self.progress_label.configure(
            text=t("completed") if all_completed else t("finished_with_errors")
        ))
        
        self.is_running = False
        self.after(0, lambda: self.btn_stop.configure(state="disabled"))
        self.after(0, lambda: self.btn_run_all.configure(state="normal"))
        
    def _execute_single_step(self, step, input_file):
        """Executa uma única etapa do workflow"""
        output_file = step.get("output_file")
        config = step.get("config", {})
        
        # Obter separador e encoding
        sep = config.get("separator", ";")
        if sep == "\\t":
            sep = "\t"
        encoding = config.get("encoding", "utf-8")
        
        try:
            # Carregar dados
            if not input_file:
                return {"success": False, "error": t("no_input_file")}
                
            if input_file.endswith('.xlsx') or input_file.endswith('.xls'):
                df = pd.read_excel(input_file)
            else:
                df = pd.read_csv(input_file, sep=sep, encoding=encoding)
                
            # Aplicar transformações baseadas na ferramenta
            df = self._apply_tool_transformations(step["tool_id"], df, config)
            
            # Salvar resultado
            if output_file:
                df.to_csv(output_file, sep=sep, index=False, encoding="utf-8")
            
            return {"success": True, "rows": len(df)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def _apply_tool_transformations(self, tool_id, df, config):
        """Aplica transformações baseadas na ferramenta"""
        
        if tool_id == "cleaner":
            # Limpar espaços
            if config.get("trim_spaces", True):
                for col in df.select_dtypes(include=['object']).columns:
                    df[col] = df[col].astype(str).str.strip()
                    
        elif tool_id == "transformer":
            # Aplicar mapeamentos de coluna
            if "column_mapping" in config:
                df = df.rename(columns=config["column_mapping"])
                
        elif tool_id == "verticalizer":
            # Aplicar verticalização
            fixed_cols = config.get("fixed_columns", [])
            value_vars = config.get("value_columns", [])
            if value_vars:
                df = pd.melt(
                    df,
                    id_vars=fixed_cols,
                    value_vars=value_vars,
                    var_name=config.get("var_name", "PERIODO"),
                    value_name=config.get("val_name", "VALOR")
                )
                
        # Opções comuns
        if config.get("remove_duplicates"):
            df = df.drop_duplicates()
            
        if config.get("remove_empty_rows"):
            df = df.dropna(how='all')
            
        return df
        
    def stop_execution(self):
        """Para a execução"""
        self.is_running = False
        self.btn_stop.configure(state="disabled")
        self.log(f"⏹️ {t('stopping_execution')}...")
        
    def log(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        
    def get_settings(self):
        """Retorna configurações atuais para salvar perfil"""
        return {
            "workflow_name": self.workflow_name_entry.get()
        }
        
    def load_settings(self, settings):
        """Carrega configurações de um perfil"""
        if "workflow_name" in settings:
            self.workflow_name_entry.delete(0, "end")
            self.workflow_name_entry.insert(0, settings["workflow_name"])
            
    def destroy(self):
        """Cleanup ao destruir"""
        workflow_manager.remove_listener(self.on_workflow_changed)
        super().destroy()
