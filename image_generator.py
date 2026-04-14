# image_generator.py
from PIL import Image, ImageDraw, ImageFont
import requests
import os
from io import BytesIO

FUENTE_PATH = "assets/Teko.ttf"

def buscar_imagen_artista(nombre_artista: str) -> Image.Image:
    """Busca imagen del artista en Wikipedia"""
    try:
        # Probamos primero Wikipedia en inglés
        for lang in ["en", "es"]:
            wiki_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{nombre_artista.replace(' ', '_')}"
            wiki_response = requests.get(
                wiki_url, 
                timeout=10,
                headers={"User-Agent": "MusicBot/1.0"}
            )
            
            if wiki_response.status_code != 200:
                continue
                
            wiki_data = wiki_response.json()
            
            if "originalimage" in wiki_data:
                img_url = wiki_data["originalimage"]["source"]
            elif "thumbnail" in wiki_data:
                img_url = wiki_data["thumbnail"]["source"]
            else:
                continue
                
            img_response = requests.get(img_url, timeout=10,
                                        headers={"User-Agent": "MusicBot/1.0"})
            return Image.open(BytesIO(img_response.content)).convert("RGBA")

    except Exception as e:
        print(f"⚠️ Error buscando imagen: {e}")
    return None

def extraer_artista_de_titulo(titulo: str) -> str:
    """Extrae el nombre del artista del título de la noticia"""
    artistas = [
        "Celine Dion", "Bad Bunny", "Taylor Swift", "Kanye West",
        "BTS", "Karol G", "J Balvin", "Peso Pluma", "SZA",
        "Post Malone", "Chappell Roan", "Kesha", "FKA Twigs",
        "Camilo", "Interpol", "Lana Del Rey", "Kacey Musgraves"
    ]
    for artista in artistas:
        if artista.lower() in titulo.lower():
            return artista
    palabras = titulo.split()
    return " ".join(palabras[:2])

def generar_portada(plantilla_path: str, titulo: str, subtitulo: str,
                    nombre_artista: str, output_path: str):
    """Genera la portada final con foto, título y subtítulo"""

    # Abrir plantilla limpia
    plantilla = Image.open(plantilla_path).convert("RGBA")
    ancho, alto = plantilla.size  # 1080 x 1920

    # Buscar y pegar foto del artista
    foto = buscar_imagen_artista(nombre_artista)
    if foto:
        foto_alto = int(alto * 0.55)
        foto = foto.resize((ancho, foto_alto), Image.LANCZOS)

        #crear mascara de degradado para fundir la foto con el fond
        mascara = Image.new("L",(ancho,  foto_alto), 255)
        draw_mascara = ImageDraw.Draw(mascara)

         # Degradado en la parte inferior de la foto
        for i in range(int(foto_alto * 0.6), foto_alto):
            opacidad = int(255 * (1 - (i - foto_alto * 0.6) / (foto_alto * 0.4)))
            draw_mascara.line([(0, i), (ancho, i)], fill=opacidad)

        foto_rgba = foto.convert("RGBA")
        foto_rgba.putalpha(mascara)
        plantilla.paste(foto_rgba, (0, 0), foto_rgba)

    # Preparar para escribir texto
    draw = ImageDraw.Draw(plantilla)

    # Cargar fuente Teko
    fuente_titulo = ImageFont.truetype(FUENTE_PATH, 220)
    fuente_subtitulo = ImageFont.truetype(FUENTE_PATH, 130)

    # Título en blanco #FF9EFE centrado
    texto_titulo = titulo.upper()
    bbox = draw.textbbox((0, 0), texto_titulo, font=fuente_titulo)
    w = bbox[2] - bbox[0]
    x = (ancho - w) // 2
    y = int(alto * 0.62)
    draw.text((x, y), texto_titulo, font=fuente_titulo, fill="#FFFFFF")

    # Subtítulo en rosa #FFFFFF centrado
    texto_sub = subtitulo.upper()
    bbox_sub = draw.textbbox((0, 0), texto_sub, font=fuente_subtitulo)
    w_sub = bbox_sub[2] - bbox_sub[0]
    x_sub = (ancho - w_sub) // 2
    y_sub = int(alto * 0.76)
    draw.text((x_sub, y_sub), texto_sub, font=fuente_subtitulo, fill="#FF9EFE")

    # Guardar
    resultado = plantilla.convert("RGB")
    resultado.save(output_path, quality=95)
    print(f"✅ Portada guardada: {output_path}")
    return output_path

# Prueba
if __name__ == "__main__":
    generar_portada(
        plantilla_path="assets/plantilla_instagram.jpg",
        titulo="Celine Dion",
        subtitulo="Vuelta en Paris",
        nombre_artista="Celine Dion",
        output_path="assets/resultado_instagram.jpg"
    )