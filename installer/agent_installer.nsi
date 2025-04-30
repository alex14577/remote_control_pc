!include "MUI2.nsh"
!define VERSION "$%VERSION%"

RequestExecutionLevel admin

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
  File "..\dist\agent_service.exe"

  ; Регистрация для удаления
  WriteRegStr HKLM "Software\Agent" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "DisplayName" "Agent Service"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "DisplayVersion" "${VERSION}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "NoRepair" 1

  WriteUninstaller "${UNINSTALL_EXE}"

  nsExec::Exec '"$INSTDIR\agent_service.exe"'
SectionEnd


; Секция удаления
Section "Uninstall"
  ; Остановить и удалить службу через обёртку
  nsExec::Exec '"$INSTDIR\agent_service.exe" remove'
  Sleep 2000

  Delete "$INSTDIR\agent.exe"
  Delete "$INSTDIR\config.json"
  Delete "$INSTDIR\agent_service.exe"
  Delete "$INSTDIR\agent.log"
  Delete "${UNINSTALL_EXE}"
  RMDir "$INSTDIR"

  DeleteRegKey HKLM "Software\Agent"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent"
SectionEnd
