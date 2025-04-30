!include "MUI2.nsh"
!define VERSION "$%VERSION%"

Outfile "installer-agent-windows-v${VERSION}.exe"
InstallDir "$PROGRAMFILES\Agent"
InstallDirRegKey HKLM "Software\Agent" "Install_Dir"

!define UNINSTALL_EXE "$INSTDIR\uninstall.exe"

; Добавим логотип/иконку, если хочешь — напомни

; Главная секция установки
Section "Install Agent"
  SetOutPath "$INSTDIR"
  File "..\dist\agent.exe"
  File "..\agent\config.json"

  ; Сохраняем путь
  WriteRegStr HKLM "Software\Agent" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "DisplayName" "Agent Service"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "DisplayVersion" "${VERSION}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "NoRepair" 1

  ; Сохраняем сам uninstall.exe
  WriteUninstaller "${UNINSTALL_EXE}"

  ; Создаём и запускаем службу
  nsExec::Exec 'sc.exe create AgentService binPath= "\"$INSTDIR\agent.exe\"" start= auto DisplayName= "Agent Service"'
  nsExec::Exec 'sc.exe failure "AgentService" reset= 60 actions= restart/5000'
  nsExec::Exec 'sc.exe start AgentService'
SectionEnd

; Секция удаления
Section "Uninstall"
  nsExec::Exec 'sc.exe stop AgentService'
  Sleep 2000
  nsExec::Exec 'sc.exe delete AgentService'

  Delete "$INSTDIR\agent.exe"
  Delete "$INSTDIR\config.json"
  Delete "${UNINSTALL_EXE}"
  RMDir "$INSTDIR"

  DeleteRegKey HKLM "Software\Agent"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent"
SectionEnd
