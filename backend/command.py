import time
import pyttsx3
import speech_recognition as sr
import eel
import re

@eel.expose
def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    
    # Fix: Check the number of available voices before setting
    voice_index = 0  # Default to the first voice
    if len(voices) > 1:
        voice_index = 1  # Use second voice if available
    
    engine.setProperty('voice', voices[voice_index].id)
    engine.setProperty('rate', 174)  # Set rate before speaking
    eel.receiverText(text)
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()

def normalize_vietnamese_names(text):
    """
    Chuẩn hóa các tên tiếng Việt thường bị nhận diện sai
    """
    # Thêm các tên tiếng Việt thường bị nhận diện sai vào đây
    replacements = {
        "chau ngan": "Châu Ngân",
        "show ngan": "Châu Ngân",
        "chow ngan": "Châu Ngân",
        # Thêm các tên khác vào đây
    }
    
    # Kiểm tra và thay thế
    lower_text = text.lower()
    for incorrect, correct in replacements.items():
        if incorrect in lower_text:
            pattern = re.compile(re.escape(incorrect), re.IGNORECASE)
            return pattern.sub(correct, text)
    return text

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
        
        # Thử nhận diện với tiếng Anh trước
        try:
            query = r.recognize_google(audio, language='en-US')
            print(f"Recognized with en-US: {query}")
            
            # Kiểm tra xem có cần phải nhận diện lại với tiếng Việt không
            if "call to" in query.lower() or "send message" in query.lower() or "play" in query.lower():
                # Thử nhận diện lại với tiếng Việt
                try:
                    vn_query = r.recognize_google(audio, language='vi-VN')
                    print(f"Also recognized with vi-VN: {vn_query}")
                    
                    # Trích xuất phần tên tiếng Việt từ câu tiếng Việt
                    if "call to" in query.lower():
                        en_parts = query.lower().split("call to ")
                        vn_parts = vn_query.lower().split("call to ")
                        if len(en_parts) > 1 and len(vn_parts) > 1:
                            # Thay thế phần tên trong câu tiếng Anh bằng tên từ câu tiếng Việt
                            query = en_parts[0] + "call to " + vn_parts[1]
                    elif "send message" in query.lower():
                        en_parts = query.lower().split("send message to ")
                        vn_parts = vn_query.lower().split("send message to ")
                        if len(en_parts) > 1 and len(vn_parts) > 1:
                            query = en_parts[0] + "send message to " + vn_parts[1]
                    elif "play" in query.lower() and "youtube" in query.lower():
                        en_parts = query.lower().split("play ")
                        if len(en_parts) > 1:
                            vn_parts = vn_query.lower().split("play ")
                            if len(vn_parts) > 1:
                                parts_on = en_parts[1].split(" on ")
                                vn_parts_on = vn_parts[1].split(" on ")
                                if len(parts_on) > 1 and len(vn_parts_on) > 1:
                                    query = en_parts[0] + "play " + vn_parts_on[0] + " on " + parts_on[1]
                except:
                    # Nếu không thể nhận diện tiếng Việt, giữ nguyên kết quả tiếng Anh
                    pass
        except:
            # Nếu tiếng Anh thất bại, thử tiếng Việt
            query = r.recognize_google(audio, language='vi-VN')
            print(f"Recognized with vi-VN: {query}")
        
        # Chuẩn hóa các tên tiếng Việt
        query = normalize_vietnamese_names(query)
        
        print(f"Final user query: {query}\n")   
        eel.DisplayMessage(query)     
        speak(query)
       
    except Exception as e:
        print(f"Error: {str(e)}\n")
        return None

    return query.lower()

# Expose this function to JavaScript
@eel.expose
def takeAllCommand(message=None):
    print(f"takeAllCommand called with message: {message}")
    
    # Xử lý message từ văn bản nhập vào
    if message is not None:
        query = message.lower()  # Nếu có message, sử dụng nó
        print(f"Processing text input: {query}")
        eel.DisplayMessage(query)  # Hiển thị tin nhắn của người dùng
        eel.senderText(query)  # Gửi tin nhắn đến giao diện
        
        # Xử lý các lệnh dựa trên tin nhắn văn bản
        try:
            if query:
                if "open" in query:
                    from backend.feature import openCommand
                    openCommand(query)
                elif "send message to" in query and "on facebook" in query:
                    from backend.feature import facebookMessage
                    facebookMessage(query)
                elif "find" in query and "on facebook" in query:
                    from backend.feature import facebookSearch
                    facebookSearch(query)
                elif "send message" in query or "phone call" in query or "video call" in query:
                    print("Processing contact command")
                    from backend.feature import findContact, whatsApp
                    flag = ""
                    Phone, name = findContact(query)
                    if(Phone != 0):
                        if "send message" in query:
                            flag = 'message'
                            speak("what message to send?")
                            message_to_send = takecommand()  # Lấy tin nhắn bằng giọng nói
                            if message_to_send is None:
                                message_to_send = ""
                            query = message_to_send
                        elif "phone call" in query:
                            flag = 'call'
                        else:
                            flag = 'video call'
                        whatsApp(Phone, query, flag, name)
                elif "youtube" in query:
                    from backend.feature import PlayYoutube
                    PlayYoutube(query)
                else:
                    from backend.feature import chatBot
                    chatBot(query)
            else:
                speak("No command was given.")
        except Exception as e:
            print(f"Error processing text command: {e}")
            speak("Sorry, I encountered an error processing your command")
        
        # Hiển thị lại giao diện chính
        eel.ShowHood()
        return
    
    # Nếu không có tin nhắn văn bản, tiếp tục với nhận diện giọng nói
    query = takecommand()
    if not query:
        eel.ShowHood()  # Hiển thị lại giao diện nếu không nhận được lệnh
        return
    
    print(f"Processing voice command: {query}")
    eel.senderText(query)  # Gửi tin nhắn đến giao diện
    
    try:
        if "open" in query:
            from backend.feature import openCommand
            openCommand(query)
        elif "send message to" in query and "on facebook" in query:
            from backend.feature import facebookMessage
            facebookMessage(query)
        elif "find" in query and "on facebook" in query:
            from backend.feature import facebookSearch
            facebookSearch(query)
        elif "send message" in query or "phone call" in query or "video call" in query:
            print("Processing contact command")
            from backend.feature import findContact, whatsApp
            flag = ""
            Phone, name = findContact(query)
            if(Phone != 0):
                if "send message" in query:
                    flag = 'message'
                    speak("what message to send?")
                    message_to_send = takecommand()
                    if message_to_send is None:
                        message_to_send = ""
                    query = message_to_send
                elif "phone call" in query:
                    flag = 'call'
                else:
                    flag = 'video call'
                whatsApp(Phone, query, flag, name)
        elif "youtube" in query:
            from backend.feature import PlayYoutube
            PlayYoutube(query)
        else:
            speak("I heard you say: " + query)
            print("Command not recognized")
    except Exception as e:
        print(f"Error processing voice command: {e}")
        speak("Sorry, I encountered an error processing your command")
    
    eel.ShowHood()  # Hiển thị lại giao diện chính|