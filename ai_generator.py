# ai_generator.py
#from openai import OpenAI
from google import genai
import os
import json
import re
import sys
import time
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#clientGPT = OpenAI(api_key=os.getenv("CHATGPT_API_KEY"))

#Peticion para gemini y generar el titulo, descripcion y captions para redes sociales

#def generar_metadata(titulo: str, subtitulo: str, genero: str = "música") -> dict:
#    
#    prompt = f"""Eres un experto en marketing musical para redes sociales.
#Tengo un video de {genero} con título: "{titulo}" y subtítulo: "{subtitulo}".
#
#Responde SOLO con JSON válido, sin texto extra, sin markdown, así:
#{{
#  "youtube_title": "título atractivo para YouTube (max 70 caracteres)",
#  "youtube_description": "descripción para YouTube con hashtags musicales",
#  "instagram_caption": "caption con emojis y hashtags para Instagram",
#  "tiktok_caption": "caption corto y viral para TikTok con hashtags"
#}}"""
#
#    # Reintentos automáticos si Gemini está saturado
#    intentos = 0
#    max_intentos = 5
#    
#    while intentos < max_intentos:
#        try:
#            response = client.models.generate_content(
#                model="gemini-2.5-flash",
#                contents=prompt
#            )
#            texto = response.text
#            texto_limpio = re.sub(r"```json|```", "", texto).strip()
#            return json.loads(texto_limpio)
#
#        except Exception as e:
#            intentos += 1
#            if intentos < max_intentos:
#                espera = intentos * 10  # 10s, 20s, 30s, 40s
#                print(f"⚠️ Gemini saturado, reintentando en {espera}s... ({intentos}/{max_intentos})")
#                time.sleep(espera)
#            else:
#                print("❌ Gemini no responde después de varios intentos")
#                raise e

def _llamar_gemini(prompt: str) -> str:
    """Llama a Gemini con reintentos"""
    modelos = ["gemini-2.5-flash", "gemini-2.0-flash-lite"]
    
    for modelo in modelos:
        for intento in range(3):
            try:
                response = client.models.generate_content(
                    model=modelo,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                espera = (intento + 1) * 10
                print(f"⚠️ Gemini ({modelo}) saturado, reintentando en {espera}s... ({intento+1}/3)")
                time.sleep(espera)
    return None

def _llamar_groq(prompt: str) -> str:
    """Llama a Groq como respaldo"""
    try:
        from groq import Groq
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"⚠️ Groq también falló: {e}")
        return None

def _llamar_ia(prompt: str) -> str:
    """Llama a la IA con respaldo automático Gemini → Groq"""
    # Intentar Gemini primero
    resultado = _llamar_gemini(prompt)
    if resultado:
        return resultado
    
    # Respaldo Groq
    print("🔄 Cambiando a Groq como respaldo...")
    resultado = _llamar_groq(prompt)
    if resultado:
        return resultado
    
    raise Exception("❌ Todos los servicios de IA fallaron")
##Peticion para gemini y elegir la noticia más viral e interesante de una lista de noticias

def generar_query_video(titulo_noticia: str, artista: str) -> str:
    """La IA genera el mejor query para buscar el video en YouTube"""
    prompt = f"""Eres un experto en búsqueda de videos de YouTube.
Tengo esta noticia musical: "{titulo_noticia}"
El artista es: "{artista}"

Genera el MEJOR query de búsqueda para encontrar en YouTube un video 
relacionado con esta noticia — puede ser un clip oficial, una actuación, 
una entrevista o el momento exacto de la noticia.

Responde SOLO con el query de búsqueda, sin explicaciones, máximo 6 palabras.
Ejemplos: "Celine Dion Paris concert 2026", "Michael Jackson biopic trailer official"
"""
    try:
        texto = _llamar_ia(prompt)
        query = texto.strip().replace('"', '')
        print(f"🔍 Query generado por IA: {query}")
        return query
    except:
        # Fallback simple
        palabras = titulo_noticia.split()[:3]
        return f"{artista} {' '.join(palabras)}"

def generar_metadata(titulo: str, subtitulo: str, genero: str = "música") -> dict:
    prompt = f"""Eres un experto en marketing musical para redes sociales.
Tengo un video de {genero} con título: "{titulo}" y subtítulo: "{subtitulo}".

Responde SOLO con JSON válido, sin texto extra, sin markdown, así:
{{
  "youtube_title": "título atractivo para YouTube (max 70 caracteres)",
  "youtube_description": "descripción para YouTube con hashtags musicales",
  "instagram_caption": "caption con emojis y hashtags para Instagram",
  "tiktok_caption": "caption corto y viral para TikTok con hashtags"
  "subtitulo_portada": "2-3 palabras clave del subtítulo para usar en la portada que resuman la noticia , (ej GRAN COMEBACK, NUEVO DISCO, GIRA MUNDIAL) pero que le den sentido a la portada y sean atractivas para el público, no solo repetir el subtítulo"
}}"""

    texto = _llamar_ia(prompt)
    texto_limpio = re.sub(r"```json|```", "", texto).strip()
    return json.loads(texto_limpio)

