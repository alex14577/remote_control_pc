!include "MUI2.nsh"

!define VERSION "${VERSION}"

Outfile "installer-agent-windows-v${VERSION}.exe"
InstallDir $TEMP

Section
  SetOutPath $INSTDIR
  File "..\\dist\\agent.exe"
  File "..\\agent\\config.json"
  WriteRegStr HKLM "SOFTWARE\\Agent" "Path" "$INSTDIR\\agent.exe"
  ExecWait '"$INSTDIR\\agent.exe" -f "$INSTDIR\\config.json"'
SectionEnd
