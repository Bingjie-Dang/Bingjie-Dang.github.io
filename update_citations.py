from scholarly import scholarly
import json
from pathlib import Path

author_id = "Mfp83rUAAAAJ"

author = scholarly.search_author_id(author_id)
author = scholarly.fill(author, sections=['publications'])

items = []
for pub in author.get('publications', []):
    try:
        full = scholarly.fill(pub)
    except Exception:
        full = pub
    title = full.get('bib', {}).get('title', '').strip()
    if not title:
        continue
    items.append({
        'title': title,
        'citations': int(full.get('num_citations', 0) or 0)
    })

items.sort(key=lambda x: x['title'].lower())
Path('citations.json').write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'updated {len(items)} records')
