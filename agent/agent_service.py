import win32serviceutil
import win32service
import win32event
import subprocess
import os
import sys

class AgentService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AgentService"
    _svc_display_name_ = "Agent Service"
    _svc_description_ = "My agent that runs with arguments"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.process:
            self.process.terminate()
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        base = os.path.dirname(__file__)
        agent = os.path.join(base, "agent.exe")
        config = os.path.join(base, "config.json")
        log = open(os.path.join(base, "agent.log"), "a")

        self.process = subprocess.Popen(
            [agent, "-f", config],
            stdout=log,
            stderr=subprocess.STDOUT
        )

        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Если запущен без аргументов — устанавливаем и запускаем
        if not win32serviceutil.QueryServiceStatus(AgentService._svc_name_):
            try:
                win32serviceutil.InstallService(
                    AgentService,
                    AgentService._svc_name_,
                    AgentService._svc_display_name_,
                    startType=win32service.SERVICE_AUTO_START
                )
                print("Service installed")
            except Exception as e:
                print("Install failed:", e)
        try:
            win32serviceutil.StartService(AgentService._svc_name_)
            print("Service started")
        except Exception as e:
            print("Start failed:", e)
    else:
        # Режим управления
        win32serviceutil.HandleCommandLine(AgentService)
