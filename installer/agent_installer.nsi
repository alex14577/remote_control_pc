!include "MUI2.nsh"
!define VERSION "$%VERSION%"

RequestExecutionLevel admin

Outfile "installer-agent-windows-v${VERSION}.exe"
InstallDir "$PROGRAMFILES\Agent"
InstallDirRegKey HKLM "Software\Agent" "Install_Dir"

!define UNINSTALL_EXE "$INSTDIR\uninstall.exe"

Section "Install Agent"
  SetOutPath "$INSTDIR"
  DetailPrint "[INFO] Installation started"

  File "..\dist\agent.exe"
  File "..\agent\config.json"
  File "..\dist\agent_service.exe"
  DetailPrint "[OK] Files copied"

  WriteRegStr HKLM "Software\Agent" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "DisplayName" "Agent Service"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "DisplayVersion" "${VERSION}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "NoRepair" 1
  DetailPrint "[OK] Registry updated"

  WriteUninstaller "${UNINSTALL_EXE}"
  DetailPrint "[OK] Uninstaller created"

  nsExec::ExecToStack '"$INSTDIR\agent_service.exe" install'
  Pop $0
  ${If} $0 != 0
    DetailPrint "[ERROR] Service installation failed (code $0)"
    MessageBox MB_ICONSTOP "Failed to install the service"
  ${Else}
    DetailPrint "[OK] Service installed"
  ${EndIf}

  nsExec::ExecToStack '"$INSTDIR\agent_service.exe" start'
  Pop $0
  ${If} $0 != 0
    DetailPrint "[ERROR] Service failed to start (code $0)"
    MessageBox MB_ICONSTOP "Failed to start the service"
  ${Else}
    DetailPrint "[OK] Service started"
  ${EndIf}

  DetailPrint "[INFO] Installation complete"
SectionEnd


Section "Uninstall"
  DetailPrint "[INFO] Uninstallation started"

  nsExec::ExecToStack '"$INSTDIR\agent_service.exe" remove'
  Pop $0
  ${If} $0 != 0
    DetailPrint "[ERROR] Failed to remove service (code $0)"
  ${Else}
    DetailPrint "[OK] Service removed"
  ${EndIf}

  Sleep 2000

  Delete "$INSTDIR\agent.exe"
  Delete "$INSTDIR\config.json"
  Delete "$INSTDIR\agent_service.exe"
  Delete "$INSTDIR\agent.log"
  Delete "${UNINSTALL_EXE}"
  DetailPrint "[OK] Files deleted"

  RMDir "$INSTDIR"
  DetailPrint "[OK] Folder removed"

  DeleteRegKey HKLM "Software\Agent"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent"
  DetailPrint "[OK] Registry cleaned"

  DetailPrint "[INFO] Uninstallation complete"
SectionEnd
