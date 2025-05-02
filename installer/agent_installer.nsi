!include "MUI2.nsh"
!define VERSION "$%VERSION%"

RequestExecutionLevel admin

Outfile "installer-agent-windows-v${VERSION}.exe"
InstallDir "$PROGRAMFILES\Agent"
InstallDirRegKey HKLM "Software\Agent" "Install_Dir"

!define UNINSTALL_EXE "$INSTDIR\uninstall.exe"

Section "Install Agent"
  SetOutPath "$INSTDIR"
  DetailPrint "--- Установка начата ---"

  File "..\dist\agent.exe"
  File "..\agent\config.json"
  File "..\dist\agent_service.exe"
  DetailPrint "✔️ Файлы скопированы"

  WriteRegStr HKLM "Software\Agent" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "DisplayName" "Agent Service"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "DisplayVersion" "${VERSION}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent" "NoRepair" 1
  DetailPrint "✔️ Реестр обновлён"

  WriteUninstaller "${UNINSTALL_EXE}"
  DetailPrint "✔️ Uninstaller создан"

  nsExec::ExecToStack '"$INSTDIR\agent_service.exe" install'
  Pop $0
  ${If} $0 != 0
    DetailPrint "❌ Ошибка установки службы (код $0)"
    MessageBox MB_ICONSTOP "❌ Не удалось установить службу"
  ${Else}
    DetailPrint "✔️ Служба установлена"
  ${EndIf}

  nsExec::ExecToStack '"$INSTDIR\agent_service.exe" start'
  Pop $0
  ${If} $0 != 0
    DetailPrint "❌ Ошибка запуска службы (код $0)"
    MessageBox MB_ICONSTOP "❌ Не удалось запустить службу"
  ${Else}
    DetailPrint "✔️ Служба запущена"
  ${EndIf}

  DetailPrint "--- Установка завершена ---"
SectionEnd


Section "Uninstall"
  DetailPrint "--- Удаление начато ---"

  nsExec::ExecToStack '"$INSTDIR\agent_service.exe" remove'
  Pop $0
  ${If} $0 != 0
    DetailPrint "⚠️ Ошибка при удалении службы (код $0)"
  ${Else}
    DetailPrint "✔️ Служба удалена"
  ${EndIf}

  Sleep 2000

  Delete "$INSTDIR\agent.exe"
  Delete "$INSTDIR\config.json"
  Delete "$INSTDIR\agent_service.exe"
  Delete "$INSTDIR\agent.log"
  Delete "${UNINSTALL_EXE}"
  DetailPrint "✔️ Файлы удалены"

  RMDir "$INSTDIR"
  DetailPrint "✔️ Папка удалена"

  DeleteRegKey HKLM "Software\Agent"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Agent"
  DetailPrint "✔️ Реестр очищен"

  DetailPrint "--- Удаление завершено ---"
SectionEnd
