import subprocess as sp
import minecraft_launcher_lib as mclib
import requests
from pathlib import Path

import utils, mod_loader

def clean_jars(version_id: str):
    mc_dir = utils.get_minecraft_dir()
    jar_path = mc_dir / "versions" / version_id / f"{version_id}.jar"
    if jar_path.exists() and jar_path.stat().st_size == 0:
        try: jar_path.unlink()
        except: pass

def launch_mc(version_id: str):
    mc_dir = utils.get_minecraft_dir()

    loader, version = utils.parse_version_id(version_id)

    clean_jars(version_id)

    print(f"[Launcher] Verifying base game ({version_id})...")
    mclib.install.install_minecraft_version(
        version=version_id,
        minecraft_directory=mc_dir,
        callback={"setStatus": print, "setProgress": lambda v: None}
    )

    if loader and loader != "vanilla":
        try:
            mod_loader.prepare_mods(version, loader)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("Mod loading failed, attempting to play anyway...")

    print("Verifying libraries and natives...")
    
    mclib.install.install_libraries(
        version_id,
        utils.get_version_json(version_id, mc_dir).get('libraries', []),
        mc_dir,
        callback={"setStatus": print, "setProgress": lambda v: None},
    )
        
    options = {
        "username": utils.get_selected_username(),
        "uuid": "",
        "token": "",

        "launcherName": "Cesena",
        "gameDirectory": str(mc_dir),
    }

    mc_cmd = mclib.command.get_minecraft_command(
        version = version_id,
        minecraft_directory = mc_dir,
        options = options,
    )

    # print("Launch Command:", ' '.join(mc_cmd))

    proc = sp.Popen(mc_cmd, cwd=mc_dir, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
    return proc