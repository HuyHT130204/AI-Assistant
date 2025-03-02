import os
import eel
from backend.feature import *

eel.init("frontend")
os.system('start msedge.exe --app="http://127.0.0.1:8000/index.html"')

playAssistantSound()

eel.start("index.html", mode=None, host="localhost", block=True)
