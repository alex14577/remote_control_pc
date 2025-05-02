!include "MUI2.nsh"
!define VERSION "$%VERSION%"

RequestExecutionLevel admin

Outfile "installer-agent-windows-v${VERSION}.exe"
InstallDir "$PROGRAMFILES\Agent"
InstallDirRegKey HKLM "Software\Agent" "Install_Dir"

!define UNINSTALL_EXE "$INSTDIR\uninstall.exe"

Section "Install Agent"
  SetOutPath "$INSTDIR"
  DetailPrint "[INFO] Установка начата"

  File "..\dist\agent.exe"
  File "..\agent\config.json"
  File "..\dist\agent_service.exe"
  DetailPrint "[OK] Файлы скопированы"

  WriteRegStr HKLM "Software\Agent" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "DisplayName" "Agent Service"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "DisplayVersion" "${VERSION}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "NoRepair" 1
  DetailPrint "[OK] Реестр обновлён"

  WriteUninstaller "${UNINSTALL_EXE}"
  DetailPrint "[OK] Uninstaller создан"

  nsExec::ExecToStack '"$INSTDIR\agent_service.exe" install'
  Pop $0
  ${If} $0 != 0
    DetailPrint "[ERROR] Установка службы не удалась (код $0)"
    MessageBox MB_ICONSTOP "Не удалось установить службу"
  ${Else}
    DetailPrint "[OK] Служба установлена"
  ${EndIf}

  nsExec::ExecToStack '"$INSTDIR\agent_service.exe" start'
  Pop $0
  ${If} $0 != 0
    DetailPrint "[ERROR] Ошибка запуска службы (код $0)"
    MessageBox MB_ICONSTOP "Не удалось запустить службу"
  ${Else}
    DetailPrint "[OK] Служба запущена"
  ${EndIf}

  DetailPrint "[INFO] Установка завершена"
SectionEnd


Section "Uninstall"
  DetailPrint "[INFO] Удаление начато"

  nsExec::ExecToStack '"$INSTDIR\agent_service.exe" remove'
  Pop $0
  ${If} $0 != 0
    DetailPrint "[ERROR] Ошибка при удалении службы (код $0)"
  ${Else}
    DetailPrint "[OK] Служба удалена"
  ${EndIf}

  Sleep 2000

  Delete "$INSTDIR\agent.exe"
  Delete "$INSTDIR\config.json"
  Delete "$INSTDIR\agent_service.exe"
  Delete "$INSTDIR\agent.log"
  Delete "${UNINSTALL_EXE}"
  DetailPrint "[OK] Файлы удалены"

  RMDir "$INSTDIR"
  DetailPrint "[OK] Папка удалена"

  DeleteRegKey HKLM "Software\Agent"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent"
  DetailPrint "[OK] Реестр очищен"

  DetailPrint "[INFO] Удаление завершено"
SectionEnd
