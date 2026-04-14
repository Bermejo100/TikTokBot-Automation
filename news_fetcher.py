# news_fetcher.py
import feedparser
import requests
import socket
import os
import re
from html.parser import HTMLParser
from dotenv import load_dotenv

load_dotenv()

socket.setdefaulttimeout(5)

# RSS feeds música general (solo los que funcionan)
FEEDS = [
    "https://www.billboard.com/feed/",
    "https://www.nme.com/feed",
    "https://consequence.net/feed/",
    "https://www.stereogum.com/feed/",
]

# Palabras clave para música latina
KEYWORDS_LATINO = [
    "Bad Bunny", "reggaeton", "J Balvin",
    "Karol G", "Peso Pluma", "musica latina"
]

def limpiar_html(texto: str) -> str:
    texto_limpio = re.sub(r'<[^>]+>', '', texto)
    return texto_limpio.strip()[:300]

def obtener_noticias_rss(max_noticias: int = 20) -> list:
    noticias = []
    for feed_url in FEEDS:
        feed = feedparser.parse(
            feed_url,
            agent="Mozilla/5.0",
            request_headers={"Connection": "close"}
        )
        for entrada in feed.entries[:10]:  # Limitar a las primeras 10 entradas de cada feed
            noticias.append({
                "titulo": entrada.title,
                "resumen": limpiar_html(entrada.get("summary", "")),
                "url": entrada.link,
                "fuente": feed.feed.get("title", "Desconocido"),
                "tipo": "general"
            })
    return noticias[:max_noticias]

def obtener_noticias_latinas(max_noticias: int = 10) -> list:
    api_key = os.getenv("NEWSAPI_KEY")
    noticias = []

    for keyword in KEYWORDS_LATINO[:3]:
        url = f"https://newsapi.org/v2/everything?q={keyword}&language=es&sortBy=publishedAt&pageSize=3&apiKey={api_key}"
        response = requests.get(url)
        data = response.json()

        if data.get("status") == "ok":
            for articulo in data.get("articles", []):
                noticias.append({
                    "titulo": articulo["title"],
                    "resumen": articulo.get("description", "")[:300],
                    "url": articulo["url"],
                    "fuente": articulo["source"]["name"],
                    "tipo": "latino"
                })

    return noticias[:max_noticias]

def obtener_todas_noticias() -> list:
    generales = obtener_noticias_rss()
    latinas = obtener_noticias_latinas()
    return generales + latinas

def mostrar_noticias(noticias: list):
    print("\n📰 NOTICIAS DISPONIBLES:\n")
    for i, noticia in enumerate(noticias):
        emoji = "🌍" if noticia["tipo"] == "general" else "🎵"
        print(f"{i+1}. {emoji} [{noticia['fuente']}] {noticia['titulo']}")
        print(f"   {noticia['resumen'][:100]}...")
        print()

# Prueba
if __name__ == "__main__":
    noticias = obtener_todas_noticias()
    mostrar_noticias(noticias)