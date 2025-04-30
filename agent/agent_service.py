import os
import sys
import subprocess
import win32event
import win32service
import win32serviceutil
import pywintypes


class AgentService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AgentService"
    _svc_display_name_ = "Agent Service"
    _svc_description_ = "Runs agent.exe with config.json as a background service."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.process:
            try:
                self.process.terminate()
            except Exception as e:
                self._log(f"Failed to terminate process: {e}")
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        base = (
            os.path.dirname(sys.executable)
            if getattr(sys, "frozen", False)
            else os.path.dirname(__file__)
        )
        agent_path = os.path.join(base, "agent.exe")
        config_path = os.path.join(base, "config.json")
        log_path = os.path.join(base, "agent.log")

        try:
            log_file = open(log_path, "a", buffering=1)
            self.process = subprocess.Popen(
                [agent_path, "-f", config_path],
                stdout=log_file,
                stderr=subprocess.STDOUT
            )
            self._log(f"Started process: {agent_path} -f {config_path}")
        except Exception as e:
            self._log(f"Failed to start agent: {e}")
            return

        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

    def _log(self, message):
        try:
            with open(os.path.join(os.path.dirname(__file__), "agent_service.log"), "a") as log:
                log.write(message + "\n")
        except Exception:
            pass


def service_exists(name):
    try:
        win32serviceutil.QueryServiceStatus(name)
        return True
    except pywintypes.error as e:
        if e.winerror == 1060:  # service does not exist
            return False
        raise


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Автоматическая установка и запуск, если службы нет
        if not service_exists(AgentService._svc_name_):
            try:
                win32serviceutil.InstallService(
                    AgentService,
                    AgentService._svc_name_,
                    AgentService._svc_display_name_,
                    startType=win32service.SERVICE_AUTO_START
                )
                print("✅ Service installed")
            except Exception as e:
                print(f"❌ Install failed: {e}")

        try:
            win32serviceutil.StartService(AgentService._svc_name_)
            print("▶️ Service started")
        except Exception as e:
            print(f"❌ Start failed: {e}")

    elif sys.argv[1].lower() == "remove":
        try:
            win32serviceutil.StopService(AgentService._svc_name_)
        except Exception:
            pass
        try:
            win32serviceutil.RemoveService(AgentService._svc_name_)
            print("🗑️ Service removed")
        except Exception as e:
            print(f"❌ Remove failed: {e}")

    else:
        # Поддержка install/start/stop/remove/etc
        win32serviceutil.HandleCommandLine(AgentService)
