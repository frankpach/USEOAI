import requests

url = "http://localhost:8000/api/analyses/html"
files = {'html_file': open('view-source_https___deluxesmartfilm.com.html', 'rb')}
data = {
    'url': 'https://deluxesmartfilm.com/',
    'seo_goal': 'Posicionamiento de Servicios Profesionales',
    'language': 'es',
    'sector': 'Otro',
    'location': '',
    'keywords': '',
    'local_radius_km': '5',
    'geo_samples': '10',
    'llm_provider': 'gemini',
    'force_playwright': 'false'
}
response = requests.post(url, files=files, data=data)
with open('resultado_html.json', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Respuesta guardada en resultado_html.json")
