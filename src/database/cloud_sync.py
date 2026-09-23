import os
import json
import sqlite3
import urllib.request
import base64
from typing import Dict, Any, Optional

def export_db_to_json(db_path: str, json_path: str) -> bool:
    """Exporta los registros canónicos de resources a JSON como respaldo plano permanente."""
    try:
        if not os.path.exists(db_path):
            return False
            
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM resources ORDER BY id DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error exportando DB a JSON: {e}")
        return False

def sync_to_github(file_path: str, repo: str = "Mark020226/nexus-life-os", branch: str = "main", token: Optional[str] = None) -> bool:
    """Sincroniza un archivo modificado con el repositorio de GitHub mediante la API REST si hay un token disponible."""
    if not token or not os.path.exists(file_path):
        return False
        
    rel_path = os.path.relpath(file_path, os.path.dirname(os.path.dirname(os.path.dirname(file_path))))
    # Normalizar separadores a '/'
    rel_path = rel_path.replace("\\", "/")
    
    api_url = f"https://api.github.com/repos/{repo}/contents/{rel_path}"
    
    try:
        # 1. Obtener el SHA actual del archivo si existe
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "NEXUS-Life-OS-CloudSync"
        }
        
        sha = None
        req = urllib.request.Request(f"{api_url}?ref={branch}", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    sha = data.get("sha")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                print(f"Aviso obteniendo SHA de {rel_path}: {e}")
                
        # 2. Leer contenido y codificar en base64
        with open(file_path, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode('utf-8')
            
        payload = {
            "message": f"sync(cloud): backup {rel_path} from NEXUS Life OS",
            "content": content_b64,
            "branch": branch
        }
        if sha:
            payload["sha"] = sha
            
        req_put = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method="PUT"
        )
        with urllib.request.urlopen(req_put, timeout=10) as resp:
            return resp.status in (200, 201)
    except Exception as e:
        print(f"Error sincronizando con GitHub: {e}")
        return False
