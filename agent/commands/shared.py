import os
import psutil
import subprocess
import getpass
import unicodedata

from agent.logger import Logger


logger = Logger().Get("launcher")

def resolve_lnk(path: str) -> str:
    if path.lower().endswith(".lnk"):
        try:
            with open(path, "rb") as f:
                lnk = pylnk3.parse(f)
                if lnk.path:
                    return lnk.path
        except Exception as e:
            logger.error(f"Failed to resolve .lnk: {e}")
    return path


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
    # Разрешаем ярлык в exe (если это .lnk)
    real_path = resolve_lnk(path)
    logger.info(f"Resolved launch path: {real_path}")

    # Удалим старую задачу
    subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Создаём новую задачу
    create_cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", f'"{real_path}"',
        "/sc", "ONCE",
        "/st", "00:00",
        "/f",
        "/rl", "HIGHEST",
        "/ru", getpass.getuser()
    ]

    logger.info(f"Creating task: {' '.join(create_cmd)}")
    result = subprocess.run(" ".join(create_cmd), shell=True, capture_output=True, text=True)
    logger.info(f"Create stdout: {result.stdout.strip()}")
    if result.stderr:
        logger.error(f"Create stderr: {result.stderr.strip()}")
    result.check_returncode()

    # Запускаем задачу
    run_cmd = ["schtasks", "/run", "/tn", task_name]
    logger.info(f"Running task: {' '.join(run_cmd)}")
    result = subprocess.run(run_cmd, capture_output=True, text=True)
    logger.info(f"Run stdout: {result.stdout.strip()}")
    if result.stderr:
        logger.error(f"Run stderr: {result.stderr.strip()}")
    result.check_returncode()