from pathlib import Path
import os, platform, sys, shutil, json
from functools import lru_cache
from typing import Optional
import requests
from PySide6.QtCore import QRunnable, QObject, Signal, QThreadPool

class WorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def __call__(self, *args, **kwds):
        self.args = args
        self.kwargs.update(kwds)
        return self
    
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            import traceback
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

pool = QThreadPool()

@lru_cache
def get_minecraft_dir():
    match platform.system().lower():
        case "windows":
            return Path(os.getenv("APPDATA")) / ".minecraft"
        case "linux":
            return Path.home() / ".minecraft"
        case "darwin":
            return Path.home() / "Library/Application Support/minecraft"
        case _:
            return Path.home() / ".minecraft"
        
@lru_cache
def get_config_dir(mc_path: Optional[Path] = None):
    if not mc_path: mc_path = get_minecraft_dir()
    config = mc_path / "cesena"
    config.mkdir(exist_ok=True)
    return config

@lru_cache()
def get_online_versions():
    res = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=5)
    res.raise_for_status()
    return res.json()

def get_local_versions():
    versions = get_minecraft_dir() / 'versions'
    if not versions.exists(): return []
    
    dirs = [v for v in versions.iterdir() if v.is_dir()]
    
    config = get_config()
    saved_order = config.get("instance_order", [])

    def sort(d):
        try:
            return saved_order.index(d.name)
        except ValueError:
            return 9999
            
    return sorted(dirs, key=sort)

def save_instance_order(names_list):
    config = get_config()
    config["instance_order"] = names_list
    save_config(config)

def get_accounts():
    accounts_path = get_config_dir() / 'accounts.json'

    default = { "selected": None, "accounts": [] }

    if (not accounts_path.exists()):
        accounts_path.touch()
        accounts_path.write_text(json.dumps(default))
        return default
    
    try:
        return json.loads(accounts_path.read_text())
    except json.JSONDecodeError:
        return default
    
def get_selected_username():
    return get_accounts().get("selected", "player") or "player"
    
def save_accounts(accounts):
    accounts_path = get_config_dir() / 'accounts.json'
    accounts_path.write_text(json.dumps(accounts))

def get_config_file():
    return get_config_dir() / "config.json"

def get_config():
    f = get_config_file()
    if not f.exists(): return {}
    try: return json.loads(f.read_text())
    except: return {}

def save_config(data):
    get_config_file().write_text(json.dumps(data))

def get_mods_config():
    f = get_config_dir() / 'mods.json'
    if not f.exists(): return {'enabled_mods': []}
    return json.loads(f.read_text())

def save_mods_config(data):
    f = get_config_dir() / 'mods.json'
    f.write_text(json.dumps(data))

def add_mod(mod):
    cfg = get_mods_config()
    if mod not in cfg["enabled_mods"]:
        cfg["enabled_mods"].append(mod)
        save_mods_config(cfg)

def rm_mod(mod):
    cfg = get_mods_config()
    if mod in cfg["enabled_mods"]:
        cfg["enabled_mods"].remove(mod)
        save_mods_config(cfg)

def parse_version_id(version_id: str, with_loader_version = False):
    vid = version_id.lower()

    mc_version = vid.split('-')[0 if vid[0].isdigit() else -1]

    loader_versions = [x for x in vid.split('-') if x[0].isdigit() and x != mc_version]
    loader_version = loader_versions[0] if len(loader_versions) > 0 else None
        
    if "forge" in vid:       v = "forge",     mc_version
    elif "neoforge" in vid:  v = "neoforge",  mc_version
    elif "fabric" in vid:    v = "fabric",    mc_version
    elif "quilt" in vid:     v = "quilt",     mc_version
    else:                    v = "vanilla",   mc_version

    return (*v, loader_version) if with_loader_version else v

def format_vid(version_id: str):
    loader, version, loader_version = parse_version_id(version_id, with_loader_version=True)

    suffix = f" ({loader_version})" if loader_version else ''

    return f"{loader.capitalize()} {version}" + suffix

def get_version_json(version_id, mc_dir):
    if not mc_dir: mc_dir = get_minecraft_dir()
    json_path = mc_dir / "versions" / version_id / f"{version_id}.json"
    if not json_path.exists():
        return None
    try:
        return json.loads(json_path.read_text())
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
    
def short_num(n: int) -> str:
    for unit in ("", "k", "m", "b", "t"):
        if abs(n) < 1000:
            return f"{n:g}{unit}"
        n = round(n / 1000, 1)
    return str(n)