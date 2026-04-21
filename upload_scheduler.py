## scheduler/upload_scheduler.py
#import schedule
#import time
#import datetime
#import threading
#import subprocess
#
#def programar_subida(ruta_video, descripcion, fecha_str):
#    fecha_obj = datetime.datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
#    hora_programada = fecha_obj.strftime("%H:%M")
#
#    def job():
#        print("🚀 Ejecutando subida a TikTok...")
#        subprocess.run([
#            "python", "tiktok_uploader/upload.py",
#            "--video", ruta_video,
#            "--description", descripcion
#        ])
#
#    schedule.every().day.at(hora_programada).do(job)
#
#    def ejecutar_programacion():
#        while True:
#            schedule.run_pending()
#            time.sleep(1)
#
#    threading.Thread(target=ejecutar_programacion, daemon=True).start()
#
#
# upload_scheduler.py
import schedule
import time
import datetime
import threading
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# SCHEDULER — programa cuándo publicar
# ============================================================

trabajos_pendientes = []

def publicar_ahora(ruta_imagen: str, ruta_video: str, metadata: dict):
    """Publica en todas las plataformas ahora mismo"""
    from uploaders.tiktok_uploader import subir_tiktok
    from uploaders.instagram_uploader import subir_instagram

    resultados = {}

    # Instagram — imagen
    print("\n📸 Subiendo a Instagram...")
    resultados["instagram"] = subir_instagram(
        ruta_imagen,
        metadata["instagram_caption"]
    )

    # TikTok — video
    print("\n🎵 Subiendo a TikTok...")
    resultados["tiktok"] = subir_tiktok(
        ruta_video,
        metadata["tiktok_caption"]
    )

    # Resumen
    print("\n📊 RESUMEN DE PUBLICACIÓN:")
    for plataforma, exito in resultados.items():
        emoji = "✅" if exito else "❌"
        print(f"   {emoji} {plataforma.capitalize()}")

    return resultados


def programar_subida(ruta_imagen: str, ruta_video: str, 
                     metadata: dict, fecha_str: str):
    """Programa la publicación para una fecha y hora específica"""
    
    fecha_obj = datetime.datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
    ahora = datetime.datetime.now()

    if fecha_obj <= ahora:
        # Si la hora ya pasó publicamos ahora
        print("⚡ La hora ya pasó — publicando ahora...")
        publicar_ahora(ruta_imagen, ruta_video, metadata)
        return

    delay_segundos = (fecha_obj - ahora).total_seconds()
    delay_minutos = int(delay_segundos / 60)
    delay_horas = round(delay_segundos / 3600, 1)

    print(f"⏰ Publicación programada para {fecha_str}")
    if delay_horas >= 1:
        print(f"   Faltan {delay_horas} horas")
    else:
        print(f"   Faltan {delay_minutos} minutos")

    def esperar_y_publicar():
        time.sleep(delay_segundos)
        print(f"\n🚀 ¡Es la hora! Publicando ahora...")
        publicar_ahora(ruta_imagen, ruta_video, metadata)

    hilo = threading.Thread(target=esperar_y_publicar, daemon=True)
    hilo.start()
    trabajos_pendientes.append(hilo)
    
    return hilo


def programar_publicacion_diaria(hora: str, ruta_imagen: str, 
                                  ruta_video: str, metadata: dict):
    """
    Programa una publicación automática todos los días a la misma hora
    hora formato: "18:00"
    """
    def job():
        print(f"\n🔄 Publicación diaria a las {hora}")
        publicar_ahora(ruta_imagen, ruta_video, metadata)

    schedule.every().day.at(hora).do(job)
    print(f"📅 Publicación diaria programada a las {hora}")

    def ejecutar_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(30)

    hilo = threading.Thread(target=ejecutar_scheduler, daemon=True)
    hilo.start()
    return hilo
