# main.py
from editor.video_generator import generar_video
from scheduler.upload_scheduler import programar_subida

def main():
    print("🎛️  The Released - BOT\n")

    enlace = input("🔗 Enlace de TikTok (opcional): ")
    titulo = input("🎵 Título del video: ")
    subtitulo = input("✏️ Subtítulo del video: ")
    fecha = input("🕒 Fecha de publicación (YYYY-MM-DD HH:MM): ")

    generar_video(titulo, subtitulo)
    programar_subida("video_final.mp4", f"{titulo} - {subtitulo}", fecha)

    print("\n✅ Video generado y subida programada.")

if __name__ == "__main__":
    main()
