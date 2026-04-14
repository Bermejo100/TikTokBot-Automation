# ai_generator.py
from google import genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

#Peticion para gemini y generar el titulo, descripcion y captions para redes sociales

def generar_metadata(titulo: str, subtitulo: str, genero: str = "música") -> dict:
    
    prompt = f"""Eres un experto en marketing musical para redes sociales.
Tengo un video de {genero} con título: "{titulo}" y subtítulo: "{subtitulo}".

Responde SOLO con JSON válido, sin texto extra, sin markdown, así:
{{
  "youtube_title": "título atractivo para YouTube (max 70 caracteres)",
  "youtube_description": "descripción para YouTube con hashtags musicales",
  "instagram_caption": "caption con emojis y hashtags para Instagram",
  "tiktok_caption": "caption corto y viral para TikTok con hashtags"
}}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    texto = response.text
    texto_limpio = re.sub(r"```json|```", "", texto).strip()
    return json.loads(texto_limpio)

#Peticion para gemini y elegir la noticia más viral e interesante de una lista de noticias

def elegir_noticia(noticias: list) -> dict:
    
    # Preparamos la lista para que la IA la evalúe
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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    texto = response.text
    texto_limpio = re.sub(r"```json|```", "", texto).strip()
    return json.loads(texto_limpio)

def confirmar_y_generar(noticias: list) -> dict:
    
    # IA sugiere
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
if __name__ == "__main__":
    resultado = generar_metadata("Noche Eterna", "Extended Mix", "techno")
    print(resultado)