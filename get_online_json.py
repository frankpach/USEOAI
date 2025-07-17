import requests

response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "url": "https://deluxesmartfilm.com/",
        "seo_goal": "Posicionamiento de Servicios Profesionales",
        "language": "es",
        "sector": "Otro",
        "location": "",
        "keywords": "",
        "local_radius_km": 5,
        "geo_samples": 10,
        "llm_provider": "gemini",
        "force_playwright": False
    }
)
with open("resultado_online.json", "w", encoding="utf-8") as f:
    f.write(response.text)
print("Respuesta guardada en resultado_online.json")
