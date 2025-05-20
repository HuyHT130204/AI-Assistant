!macro customInit
  ; Custom initialization code
!macroend

!macro customRemoveFiles
  ; Delete the entire face_data directory in AppData\Local\AI-Assistant
  RMDir /r "$LOCALAPPDATA\AI-Assistant\face_data"
  ; Wait a bit to ensure deletion completes
  Sleep 1000
  
  ; Try again with explicit path to samples and trainer
  RMDir /r "$LOCALAPPDATA\AI-Assistant\face_data\samples"
  RMDir /r "$LOCALAPPDATA\AI-Assistant\face_data\trainer"
  Sleep 1000
  
  ; Execute the batch file to ensure cleanup
  !ifdef NSIS_UNICODE
    ExecWait '"$SYSDIR\cmd.exe" /c "$INSTDIR\resources\app\electron\build\cleanup.bat"'
  !else
    ExecWait '"$SYSDIR\cmd.exe" /c "$INSTDIR\resources\app\electron\build\cleanup.bat"'
  !endif
  
  ; Ensure parent directory is removed if empty
  RMDir "$LOCALAPPDATA\AI-Assistant\face_data"
  RMDir "$LOCALAPPDATA\AI-Assistant"
!macroend

!macro customUnInit
  ; Custom uninstaller initialization code
!macroend 