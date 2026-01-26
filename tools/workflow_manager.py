# Workflow Manager - Gerenciador Global de Etapas de Workflow

import json
import os
from pathlib import Path
from datetime import datetime
import copy

class WorkflowManager:
    """Singleton para gerenciar etapas do workflow globalmente"""
    
    _instance = None
    _listeners = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.steps = []
        self.workflows_dir = Path(os.path.expanduser("~")) / "Documents" / "CSVToolBox" / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
    def add_step(self, tool_id: str, tool_name: str, input_file: str, output_file: str, 
                 config: dict, use_previous_output: bool = False):
        """Adiciona uma etapa ao workflow"""
        step = {
            "id": len(self.steps) + 1,
            "tool_id": tool_id,
            "tool_name": tool_name,
            "input_file": input_file,
            "output_file": output_file,
            "use_previous_output": use_previous_output,
            "config": copy.deepcopy(config),
            "status": "pending",
            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.steps.append(step)
        self._notify_listeners()
        return step
        
    def remove_step(self, index: int):
        """Remove uma etapa pelo índice"""
        if 0 <= index < len(self.steps):
            removed = self.steps.pop(index)
            self._renumber_steps()
            self._notify_listeners()
            return removed
        return None
        
    def move_step_up(self, index: int):
        """Move etapa para cima"""
        if index > 0:
            self.steps[index], self.steps[index-1] = self.steps[index-1], self.steps[index]
            self._renumber_steps()
            self._notify_listeners()
            
    def move_step_down(self, index: int):
        """Move etapa para baixo"""
        if index < len(self.steps) - 1:
            self.steps[index], self.steps[index+1] = self.steps[index+1], self.steps[index]
            self._renumber_steps()
            self._notify_listeners()
            
    def clear_steps(self):
        """Limpa todas as etapas"""
        self.steps = []
        self._notify_listeners()
        
    def get_steps(self):
        """Retorna lista de etapas"""
        return self.steps
        
    def get_step_count(self):
        """Retorna quantidade de etapas"""
        return len(self.steps)
        
    def _renumber_steps(self):
        """Renumera as etapas"""
        for i, step in enumerate(self.steps):
            step["id"] = i + 1
            
    def update_step_status(self, index: int, status: str):
        """Atualiza status de uma etapa"""
        if 0 <= index < len(self.steps):
            self.steps[index]["status"] = status
            self._notify_listeners()
            
    def reset_all_status(self):
        """Reseta status de todas as etapas para pending"""
        for step in self.steps:
            step["status"] = "pending"
        self._notify_listeners()
            
    # === Listeners para notificar UI ===
    def add_listener(self, callback):
        """Adiciona listener para mudanças"""
        if callback not in self._listeners:
            self._listeners.append(callback)
            
    def remove_listener(self, callback):
        """Remove listener"""
        if callback in self._listeners:
            self._listeners.remove(callback)
            
    def _notify_listeners(self):
        """Notifica todos os listeners"""
        for callback in self._listeners:
            try:
                callback()
            except Exception as e:
                print(f"[WorkflowManager] Erro ao notificar listener: {e}")
                
    # === Persistência ===
    def save_workflow(self, name: str) -> str:
        """Salva workflow atual em arquivo"""
        workflow = {
            "name": name,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "steps": copy.deepcopy(self.steps)
        }
        # Resetar status no arquivo salvo
        for step in workflow["steps"]:
            step["status"] = "pending"
            
        filepath = self.workflows_dir / f"{name}.workflow.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=4, ensure_ascii=False)
        return str(filepath)
        
    def load_workflow(self, filepath: str) -> dict:
        """Carrega workflow de arquivo"""
        with open(filepath, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        self.steps = workflow.get("steps", [])
        self._renumber_steps()
        self._notify_listeners()
        return workflow
        
    def list_saved_workflows(self) -> list:
        """Lista workflows salvos"""
        workflows = []
        for f in self.workflows_dir.glob("*.workflow.json"):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    workflows.append({
                        "name": data.get("name", f.stem),
                        "path": str(f),
                        "created": data.get("created", ""),
                        "steps_count": len(data.get("steps", []))
                    })
            except:
                pass
        return workflows


# Instância global
workflow_manager = WorkflowManager()
