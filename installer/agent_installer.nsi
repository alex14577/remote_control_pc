!include "MUI2.nsh"
!define VERSION "$%VERSION%"

Outfile "installer-agent-windows-v${VERSION}.exe"
InstallDir "$PROGRAMFILES\Agent"

Section "Install Agent"
  SetOutPath "$INSTDIR"
  File "..\dist\agent.exe"
  File "..\agent\config.json"

  WriteRegStr HKLM "SOFTWARE\Agent" "Path" "$INSTDIR\agent.exe"

  nsExec::Exec 'sc.exe create AgentService binPath= "\"$INSTDIR\agent.exe\"" start= auto DisplayName= "Agent Service"'
  nsExec::Exec 'sc.exe failure "AgentService" reset= 60 actions= restart/5000'
  nsExec::Exec 'sc.exe start AgentService'
SectionEnd

Section "Uninstall Agent"
  nsExec::Exec 'sc.exe stop AgentService'
  Sleep 2000
  nsExec::Exec 'sc.exe delete AgentService'

  Delete "$INSTDIR\agent.exe"
  Delete "$INSTDIR\config.json"
  RMDir "$INSTDIR"
  DeleteRegKey HKLM "SOFTWARE\Agent"
SectionEnd