def elegir_noticia(noticias: list) -> dict:
    lista = "\n".join([
        f"{i+1}. [{n['fuente']}] {n['titulo']} - {n['resumen'][:100]}"
        for i, n in enumerate(noticias)
    ])

    prompt = f"""Eres el editor de una cuenta de música en redes sociales.
Aquí tienes una lista de noticias de música:

{lista}

Elige la noticia MÁS interesante y viral para publicar hoy en redes sociales.
Responde SOLO con JSON válido así:
{{
  "numero": 3,
  "razon": "breve explicación de por qué esta noticia es la más interesante"
}}"""

    texto = _llamar_ia(prompt)
    texto_limpio = re.sub(r"```json|```", "", texto).strip()
    return json.loads(texto_limpio)

#def elegir_noticia(noticias: list) -> dict:
#    
#    # Preparamos la lista para que la IA la evalúe
#    lista = "\n".join([
#        f"{i+1}. [{n['fuente']}] {n['titulo']} - {n['resumen'][:100]}"
#        for i, n in enumerate(noticias)
#    ])
#
#    prompt = f"""Eres el editor de una cuenta de música en redes sociales.
#Aquí tienes una lista de noticias de música:
#
#{lista}
#
#Elige la noticia MÁS interesante y viral para publicar hoy en redes sociales.
#Responde SOLO con JSON válido así:
#{{
#  "numero": 3,
#  "razon": "breve explicación de por qué esta noticia es la más interesante"
#}}"""
#
#     # Reintentos automáticos si Gemini está saturado
#    intentos = 0
#    max_intentos = 5
#    
#    while intentos < max_intentos:
#        try:
#            response = client.models.generate_content(
#                model="gemini-2.5-flash",
#                contents=prompt
#            )
#            texto = response.text
#            texto_limpio = re.sub(r"```json|```", "", texto).strip()
#            return json.loads(texto_limpio)
#
#        except Exception as e:
#            intentos += 1
#            if intentos < max_intentos:
#                espera = intentos * 10  # 10s, 20s, 30s, 40s
#                print(f"⚠️ Gemini saturado, reintentando en {espera}s... ({intentos}/{max_intentos})")
#                time.sleep(espera)
#            else:
#                print("❌ Gemini no responde después de varios intentos")
#                raise e
#
#    response = client.models.generate_content(
#        model="gemini-2.5-flash", #gemini-1.5-flash
#        contents=prompt
#    )
#
#    texto = response.text
#    texto_limpio = re.sub(r"```json|```", "", texto).strip()
#    return json.loads(texto_limpio)
#

def elegir_noticia(noticias: list) -> dict:
    lista = "\n".join([
        f"{i+1}. [{n['fuente']}] {n['titulo']} - {n['resumen'][:100]}"
        for i, n in enumerate(noticias)
    ])

    prompt = f"""Eres el editor de una cuenta de música en redes sociales.
Aquí tienes una lista de noticias de música:

{lista}

Elige la noticia MÁS interesante y viral para publicar hoy en redes sociales.
Responde SOLO con JSON válido así:
{{
  "numero": 3,
  "razon": "breve explicación de por qué esta noticia es la más interesante"
}}"""

    texto = _llamar_ia(prompt)
    texto_limpio = re.sub(r"```json|```", "", texto).strip()
    return json.loads(texto_limpio)


#
#def extraer_artista_de_titulo(titulo: str) -> str:
#    """Extrae el nombre del artista del título de la noticia"""
#    artistas = [
#        "Celine Dion", "Bad Bunny", "Taylor Swift", "Kanye West",
#        "BTS", "Karol G", "J Balvin", "Peso Pluma", "SZA",
#        "Post Malone", "Chappell Roan", "Kesha", "FKA Twigs",
#        "Camilo", "Interpol", "Lana Del Rey", "Kacey Musgraves"
#    ]
#    for artista in artistas:
#        if artista.lower() in titulo.lower():
#            return artista
#    palabras = titulo.split()
#    return " ".join(palabras[:2])
#
def extraer_artista_de_titulo(titulo: str) -> str:
    """Usa IA para extraer el nombre del artista del título"""
    try:
        prompt = f"""Del siguiente título de noticia musical, extrae SOLO el nombre del artista principal.
Responde ÚNICAMENTE con el nombre, sin explicaciones ni puntuación extra.
Título: "{titulo}"
"""
        texto = _llamar_ia(prompt)
        return texto.strip()
    except:
        return titulo.split()[0]

def confirmar_y_generar(noticias: list) -> dict:
    
    # IA sugiere
    time.sleep(45)  # damos mas tiempo a la IA
    sugerencia = elegir_noticia(noticias)
    noticia_elegida = noticias[sugerencia["numero"] - 1]
        
    # Mostramos al usuario
    print(f"\n🤖 La IA sugiere:")
    print(f"   📰 {noticia_elegida['titulo']}")
    print(f"   💡 {sugerencia['razon']}")
    
    # Tú confirmas
    respuesta = input("\n¿Publicamos esta noticia? (s/n): ").lower()
    
    if respuesta != "s":
        # Elegir manualmente
        sys.stdin.flush()
        print("\n¿Qué número quieres publicar? ", end="")
        numero = int(input()) - 1
        noticia_elegida = noticias[numero]
    
    # IA genera los textos para cada red
    print("\n✍️ Generando textos para cada plataforma...")
    metadata = generar_metadata(
        noticia_elegida["titulo"],
        noticia_elegida["resumen"],
        "música"
    )
    
    return {
        "noticia": noticia_elegida,
        "metadata": metadata
    }



# Prueba del modulo solo
#if __name__ == "__main__":
#    resultado = generar_metadata("Noche Eterna", "Extended Mix", "techno")
#    print(resultado)