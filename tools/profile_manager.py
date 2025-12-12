# Profile Manager - Gerenciador de Perfis de Configuração

import json
from pathlib import Path
from datetime import datetime

class ProfileManager:
    """Gerencia perfis de configuração para processos recorrentes"""
    
    def __init__(self, config: dict):
        self.config = config
        
    def get_profiles(self) -> dict:
        """Retorna todos os perfis"""
        return self.config.get("profiles", {})
    
    def get_profile(self, name: str) -> dict:
        """Retorna um perfil específico"""
        return self.config.get("profiles", {}).get(name, {})
    
    def save_profile(self, name: str, tool: str, settings: dict):
        """Salva um perfil com as configurações"""
        if "profiles" not in self.config:
            self.config["profiles"] = {}
        
        self.config["profiles"][name] = {
            "tool": tool,
            "settings": settings,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def update_profile(self, name: str, settings: dict):
        """Atualiza as configurações de um perfil existente"""
        if name in self.config.get("profiles", {}):
            self.config["profiles"][name]["settings"] = settings
            self.config["profiles"][name]["updated_at"] = datetime.now().isoformat()
    
    def delete_profile(self, name: str) -> bool:
        """Remove um perfil"""
        if name in self.config.get("profiles", {}):
            del self.config["profiles"][name]
            return True
        return False
    
    def duplicate_profile(self, original_name: str, new_name: str) -> bool:
        """Duplica um perfil existente"""
        original = self.get_profile(original_name)
        if original:
            self.config["profiles"][new_name] = {
                **original,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            return True
        return False
    
    def export_profile(self, name: str, filepath: Path) -> bool:
        """Exporta um perfil para arquivo JSON"""
        profile = self.get_profile(name)
        if profile:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({name: profile}, f, indent=4, ensure_ascii=False)
                return True
            except Exception:
                return False
        return False
    
    def import_profile(self, filepath: Path) -> bool:
        """Importa um perfil de arquivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for name, profile in data.items():
                self.config["profiles"][name] = profile
            return True
        except Exception:
            return False
