# uploaders/instagram_uploader.py
import os
import time
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# OPCIÓN 1 — CON instagrapi (recomendada)
# ============================================================

def subir_instagram_instagrapi(ruta_imagen: str, caption: str) -> bool:
    """Sube imagen/video a Instagram usando instagrapi"""
    try:
        from instagrapi import Client

        usuario = os.getenv("INSTAGRAM_USER")
        password = os.getenv("INSTAGRAM_PASS")

        if not usuario or not password:
            print("❌ Faltan credenciales de Instagram en .env")
            return False

        cl = Client()
        
        # Intentar cargar sesión guardada para no hacer login cada vez
        session_file = "instagram_session.json"
        if os.path.exists(session_file):
            print("📂 Cargando sesión guardada...")
            cl.load_settings(session_file)
            cl.login(usuario, password)
        else:
            print("🔑 Iniciando sesión en Instagram...")
            cl.login(usuario, password)
            cl.dump_settings(session_file)

        # Detectar si es imagen o video
        extension = os.path.splitext(ruta_imagen)[1].lower()
        
        if extension in [".mp4", ".mov"]:
            print("📤 Subiendo Reel a Instagram...")
            cl.clip_upload(
                path=ruta_imagen,
                caption=caption
            )
        else:
            print("📤 Subiendo imagen a Instagram...")
            cl.photo_upload(
                path=ruta_imagen,
                caption=caption
            )

        print("✅ Publicado en Instagram")
        return True

    except Exception as e:
        print(f"❌ Error subiendo a Instagram: {e}")
        return False


# ============================================================
# OPCIÓN 2 — CON API oficial de Meta
# Requiere cuenta de empresa verificada en Meta Business
# ============================================================

def subir_instagram_api(ruta_imagen: str, caption: str) -> bool:
    """Sube imagen a Instagram usando la API oficial de Meta"""
    try:
        import requests

        access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        instagram_id = os.getenv("INSTAGRAM_BUSINESS_ID")

        if not access_token or not instagram_id:
            print("❌ Faltan credenciales de API de Meta en .env")
            print("   Necesitas: INSTAGRAM_ACCESS_TOKEN e INSTAGRAM_BUSINESS_ID")
            return False

        # Paso 1 — Crear contenedor
        print("📦 Creando contenedor...")
        container_response = requests.post(
            f"https://graph.facebook.com/v18.0/{instagram_id}/media",
            params={
                "image_url": ruta_imagen,  # Con API oficial necesita URL pública
                "caption": caption,
                "access_token": access_token
            }
        )

        container_data = container_response.json()
        
        if "id" not in container_data:
            print(f"❌ Error creando contenedor: {container_data}")
            return False

        container_id = container_data["id"]
        time.sleep(5)

        # Paso 2 — Publicar contenedor
        print("🚀 Publicando...")
        publish_response = requests.post(
            f"https://graph.facebook.com/v18.0/{instagram_id}/media_publish",
            params={
                "creation_id": container_id,
                "access_token": access_token
            }
        )

        publish_data = publish_response.json()

        if "id" not in publish_data:
            print(f"❌ Error publicando: {publish_data}")
            return False

        print(f"✅ Publicado en Instagram (ID: {publish_data['id']})")
        return True

    except Exception as e:
        print(f"❌ Error con API de Instagram: {e}")
        return False


# ============================================================
# FUNCIÓN PRINCIPAL — elige automáticamente el método
# ============================================================

def subir_instagram(ruta_imagen: str, caption: str) -> bool:
    """
    Intenta subir con API oficial primero.
    Si no hay credenciales de API, usa instagrapi.
    """
    if os.getenv("INSTAGRAM_ACCESS_TOKEN") and os.getenv("INSTAGRAM_BUSINESS_ID"):
        print("📡 Usando API oficial de Instagram...")
        return subir_instagram_api(ruta_imagen, caption)
    
    print("📱 Usando instagrapi para Instagram...")
    return subir_instagram_instagrapi(ruta_imagen, caption)
