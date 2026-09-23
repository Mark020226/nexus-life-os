import os
import sys
import time
import json
import urllib.request
import urllib.parse
from typing import Optional
from datetime import datetime

# Ensure repository root is in sys.path
def get_project_root():
    if "NEXUS_ROOT" in os.environ and os.path.exists(os.environ["NEXUS_ROOT"]):
        return os.path.abspath(os.environ["NEXUS_ROOT"])
    cur = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    for _ in range(5):
        if os.path.exists(os.path.join(cur, "requirements.txt")) and (
            os.path.exists(os.path.join(cur, "src")) or os.path.exists(os.path.join(cur, "data"))
        ):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return cur

ROOT_DIR = get_project_root()
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.integrations.telegram_bot import TelegramNEXUSAssistant

def get_secret(key, default=""):
    # 1. Environment variable
    if key in os.environ:
        return os.environ[key]
    # 2. .streamlit/secrets.toml
    secrets_file = os.path.join(ROOT_DIR, ".streamlit", "secrets.toml")
    if os.path.exists(secrets_file):
        try:
            import toml
            data = toml.load(secrets_file)
            if key in data:
                return data[key]
        except Exception:
            pass
    return default

DB_PATH = os.path.join(ROOT_DIR, "data", "nexus.db")
BOT_TOKEN = get_secret("TELEGRAM_BOT_TOKEN", "")
GEMINI_KEY = get_secret("GEMINI_API_KEY", "")

assistant = TelegramNEXUSAssistant(DB_PATH, GEMINI_KEY)

def send_telegram_message(chat_id: int, text: str):
    """Envía un mensaje de respuesta formateado a un chat de Telegram."""
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        # Si falla por parse_mode Markdown, enviar como texto plano
        payload.pop("parse_mode", None)
        try:
            req_plain = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req_plain, timeout=10) as r:
                return r.status == 200
        except Exception:
            return False
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")
        return False

def transcribe_voice_with_gemini(file_id: str) -> Optional[str]:
    """Descarga una nota de voz de Telegram y la transcribe usando Gemini 3.6 Flash."""
    if not GEMINI_KEY:
        return None
    try:
        # 1. Obtener file_path de Telegram API
        get_file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
        req = urllib.request.Request(get_file_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            file_info = json.loads(resp.read().decode('utf-8'))
        file_path = file_info.get("result", {}).get("file_path")
        if not file_path:
            return None

        # 2. Descargar bytes de audio
        download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        with urllib.request.urlopen(download_url, timeout=15) as resp:
            audio_bytes = resp.read()

        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        mime_type = "audio/ogg" if file_path.endswith((".oga", ".ogg")) else "audio/mp3"

        # 3. Transcribir con Gemini 3.6 Flash
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_KEY}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": audio_b64
                            }
                        },
                        {
                            "text": (
                                "Eres el transcriptor inteligente de NEXUS Life OS para Mark Eduardo Terrazas Luna (estudiante de Ingeniería Industrial UMSA, estudiante de GCI World Universidad de Tokio). "
                                "Transcribe con la máxima precisión lo que dice esta nota de voz en español boliviano/latinoamericano. "
                                "Si menciona materias (Taller 1, Seguridad Industrial, Gerencia, Diseño Industrial, Empresa, GCI World, Inglés) o actividades/imprevistos/gastos, asegúrate de escribirlo fielmente. "
                                "Devuelve ÚNICAMENTE el texto transcrito directo, sin explicaciones ni comillas adicionales."
                            )
                        }
                    ]
                }
            ]
        }
        gemini_req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(gemini_req, timeout=20) as r:
            data = json.loads(r.read().decode('utf-8'))
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
    except Exception as e:
        print(f"Error transcribiendo nota de voz con Gemini: {e}")
    return None

def handle_telegram_update(update: dict):
    """Procesa una actualización individual recibida desde Telegram (Polling o Webhook)."""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    chat_id = message.get("chat", {}).get("id")
    if not chat_id:
        return

    text = message.get("text", "")
    caption = message.get("caption", "")
    voice = message.get("voice") or message.get("audio")

    is_voice = False
    input_text = ""

    if voice:
        file_id = voice.get("file_id")
        if file_id:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Nota de voz recibida de {chat_id}. Transcribiendo...")
            send_telegram_message(chat_id, "🎙️ _Escuchando tu nota de voz con IA..._")
            input_text = transcribe_voice_with_gemini(file_id)
            is_voice = True

    if not input_text:
        input_text = text or caption or ""

    if not input_text:
        if is_voice:
            send_telegram_message(chat_id, "⚠️ No pude escuchar con claridad el audio. Intenta hablar más cerca del micrófono o escribe el texto.")
        return

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Mensaje procesado de {chat_id}: {input_text}")
    
    # Procesar con el asistente
    try:
        reply = assistant.process_message(input_text, user_id=str(chat_id))
    except Exception as e:
        reply = f"⚠️ Ocurrió un error procesando tu mensaje: {e}"

    if is_voice:
        reply = f"🎙️ *Nota de voz:* \"_{input_text}_\"\n\n" + reply

    # Enviar respuesta
    send_telegram_message(chat_id, reply)

def poll_telegram(once=False):
    """Realiza un ciclo de consulta de actualizaciones a la API de Telegram."""
    offset = 0
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    
    try:
        req = urllib.request.Request(f"{api_url}?offset={offset}&timeout=5")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                results = data.get("result", [])
                for upd in results:
                    upd_id = upd.get("update_id", 0)
                    handle_telegram_update(upd)
                    offset = max(offset, upd_id + 1)
                
                # Confirmar lectura de actualizaciones
                if results and offset > 0:
                    urllib.request.urlopen(f"{api_url}?offset={offset}&timeout=1")
    except Exception as e:
        print(f"Error en polling de Telegram: {e}")

if __name__ == "__main__":
    print(f"Iniciando servicio de Telegram para @HAZARDNexusbot...")
    poll_telegram(once=True)
    print("Verificación de Telegram completada.")
