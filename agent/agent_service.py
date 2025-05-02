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

        base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(__file__)
        agent = os.path.join(base, "agent.exe")
        config = os.path.join(base, "config.json")
        log_file_path = os.path.join(base, "agent.log")

        self._log(f"Agent path: {agent}")
        self._log(f"Config path: {config}")

        if not os.path.exists(agent):
            self._log(f"ERROR: agent.exe not found at {agent}")
            return
        if not os.path.exists(config):
            self._log(f"ERROR: config.json not found at {config}")
            return

        try:
            with open(log_file_path, "a", buffering=1, encoding="utf-8") as log_file:
                self.process = subprocess.Popen(
                    [agent, "-f", config],
                    stdout=log_file,
                    stderr=subprocess.STDOUT
                )
                self._log("agent.exe started")
                self.process.wait()
                self._log("agent.exe exited")
        except Exception as e:
            self._log(f"ERROR: Failed to start agent.exe: {e}")
            return

        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

    def _log(self, msg):
        try:
            with open(os.path.join(os.path.dirname(__file__), "agent_service.log"), "a", encoding="utf-8") as f:
                f.write(f"[{self._timestamp()}] {msg}\n")
        except Exception as e:
            print(f"Logging failed: {e}")

    def _timestamp(self):
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")


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
