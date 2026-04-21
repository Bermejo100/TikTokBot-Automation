# uploaders/tiktok_uploader.py
import os
import time
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# OPCIÓN 1 — SIN API (Playwright) — funciona ahora mismo
# ============================================================

def subir_tiktok_playwright(ruta_video: str, descripcion: str) -> bool:
    """Sube video a TikTok automatizando el navegador"""
    try:
        from playwright.sync_api import sync_playwright
        
        email = os.getenv("TIKTOK_EMAIL")
        password = os.getenv("TIKTOK_PASSWORD")
        
        if not email or not password:
            print("❌ Faltan credenciales de TikTok en .env")
            return False

        with sync_playwright() as p:
            # headless=False para ver el navegador (útil para debug)
            # headless=True para que vaya en segundo plano
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            print("🌐 Abriendo TikTok...")
            page.goto("https://www.tiktok.com/login/phone-or-email/email")
            time.sleep(3)

            # Login
            print("🔑 Iniciando sesión...")
            page.fill('input[name="username"]', email)
            time.sleep(1)
            page.fill('input[type="password"]', password)
            time.sleep(1)
            page.click('button[type="submit"]')
            time.sleep(8)

            # Ir a subir video
            print("📤 Yendo a subir video...")
            page.goto("https://www.tiktok.com/upload")
            time.sleep(5)

            # Subir archivo
            ruta_absoluta = os.path.abspath(ruta_video)
            page.set_input_files('input[type="file"]', ruta_absoluta)
            time.sleep(8)

            # Añadir descripción
            print("✍️ Añadiendo descripción...")
            try:
                editor = page.locator('div[contenteditable="true"]').first
                editor.click()
                editor.fill(descripcion)
            except:
                pass
            time.sleep(2)

            # Publicar
            print("🚀 Publicando...")
            try:
                page.click('button:has-text("Post")')
            except:
                page.click('button:has-text("Publicar")')
            time.sleep(10)

            print("✅ Video subido a TikTok")
            browser.close()
            return True

    except Exception as e:
        print(f"❌ Error subiendo a TikTok: {e}")
        return False


# ============================================================
# OPCIÓN 2 — CON API OFICIAL de TikTok
# Requiere aprobación en developers.tiktok.com
# ============================================================

def subir_tiktok_api(ruta_video: str, descripcion: str) -> bool:
    """Sube video a TikTok usando la API oficial"""
    try:
        import requests

        client_key = os.getenv("TIKTOK_CLIENT_KEY")
        access_token = os.getenv("TIKTOK_ACCESS_TOKEN")

        if not client_key or not access_token:
            print("❌ Faltan credenciales de API de TikTok en .env")
            print("   Necesitas: TIKTOK_CLIENT_KEY y TIKTOK_ACCESS_TOKEN")
            return False

        # Paso 1 — Iniciar subida
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        init_response = requests.post(
            "https://open.tiktokapis.com/v2/post/publish/video/init/",
            headers=headers,
            json={
                "post_info": {
                    "title": descripcion[:150],
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": os.path.getsize(ruta_video),
                    "chunk_size": os.path.getsize(ruta_video),
                    "total_chunk_count": 1
                }
            }
        )

        data = init_response.json()
        
        if "data" not in data:
            print(f"❌ Error iniciando subida: {data}")
            return False

        upload_url = data["data"]["upload_url"]
        publish_id = data["data"]["publish_id"]

        # Paso 2 — Subir el archivo
        print("📤 Subiendo video...")
        with open(ruta_video, "rb") as video_file:
            video_data = video_file.read()

        upload_response = requests.put(
            upload_url,
            data=video_data,
            headers={
                "Content-Type": "video/mp4",
                "Content-Length": str(len(video_data)),
                "Content-Range": f"bytes 0-{len(video_data)-1}/{len(video_data)}"
            }
        )

        if upload_response.status_code not in [200, 201]:
            print(f"❌ Error subiendo video: {upload_response.status_code}")
            return False

        print(f"✅ Video subido a TikTok (ID: {publish_id})")
        return True

    except Exception as e:
        print(f"❌ Error con API de TikTok: {e}")
        return False


# ============================================================
# FUNCIÓN PRINCIPAL — elige automáticamente el método
# ============================================================

def subir_tiktok(ruta_video: str, descripcion: str) -> bool:
    """
    Intenta subir con API oficial primero.
    Si no hay credenciales de API, usa Playwright.
    """
    # Si tiene API key configurada usa la API oficial
    if os.getenv("TIKTOK_CLIENT_KEY") and os.getenv("TIKTOK_ACCESS_TOKEN"):
        print("📡 Usando API oficial de TikTok...")
        return subir_tiktok_api(ruta_video, descripcion)
    
    # Si no, usa Playwright
    print("🌐 Usando Playwright para TikTok...")
    return subir_tiktok_playwright(ruta_video, descripcion)
