# uploaders/youtube_uploader.py
import os
import pickle
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    """Autentica con YouTube usando OAuth2"""
    credentials = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists("client_secrets.json"):
                print("❌ Falta client_secrets.json")
                print("   Ve a console.cloud.google.com y descarga las credenciales OAuth2")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES
            )
            credentials = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)

    return build("youtube", "v3", credentials=credentials)


def subir_youtube(ruta_video: str, titulo: str,
                  descripcion: str, tags: list = None) -> bool:
    """
    Sube video a YouTube.
    Si es vertical (9:16) y dura menos de 60s YouTube lo detecta como Short.
    """
    try:
        youtube = get_authenticated_service()
        if not youtube:
            return False

        body = {
            "snippet": {
                "title": titulo[:100],
                "description": descripcion,
                "tags": tags or ["music", "news", "shorts"],
                "categoryId": "10"  # Música
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            }
        }

        media = MediaFileUpload(
            ruta_video,
            mimetype="video/mp4",
            resumable=True
        )

        print(f"🚀 Iniciando subida a YouTube: {titulo}...")

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"📦 Subiendo... {int(status.progress() * 100)}%")

        print(f"✅ Subido a YouTube: https://youtube.com/watch?v={response['id']}")
        return True

    except Exception as e:
        print(f"❌ Error subiendo a YouTube: {e}")
        return False