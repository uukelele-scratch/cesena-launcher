import requests
from json import dumps as j

HEADERS = {
    "User-Agent": "uukelele-scratch/cesena/1.0",
}

BASE_URL = "https://api.modrinth.com/v2"

def search_mods(query: str):
    url = BASE_URL + '/search'

    res = requests.get(
        url,
        params = {
            'query':   query,
            'facets':  j([['project_type:mod']]),
        },
        headers = HEADERS,
        timeout = 5.
    )
    res.raise_for_status()
    hits = res.json().get('hits', [])
    return [
        {
            "project_id":   h["project_id"],
            "title":        h["title"],
            "description":  h["description"],
            "icon_url":     h["icon_url"],
        }
        for h in hits
    ]

def get_latest_version(id, version, loader='fabric'):
    url = BASE_URL + f"/project/{id}/version"
    
    res = requests.get(
        url,
        params = {
            'loaders':        j([loader]),
            'game_versions':  j([version]),
        },
        headers = HEADERS,
        timeout = 5,
    )
    res.raise_for_status()
    versions = res.json()

    if not versions: return None

    latest = versions[0]

    files = latest.get('files', [])
    primary = next((f for f in files if f.get('primary')), files[0] if files else None)

    if not primary: return None

    return {
        "filename":      primary["filename"],
        "url":           primary["url"],
        "hash":          primary["hashes"]["sha1"],
        "dependencies":  latest.get("dependencies", []),
    }