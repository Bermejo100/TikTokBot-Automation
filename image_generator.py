# image_generator.py
from rembg import remove , new_session
from PIL import Image, ImageDraw, ImageFont , ImageChops ,ImageFilter ,ImageOps
import requests
import os
from io import BytesIO
import numpy as np 


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

def generar_portada(plantilla_olas_path: str, plantilla_path: str, titulo: str, subtitulo: str,
                    nombre_artista: str, output_path: str):
    """Genera la portada final con foto, título y subtítulo"""

    # Abrir plantilla limpia
    plantilla = Image.open(plantilla_path).convert("RGBA")
    ancho, alto = plantilla.size  # 1080 x 1920

    # Buscar y pegar foto del artista ,Pasar la foto po remove.png para que le quite el fondo y quede solo el artista
    foto = buscar_imagen_artista(nombre_artista)
    session = new_session("isnet-general-use")
    foto_sin_fondo = remove(
    foto, 
    session=session,
    alpha_matting=True,
    alpha_matting_foreground_threshold=240, # Píxeles muy seguros de ser persona
    alpha_matting_background_threshold=30,  # Píxeles muy seguros de ser fondo
    alpha_matting_erode_size=20              # Ajuste fino del borde
    )
    #foto_sin_fondo = remove(foto, model='isnet-general-use', alpha_matting=True)
    foto_sin_fondo.save("assets/foto_sin_fondo.png")


    if foto_sin_fondo:
            # 1. Aseguramos el modo y el tamaño
            foto_sin_fondo = foto_sin_fondo.convert("RGBA")
            foto_alto = int(alto * 0.55) 
            foto_sin_fondo = foto_sin_fondo.resize((ancho, foto_alto), Image.LANCZOS)

            # 2. EL TRUCO DEL PELO: Suavizado de bordes
            alfa = foto_sin_fondo.getchannel('A')
            alfa = alfa.filter(ImageFilter.GaussianBlur(radius=1.5)) 
            foto_sin_fondo.putalpha(alfa)

            # 3. CREAR LA MÁSCARA (Esto es lo que te faltaba copiar)
            # Creamos una máscara negra del tamaño de la foto
            mascara = Image.new("L", (ancho, foto_alto), 255)
            draw = ImageDraw.Draw(mascara)
            
            # Dibujamos el degradado en la parte de abajo
            inicio_grad = int(foto_alto * 0.75)
            for i in range(inicio_grad, foto_alto):
                # Calculamos la opacidad para que se desvanezca
                opacidad = int(255 * (1 - (i - inicio_grad) / (foto_alto - inicio_grad)))
                draw.line([(0, i), (ancho, i)], fill=opacidad)

            # Combinamos el alfa suavizado con el degradado recién creado
            alfa_final = ImageChops.multiply(foto_sin_fondo.getchannel('A'), mascara)
            foto_sin_fondo.putalpha(alfa_final)

            # 4. LA CLAVE FINAL: Pegado profesional
            capa_personaje = Image.new("RGBA", plantilla.size, (0, 0, 0, 0))
            capa_personaje.paste(foto_sin_fondo, (0, 100))
            
            # Mezcla real de transparencias (aquí es donde el pelo se vuelve morado de fondo)
            plantilla = Image.alpha_composite(plantilla.convert("RGBA"), capa_personaje)

    #Lo pasamos por la IA
    ###cargar la parte de la capa de las olas y el efecto de luz
    #plantilla_olas = Image.open(plantilla_olas_path).convert("RGBA")

    #r, g, b, a = plantilla_olas.split()   
    #nueva_mascara = ImageOps.invert(g)
    #nueva_mascara = nueva_mascara.point(lambda p: p if p > 100 else 0)  # Umbral para eliminar el fondo
    #nueva_mascara = nueva_mascara.filter(ImageFilter.GaussianBlur(radius=0.5))
    #plantilla_olas.putalpha(nueva_mascara)

    #olas_sin_fondo = remove(
    #        plantilla_olas,
    #        session=session,
    #        alpha_matting=True,
    #        alpha_matting_foreground_threshold=240,
    #        alpha_matting_background_threshold=10,
    #        alpha_matting_erode_size=2 
    #    )

    #redimensionado y pegado
    #plantilla_olas = plantilla_olas.resize(plantilla.size, Image.LANCZOS)
    #plantilla_olas.save("assets/olas_sin_fondo.png")
    #plantilla = Image.alpha_composite(plantilla.convert("RGBA"), plantilla_olas)


    #
    #opcion 2 a mano
    ##cargar la parte de la capa de las olas y el efecto de luz
    #plantilla_olas = Image.open(plantilla_olas_path).convert("RGBA")
    #plantilla_olas = plantilla_olas.resize(plantilla.size, Image.LANCZOS)
    ## 2. SEPARAR CANALES
    #r, g, b, a = plantilla_olas.split()
    #    
    ## 3. CREAR MÁSCARA ANTI-BLANCO
    ## Buscamos los píxeles donde R, G y B son altos (casi blancos)
    ## y creamos una máscara que los vuelva transparentes.        
    ## Convertimos los canales a arrays de Numpy para operar rápido
    #R = np.array(r)
    #G = np.array(g)
    #B = np.array(b)
    #    
    ## Definimos qué consideramos "blanco" (ej: > 240 en los 3 canales)
    ## Puedes ajustar este 240 si tu blanco no es puro.
    #umbral_blanco = 240 
    #    
    ## Creamos la máscara: Es negra (0) donde hay blanco, blanca (255) donde hay color
    #mascara_anti_blanco = np.where((R > umbral_blanco) & (G > umbral_blanco) & (B > umbral_blanco), 0, 255).astype(np.uint8)
    #    
    ## Convertimos el array de vuelta a imagen PIL
    #mask_img = Image.fromarray(mascara_anti_blanco, mode="L")
    #    
    ## 4. APLICAMOS LA MÁSCARA AL ALFA DEL EFECTO
    #plantilla_olas.putalpha(mask_img)

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
#if __name__ == "__main__":
#    generar_portada(
#        plantilla_olas_path="assets/plantilla_olas.jpg",
#        plantilla_path="assets/plantilla_instagram.jpg",
#        titulo="Celine Dion",
#        subtitulo="Vuelta en Paris",
#        nombre_artista="Celine Dion",
#        output_path="assets/resultado_instagram.jpg"
#     )