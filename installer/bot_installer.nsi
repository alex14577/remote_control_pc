!include 'MUI2.nsh'

!define VERSION "${VERSION}"

Outfile 'installer-bot-windows-v${VERSION}.exe'
InstallDir $TEMP

Section
  SetOutPath $INSTDIR
  File "..\dist\bot.exe"
  File "..\bot\config.json"

  WriteRegStr HKLM "SOFTWARE\Bot" "Path" "$INSTDIR\bot.exe"
  ExecWait "$INSTDIR\bot.exe -f $INSTDIR\config.json" 
SectionEnd
