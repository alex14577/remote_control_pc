# agent/system_info.py
import platform
import psutil

def get_system_info() -> str:
    """
    Формирует текстовую информацию о системе для отправки через Telegram.
    """
    try:
        info = [
            f"🖥️ Система: {platform.system()} {platform.release()} ({platform.machine()})",
            f"🧠 CPU: {platform.processor()} / {psutil.cpu_count(logical=True)} ядер",
            f"💾 RAM: {round(psutil.virtual_memory().total / (1024 ** 3), 2)} ГБ"
        ]
        return "\n".join(info)
    except Exception as e:
        return f"❌ Ошибка получения информации о системе: {e}"
