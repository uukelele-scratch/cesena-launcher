from concurrent.futures import ThreadPoolExecutor, as_completed
import os, shutil, hashlib, requests
from pathlib import Path

import utils, modrinth

def dl_file(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    res = requests.get(url, headers=modrinth.HEADERS, stream=True)
    with open(path, 'wb') as f:
        for chunk in res.iter_content(chunk_size=8192):
            f.write(chunk)

def resolve(mod, mc_version, loader, cache_dir):
    print(f"-> Resolving {mod['project_id']}...")
    version = modrinth.get_latest_version(mod['project_id'], mc_version, loader)

    if not version:
        print("  -> No compatible version found!")
        return

    dest = cache_dir / version["filename"]
    if not dest.exists():
        print(f"  -> Downloading {version['filename']} to {dest}...")
        dl_file(version['url'], dest)

    return dest, version.get('dependencies', [])

def prepare_mods(mc_version: str, loader: str = 'fabric'):
    print(f"Loading mods for {mc_version} ({loader})...")

    wanted = utils.get_mods_config().get('enabled_mods', [])
    
    mc_dir = utils.get_minecraft_dir()
    mods_dir = mc_dir / 'mods'
    cache_dir = utils.get_config_dir() / 'mods_cache' / f"{mc_version}-{loader}"
    
    cache_dir.mkdir(parents=True, exist_ok=True)

    files = set()
    processed = set()

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for mod in wanted:
            if not mod['project_id'] in processed:
                processed.add(mod['project_id'])
                futures[executor.submit(resolve, mod, mc_version, loader, cache_dir)] = mod

        while futures:
            done, _ = as_completed(futures), None
            for future in list(futures):
                if future.done():
                    mod = futures.pop(future)
                    try:
                        res = future.result()
                        if res:
                            path, deps = res
                            files.add(path)

                            for dep in deps:
                                if dep.get("dependency_type") == "required":
                                    print(f"  -> Adding dependency to queue: {dep['project_id']}")
                                    processed.add(dep['project_id'])
                                    futures[executor.submit(resolve, dep, mc_version, loader, cache_dir)] = dep
                    except Exception as e:
                        import traceback
                        traceback.print_exc()

    if mods_dir.exists():
        for item in mods_dir.iterdir():
            if item.is_file() and item.suffix == '.jar':
                item.unlink()
    else:
        mods_dir.mkdir()

    print(f"Copying {len(files)} mods...")
    for file in files:
        shutil.copy2(file, mods_dir / file.name)

    print("Mods Ready.")
