!include "MUI2.nsh"
!define VERSION "$%VERSION%"

Outfile "installer-bot-windows-v${VERSION}.exe"
InstallDir "$PROGRAMFILES\Bot"

Section "Install Bot"
  SetOutPath "$INSTDIR"
  File "..\dist\bot.exe"
  File "..\bot\config.json"

  WriteRegStr HKLM "SOFTWARE\Bot" "Path" "$INSTDIR\bot.exe"

  ; Создаём сервис
  nsExec::Exec 'sc.exe create BotService binPath= "\"$INSTDIR\bot.exe\"" start= auto DisplayName= "Bot Service"'
  ; Настраиваем автоматический перезапуск
  nsExec::Exec 'sc.exe failure "BotService" reset= 60 actions= restart/5000'
  ; Запускаем сервис
  nsExec::Exec 'sc.exe start BotService'
SectionEnd

Section "Uninstall Bot"
  nsExec::Exec 'sc.exe stop BotService'
  Sleep 2000
  nsExec::Exec 'sc.exe delete BotService'

  Delete "$INSTDIR\bot.exe"
  Delete "$INSTDIR\config.json"
  RMDir "$INSTDIR"
  DeleteRegKey HKLM "SOFTWARE\Bot"
SectionEnd
