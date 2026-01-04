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
        
@lru_cache()
def get_online_versions():
    res = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=5)
    res.raise_for_status()
    return res.json()

def get_local_versions(mc_path: Optional[Path] = None):
    if not mc_path: mc_path = get_minecraft_dir()
    versions_path = mc_path / 'versions'
    if not versions_path.exists(): return []
    return sorted([v for v in versions_path.iterdir() if v.is_dir()], key=lambda p: p.stat().st_atime)

def get_accounts(mc_path: Optional[Path] = None):
    if not mc_path: mc_path = get_minecraft_dir()

    accounts_path = mc_path / 'cesena_accounts.json'

    default = { "selected": None, "accounts": [] }

    if (not accounts_path.exists()):
        accounts_path.touch()
        accounts_path.write_text(json.dumps(default))
        return default
    
    try:
        return json.loads(accounts_path.read_text())
    except json.JSONDecodeError:
        return default
    
def get_selected_username(mc_path: Optional[Path] = None):
    return get_accounts().get("selected", "player") or "player"
    
def save_accounts(accounts, mc_path: Optional[Path] = None):
    if not mc_path: mc_path = get_minecraft_dir()
    accounts_path = mc_path / 'cesena_accounts.json'
    accounts_path.write_text(json.dumps(accounts))