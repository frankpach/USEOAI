import json

with open('resultado_online.json', encoding='utf-8') as f:
    raw = f.read().strip()
    if not raw or not raw.startswith('{'):
        print('El archivo no contiene JSON válido.')
        exit(1)
    data = json.loads(raw)

# Extraer detalles
imgs = data.get('images_without_alt', [])
imgs_list = [img.get('src') for img in imgs if img.get('src')]

links = data.get('links', {})
broken = links.get('broken', [])

issues = data.get('issues', [])
issues_list = []
if isinstance(issues, list):
    for issue in issues:
        issues_list.append({
            'title': issue.get('title'),
            'description': issue.get('description'),
            'priority': issue.get('priority')
        })

llm_recs = data.get('llm_recommendations', [])

# Estructura para exportar
resumen = {
    'images_without_alt': imgs_list,
    'broken_links': broken,
    'issues': issues_list,
    'llm_recommendations': llm_recs
}

with open('resumen_errores.json', 'w', encoding='utf-8') as f:
    json.dump(resumen, f, ensure_ascii=False, indent=2)

# También imprimir para el usuario
print('--- Imágenes sin alt ---')
print('\n'.join(imgs_list) if imgs_list else 'Ninguna')
print('\n--- Enlaces rotos ---')
print('\n'.join(broken) if broken else 'Ninguno')
print('\n--- Issues detectados ---')
for issue in issues_list:
    print(f"- {issue['title']}: {issue['description']} (Prioridad: {issue['priority']})")
print('\n--- Recomendaciones LLM ---')
print('\n'.join(llm_recs) if llm_recs else 'Ninguna')
