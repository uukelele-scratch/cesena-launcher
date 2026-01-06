import os, shutil, hashlib, requests
from pathlib import Path

import utils, modrinth

def dl_file(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    res = requests.get(url, headers=modrinth.HEADERS, stream=True)
    with open(path, 'wb') as f:
        for chunk in res.iter_content(chunk_size=8192):
            f.write(chunk)

def prepare_mods(mc_version: str, loader: str = 'fabric'):
    print(f"Loading mods for {mc_version} ({loader})...")

    wanted = utils.get_mods_config().get('enabled_mods', [])
    
    mc_dir = utils.get_minecraft_dir()
    mods_dir = mc_dir / 'mods'
    cache_dir = utils.get_config_dir() / 'mods_cache' / f"{mc_version}-{loader}"
    
    cache_dir.mkdir(parents=True, exist_ok=True)

    files = []
    process_q = list(wanted)
    processed = set()

    while process_q:
        mod = process_q.pop(0)
        if mod['project_id'] in processed: continue
        processed.add(mod['project_id'])

        print(f"-> Resolving {mod['project_id']}...")
        version = modrinth.get_latest_version(mod['project_id'], mc_version, loader)

        if not version:
            print("  -> No compatible version found!")
            continue

        dest = cache_dir / version["filename"]
        if not dest.exists():
            print(f"  -> Downloading {version['filename']} to {dest}...")
            dl_file(version['url'], dest)

        files.append(dest)

        for dep in version['dependencies']:
            if dep.get("dependency_type") == "required":
                proj_id = dep.get("project_id")
                if proj_id and proj_id not in processed:
                    print(f"  -> Adding dependency to queue: {proj_id}")
                    process_q.append(dep)

    if mods_dir.exists():
        for item in mods_dir.iterdir():
            if item.is_file() and item.suffix == '.jar':
                item.unlink()
    else:
        mods_dir.mkdir()

    print(f"Copying {len(files)} mods...")
    for src in files:
        dst = mods_dir / src.name
        shutil.copy2(src, dst)

    print("Mods Ready.")
