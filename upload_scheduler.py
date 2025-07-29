# scheduler/upload_scheduler.py
import schedule
import time
import datetime
import threading
import subprocess

def programar_subida(ruta_video, descripcion, fecha_str):
    fecha_obj = datetime.datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
    hora_programada = fecha_obj.strftime("%H:%M")

    def job():
        print("🚀 Ejecutando subida a TikTok...")
        subprocess.run([
            "python", "tiktok_uploader/upload.py",
            "--video", ruta_video,
            "--description", descripcion
        ])

    schedule.every().day.at(hora_programada).do(job)

    def ejecutar_programacion():
        while True:
            schedule.run_pending()
            time.sleep(1)

    threading.Thread(target=ejecutar_programacion, daemon=True).start()
