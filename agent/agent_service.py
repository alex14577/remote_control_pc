import os
import sys
import subprocess
import win32event
import win32service
import win32serviceutil
import pywintypes
import threading
import time


class AgentService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AgentService"
    _svc_display_name_ = "Agent Service"
    _svc_description_ = "Runs agent.exe with config.json"

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        self._log("Initialized AgentService")

    def SvcStop(self):
        self._log("SvcStop called")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self._log("Terminated agent.exe")
            except Exception as e:
                self._log(f"Failed to terminate agent.exe: {e}")
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        self._log("SvcDoRun called")
        print(">>> SvcDoRun called")

        # Запуск run_agent в отдельном потоке, чтобы не блокировать SvcDoRun
        thread = threading.Thread(target=self.run_agent, daemon=True)
        thread.start()
        self._log("Thread for run_agent started")

        # Ожидаем сигнал остановки службы
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
        self._log("Service stopping...")

    def run_agent(self):
        self._log("Entered run_agent()")
        print(">>> run_agent() entered")

        try:
            base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(__file__)
            agent = os.path.join(base, "agent.exe")
            config = os.path.join(base, "config.json")
            log_file_path = os.path.join(base, "agent.log")

            self._log(f"Agent path: {agent}")
            self._log(f"Config path: {config}")

            if not os.path.exists(agent):
                self._log("ERROR: agent.exe not found!")
                return
            if not os.path.exists(config):
                self._log("ERROR: config.json not found!")
                return

            with open(log_file_path, "a", buffering=1, encoding="utf-8") as log_file:
                self.process = subprocess.Popen(
                    [agent, "-f", config],
                    stdout=log_file,
                    stderr=subprocess.STDOUT
                )
                self._log("agent.exe started")
                self.process.wait()
                self._log(f"agent.exe exited with code {self.process.returncode}")

            # Если процесс завершился — инициируем остановку службы
            win32event.SetEvent(self.stop_event)

        except Exception as e:
            self._log(f"ERROR: Failed to start agent.exe: {e}")
            win32event.SetEvent(self.stop_event)

    def _log(self, msg):
        try:
            log_path = os.path.join(os.path.dirname(__file__), "agent_service.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
        except Exception:
            pass


def service_exists(name):
    try:
        win32serviceutil.QueryServiceStatus(name)
        return True
    except pywintypes.error as e:
        if hasattr(e, 'winerror') and e.winerror == 1060:
            return False
        elif e.args and e.args[0] == 1060:
            return False
        raise


if __name__ == "__main__":

    application_path = os.path.dirname(sys.executable)
    os.chdir(application_path)

    name = AgentService._svc_name_

    if len(sys.argv) == 1:
        if not service_exists(name):
            try:
                win32serviceutil.InstallService(
                    pythonClassString="agent_service.AgentService",
                    serviceName=name,
                    displayName=AgentService._svc_display_name_,
                    description=AgentService._svc_description_,
                    exeName=sys.executable,
                    startType=win32service.SERVICE_AUTO_START
                )
                print("✅ Service installed")
            except Exception as e:
                print(f"❌ Install failed: {e}")

        try:
            win32serviceutil.StartService(name)
            print("▶️ Service started")
        except Exception as e:
            print(f"❌ Start failed: {e}")

    elif sys.argv[1].lower() == "remove":
        try:
            win32serviceutil.StopService(name)
        except Exception:
            pass
        try:
            win32serviceutil.RemoveService(name)
            print("🗑️ Service removed")
        except Exception as e:
            print(f"❌ Remove failed: {e}")

    else:
        win32serviceutil.HandleCommandLine(AgentService)
