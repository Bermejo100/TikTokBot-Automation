# editor/video_generator.py
##from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
#
#def generar_video(titulo, subtitulo):
#    plantilla = "assets/plantilla.mp4"
#    salida = "video_final.mp4"
#
#    video = VideoFileClip(plantilla)
#
#    txt_titulo = TextClip(titulo, fontsize=70, color='white', font='Arial-Bold')
#    txt_titulo = txt_titulo.set_position(("center", 50)).set_duration(video.duration)
#
#    txt_subtitulo = TextClip(subtitulo, fontsize=40, color='white', font='Arial')
#    txt_subtitulo = txt_subtitulo.set_position(("center", 120)).set_duration(video.duration)
#
#    video_final = CompositeVideoClip([video, txt_titulo, txt_subtitulo])
#    video_final.write_videofile(salida, codec="libx264", audio_codec="aac")
# editor/video_generator.py
import os
import subprocess
from moviepy.editor import (VideoFileClip, ImageClip, CompositeVideoClip, 
                             AudioFileClip, TextClip, concatenate_videoclips)
from PIL import Image
import yt_dlp

def buscar_video_youtube(query: str, duracion_max: int = 60) -> str:
    """Busca y descarga el video más relevante de YouTube"""
    try:
        output_path = "assets/video_descargado.mp4"
        
        ydl_opts = {
            "format": "best[ext=mp4][height<=720]",
            "outtmpl": output_path,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "match_filter": yt_dlp.utils.match_filter_func(
                f"duration < {duracion_max}"
            ),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"🔍 Buscando video: {query}")
            ydl.download([f"ytsearch1:{query}"])

        if os.path.exists(output_path):
            print(f"✅ Video descargado")
            return output_path
        return None

    except Exception as e:
        print(f"⚠️ Error descargando video: {e}")
        return None


def recortar_video(ruta_video: str, duracion: int = 28) -> str:
    """Recorta el video a los primeros X segundos"""
    try:
        output_path = "assets/video_recortado.mp4"
        video = VideoFileClip(ruta_video)
        
        # Cogemos los primeros 28 segundos (ideal para Reels/Shorts)
        duracion_real = min(duracion, video.duration)
        video_recortado = video.subclip(0, duracion_real)
        video_recortado.write_videofile(
            output_path, 
            codec="libx264", 
            audio_codec="aac",
            verbose=False,
            logger=None
        )
        video.close()
        print(f"✂️ Video recortado a {duracion_real:.0f} segundos")
        return output_path

    except Exception as e:
        print(f"⚠️ Error recortando video: {e}")
        return ruta_video


def adaptar_formato(ruta_video: str, formato: str = "vertical") -> str:
    """Adapta el video al formato correcto para cada red"""
    try:
        output_path = f"assets/video_{formato}.mp4"
        video = VideoFileClip(ruta_video)
        ancho, alto = video.size

        if formato == "vertical":
            # 9:16 para TikTok e Instagram Reels
            nuevo_alto = 1920
            nuevo_ancho = 1080

        elif formato == "horizontal":
            # 16:9 para YouTube
            nuevo_alto = 720
            nuevo_ancho = 1280

        else:
            # Cuadrado para Instagram feed
            nuevo_alto = 1080
            nuevo_ancho = 1080

        # Redimensionar manteniendo proporciones con barras negras
        ratio_original = ancho / alto
        ratio_objetivo = nuevo_ancho / nuevo_alto

        if ratio_original > ratio_objetivo:
            ancho_final = nuevo_ancho
            alto_final = int(nuevo_ancho / ratio_original)
        else:
            alto_final = nuevo_alto
            ancho_final = int(nuevo_alto * ratio_original)

        video_redim = video.resize((ancho_final, alto_final))

        # Fondo negro del tamaño objetivo
        from moviepy.editor import ColorClip
        fondo = ColorClip(
            size=(nuevo_ancho, nuevo_alto), 
            color=[0, 0, 0],
            duration=video.duration
        )

        # Centrar video sobre fondo
        x = (nuevo_ancho - ancho_final) // 2
        y = (nuevo_alto - alto_final) // 2
        video_centrado = video_redim.set_position((x, y))

        final = CompositeVideoClip([fondo, video_centrado])
        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )
        video.close()
        print(f"📐 Video adaptado a formato {formato}")
        return output_path

    except Exception as e:
        print(f"⚠️ Error adaptando formato: {e}")
        return ruta_video


def añadir_logo(ruta_video: str, ruta_logo: str, output_path: str) -> str:
    """Añade el logo de The Released en la esquina inferior"""
    try:
        video = VideoFileClip(ruta_video)
        ancho, alto = video.size

        logo = ImageClip(ruta_logo)
        
        # Logo ocupa el 15% del ancho
        logo_ancho = int(ancho * 0.15)
        logo = logo.resize(width=logo_ancho)
        
        # Posición esquina inferior centrada
        logo = logo.set_position(
            ("center", alto - logo.size[1] - 40)
        ).set_duration(video.duration)

        final = CompositeVideoClip([video, logo])
        final.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None
        )
        video.close()
        print(f"🏷️ Logo añadido")
        return output_path

    except Exception as e:
        print(f"⚠️ Error añadiendo logo: {e}")
        return ruta_video


def generar_video_completo(titulo_noticia: str, artista: str) -> dict:
    """
    Función principal — genera todos los videos necesarios
    Devuelve rutas de los videos para cada plataforma
    """
    print(f"\n🎬 Generando videos para: {titulo_noticia}")
    
    # 1 — Buscar y descargar video
    query = f"{artista} {titulo_noticia[:50]}"
    video_descargado = buscar_video_youtube(query)
    
    if not video_descargado:
        print("❌ No se encontró video")
        return None

    # 2 — Recortar a 28 segundos
    video_recortado = recortar_video(video_descargado, duracion=28)

    # 3 — Generar versiones para cada plataforma
    print("📐 Adaptando formatos...")
    video_vertical = adaptar_formato(video_recortado, "vertical")
    video_horizontal = adaptar_formato(video_recortado, "horizontal")

    # 4 — Añadir logo si existe
    logo_path = "assets/logo.png"
    
    if os.path.exists(logo_path):
        video_tiktok = añadir_logo(
            video_vertical, logo_path, "assets/video_tiktok.mp4"
        )
        video_youtube = añadir_logo(
            video_horizontal, logo_path, "assets/video_youtube.mp4"
        )
        video_instagram = añadir_logo(
            video_vertical, logo_path, "assets/video_instagram.mp4"
        )
    else:
        import shutil
        shutil.copy(video_vertical, "assets/video_tiktok.mp4")
        shutil.copy(video_horizontal, "assets/video_youtube.mp4")
        shutil.copy(video_vertical, "assets/video_instagram.mp4")
        video_tiktok = "assets/video_tiktok.mp4"
        video_youtube = "assets/video_youtube.mp4"
        video_instagram = "assets/video_instagram.mp4"

    return {
        "tiktok": video_tiktok,
        "youtube": video_youtube,
        "instagram": video_instagram
    }


# Prueba
if __name__ == "__main__":
    videos = generar_video_completo(
        "Celine Dion Comeback Concerts Paris",
        "Celine Dion"
    )
    if videos:
        print(f"\n✅ Videos generados:")
        for plataforma, ruta in videos.items():
            print(f"   {plataforma}: {ruta}")