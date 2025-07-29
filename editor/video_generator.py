# editor/video_generator.py
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def generar_video(titulo, subtitulo):
    plantilla = "assets/plantilla.mp4"
    salida = "video_final.mp4"

    video = VideoFileClip(plantilla)

    txt_titulo = TextClip(titulo, fontsize=70, color='white', font='Arial-Bold')
    txt_titulo = txt_titulo.set_position(("center", 50)).set_duration(video.duration)

    txt_subtitulo = TextClip(subtitulo, fontsize=40, color='white', font='Arial')
    txt_subtitulo = txt_subtitulo.set_position(("center", 120)).set_duration(video.duration)

    video_final = CompositeVideoClip([video, txt_titulo, txt_subtitulo])
    video_final.write_videofile(salida, codec="libx264", audio_codec="aac")
