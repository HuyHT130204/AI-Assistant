import time
import pyttsx3
import speech_recognition as sr
import eel

@eel.expose
def speak(text):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    # print(voices)
    engine.setProperty('voice', voices[1].id)
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()
    engine.setProperty('rate', 174)

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("I'm listening...")
        eel.DisplayMessage("I'm listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, 10, 8)

    try:
        print("Recognizing...")
        eel.DisplayMessage("Recognizing...")
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}\n")   
        eel.DisplayMessage(query)     
        speak(query)
       
    except Exception as e:
        print(f"Error: {str(e)}\n")
        return None

    return query.lower()

@eel.expose
def takeAllCommand():
    try:
        query = takecommand()
        print(query)
        if "open" in query:
            from backend.feature import openCommand
            openCommand(query)
        elif "youtube" in query:
            from backend.feature import PlayYoutube
            PlayYoutube(query)
        else:
            print("I'm not sure what to do.")
    except:
        print("An error occurred.")
    eel.ShowHood()