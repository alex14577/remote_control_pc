import os
import psutil
import subprocess
import getpass
import unicodedata

def normalize_name(name: str) -> str:
    if not name:
        return ""
    name = name.lower().replace('µ', 'u')
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    return name.replace('.exe', '').strip()

def is_process_running(path: str) -> bool:
    if not path or not os.path.exists(path):
        return False
    exe_name = os.path.basename(path).lower()
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == exe_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def launch_with_task(path: str, task_name: str = "AgentLaunchTask") -> None:
    subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    create_cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", f'"{path}"',
        "/sc", "ONCE",
        "/st", "00:00",
        "/f",
        "/rl", "HIGHEST",
        "/ru", getpass.getuser()
    ]
    subprocess.run(" ".join(create_cmd), shell=True, check=True, capture_output=True)
    subprocess.run(["schtasks", "/run", "/tn", task_name], check=True, capture_output=True)
