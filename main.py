# main.py
import os
from news_fetcher import obtener_todas_noticias, mostrar_noticias
from ai_generator import confirmar_y_generar, extraer_artista_de_titulo
from image_generator import generar_portada, extraer_artista_de_titulo
from editor.video_generator import generar_video_completo
from upload_scheduler import programar_subida

def main():
    print("🎛️  THE RELEASED — BOT\n")
    print("=" * 40)

    # 1 — Obtener noticias
    print("\n📰 Obteniendo noticias...")
    noticias = obtener_todas_noticias()
    mostrar_noticias(noticias)

    # 2 — IA elige y genera textos
    resultado = confirmar_y_generar(noticias)
    noticia = resultado["noticia"]
    metadata = resultado["metadata"]

    # 3 — Extraer artista
    artista = extraer_artista_de_titulo(noticia["titulo"])
    print(f"\n🎤 Artista detectado: {artista}")

    # 4 — Generar portadas
    print("\n🎨 Generando portadas...")
    generar_portada(
        plantilla_path="assets/plantilla_instagram.jpg",
        titulo=artista,
        subtitulo=metadata["youtube_title"][:30],
        nombre_artista=artista,
        output_path="assets/portada_instagram.jpg"
    )
    generar_portada(
        plantilla_path="assets/plantilla_tiktok.jpg",
        titulo=artista,
        subtitulo=metadata["youtube_title"][:30],
        nombre_artista=artista,
        output_path="assets/portada_tiktok.jpg"
    )

    # 5 — Generar videos
    print("\n🎬 Buscando y generando videos...")
    videos = generar_video_completo(noticia["titulo"], artista)

    if not videos:
        print("❌ No se pudieron generar los videos")
        return

    # 6 — Programar publicación
    print("\n⏰ ¿Cuándo quieres publicar?")
    print("   1. Ahora mismo")
    print("   2. Programar fecha y hora")
    opcion = input("\nElige (1/2): ").strip()

    if opcion == "2":
        fecha = input("📅 Fecha y hora (YYYY-MM-DD HH:MM): ").strip()
    else:
        from datetime import datetime
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 7 — Publicar
    programar_subida(
        ruta_imagen="assets/portada_instagram.jpg",
        ruta_video=videos["tiktok"],
        metadata=metadata,
        fecha_str=fecha
    )

    # YouTube — usa su propio video horizontal
    if opcion != "2":
        from uploaders.youtube_uploader import subir_youtube
        print("\n▶️ Subiendo a YouTube...")
        subir_youtube(
            ruta_video=videos["youtube"],
            titulo=metadata["youtube_title"],
            descripcion=metadata["youtube_description"]
        )

    print("\n✅ ¡Todo listo!")
    print("=" * 40)

    # Mantener el programa vivo si hay publicaciones programadas
    if opcion == "2":
        print("\n⏳ Bot esperando para publicar... (Ctrl+C para salir)")
        try:
            import time
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Bot detenido")

if __name__ == "__main__":
    main()