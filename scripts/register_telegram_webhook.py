import sys
import json
import urllib.request
import os

def get_token():
    # 1. Environment
    if "TELEGRAM_BOT_TOKEN" in os.environ:
        return os.environ["TELEGRAM_BOT_TOKEN"]
    # 2. secrets.toml
    try:
        import toml
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".streamlit", "secrets.toml")
        if os.path.exists(path):
            sec = toml.load(path)
            return sec.get("TELEGRAM_BOT_TOKEN", "")
    except Exception:
        pass
    return ""

def set_webhook(url: str):
    token = get_token()
    api_url = f"https://api.telegram.org/bot{token}/setWebhook"
    payload = {
        "url": url,
        "drop_pending_updates": True
    }
    
    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("Respuesta de Telegram setWebhook:")
        print(json.dumps(res, indent=2))
        return res.get("ok", False)

def get_webhook_info():
    token = get_token()
    api_url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    with urllib.request.urlopen(api_url, timeout=10) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("\nEstado actual del Webhook:")
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        webhook_url = sys.argv[1].strip()
        print(f"Registrando Webhook: {webhook_url}")
        success = set_webhook(webhook_url)
        if success:
            print("\n¡Webhook registrado exitosamente en Telegram!")
        get_webhook_info()
    else:
        print("Uso: python scripts/register_telegram_webhook.py <URL_DEL_WEB_APP>")
        get_webhook_info()
