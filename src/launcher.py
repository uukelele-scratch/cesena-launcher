import subprocess as sp
import minecraft_launcher_lib as mclib
from pathlib import Path
import utils

def launch_mc(version_id: str):
    mc_dir = utils.get_minecraft_dir()

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

    print("Launch Command:", ' '.join(mc_cmd))

    proc = sp.Popen(mc_cmd, cwd=mc_dir, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
    return proc