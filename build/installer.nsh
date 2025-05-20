!macro customRemoveFiles
  ; Delete the face_data directory in AppData\Local\AI-Assistant
  RMDir /r "$LOCALAPPDATA\AI-Assistant\face_data"
!macroend 