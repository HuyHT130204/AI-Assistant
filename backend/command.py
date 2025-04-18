import os
import time
import pyttsx3
import speech_recognition as sr
import eel
import re
import webbrowser
import sys
from urllib.parse import quote

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
        eel.senderText(query)
       
    except Exception as e:
        print(f"Error: {str(e)}\n")
        return None

    return query.lower()

def process_command(query, learner=None):
    """Centralized command processing function to avoid code duplication"""
    if learner is None:
        from backend.learning import CommandLearner
        learner = CommandLearner()
    
    try:
        # Check for shutdown command first
        if query.strip() == "shutdown":
            print("Shutdown command detected in process_command")
            shutdown_app()
            return True
            
        # First try with the command learner
        if learner.handle_command(query):
            return True
            
        # Then try with the predefined commands
        if "open" in query:
            from backend.feature import openCommand
            openCommand(query)
            return True
        elif "send message to" in query and "on facebook" in query:
            from backend.feature import facebookMessage
            facebookMessage(query)
            return True
        elif "find" in query and "on facebook" in query:
            from backend.feature import facebookSearch
            facebookSearch(query)
            return True
        elif "send message" in query or "phone call" in query or "video call" in query:
            from backend.feature import findContact, whatsApp
            flag = ""
            Phone, name = findContact(query)
            if Phone != 0:
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
                return True
        elif "youtube" in query:
            from backend.feature import PlayYoutube
            PlayYoutube(query)
            return True
        # Handle teaching commands
        elif "teach" in query and "how to" in query:
            return handle_teaching(query, learner)
        elif "what can you do" in query or "help" == query or "show commands" in query:
            return show_capabilities(learner)
        else:
            from backend.feature import chatBot
            chatBot(query)
            return True
    except Exception as e:
        print(f"Error processing command: {e}")
        speak("Sorry, I encountered an error processing your command")
        return False

@eel.expose
def shutdown_app():
    """Function to shut down the application completely"""
    print("Executing shutdown_app function...")
    
    try:
        # Simplified message
        print("Attempting to close browser window...")
        
        # Just try DisplayMessage which seems to be working
        try:
            eel.DisplayMessage("Shutting down...")
        except Exception as e:
            print(f"Display error: {e}")
        
        # Try closeWindow
        try:
            eel.closeWindow()
        except Exception as e:
            print(f"closeWindow error: {e}")
            
        # Alternative method if the first fails
        try:
            eel._js_call('window.close')
        except Exception as e:
            print(f"window.close error: {e}")
            
    except Exception as e:
        print(f"General shutdown error: {e}")
    
    # Force kill the process after a short delay
    print("Forcing immediate termination...")
    time.sleep(1)
    
    # Use the most aggressive method - os._exit
    os._exit(0)  # This bypasses all cleanup and forces immediate exit

@eel.expose
def confirm_shutdown():
    """Function to confirm shutdown from JavaScript"""
    print("Shutdown confirmed from JavaScript")
    # Đảm bảo rằng chương trình sẽ kết thúc sau khi nhận được xác nhận
    import os, sys
    try:
        os._exit(0)  # Kết thúc ngay lập tức
    except:
        sys.exit(0)  # Phương pháp thay thế


def handle_teaching(query, learner=None):
    """
    Handle teaching commands where users teach the assistant new platforms
    Format: "teach you how to search/play on [platform]"
    """
    if learner is None:
        from backend.learning import CommandLearner
        learner = CommandLearner()
    
    query = query.lower()
    
    # Detect command type (search or play)
    command_type = None
    if "search" in query:
        command_type = "search"
    elif "play" in query:
        command_type = "play"
    else:
        speak("Please specify if you want to teach me how to search or play on a platform")
        return False
    
    # Extract platform name
    platform_match = re.search(r"how to (?:search|play) on (.+?)(?:\s|$)", query)
    if not platform_match:
        speak("I couldn't understand which platform you want to teach me about")
        return False
        
    platform = platform_match.group(1).strip()
    
    # Ask for URL template - but use text input instead of voice
    speak(f"Please enter the URL template for {command_type}ing on {platform}. Use {{query}} where the search term should go.")
    
    # Instead of using takecommand(), expose a JavaScript function to show text input
    eel.showURLTemplateInput(command_type, platform)
    
    # The actual URL template will be provided via a callback from JavaScript
    # We'll return True here and let the JavaScript handle the rest
    return True

def show_capabilities(learner=None):
    """Show what the assistant can do"""
    if learner is None:
        from backend.learning import CommandLearner
        learner = CommandLearner()
        
    capabilities = [
        "I can open applications on your computer",
        "I can search for information on various platforms",
        "I can play music and videos on different services",
        "I can send messages and make calls to your contacts",
        "I can interact with Facebook to search and message",
        "I can play videos on YouTube",
        "I can learn new commands when you teach me",
        "Say 'Shutdown' to close the assistant"
    ]
    
    # Get supported platforms
    supported_platforms = learner.get_supported_platforms()
    
    search_platforms = ", ".join(supported_platforms.get("search", []))
    play_platforms = ", ".join(supported_platforms.get("play", []))
    
    if search_platforms:
        capabilities.append(f"I can search on: {search_platforms}")
    if play_platforms:
        capabilities.append(f"I can play media on: {play_platforms}")
        
    capabilities.append("You can teach me new commands by saying 'teach you how to search/play on [platform]'")
    
    # Display capabilities
    speak("Here are some things I can do:")
    for capability in capabilities:
        print(f"- {capability}")
        
    speak("\n".join(capabilities))
    return True

@eel.expose
def receive_url_template(command_type, platform, url_template):
    """Receive URL template from JavaScript and add it to the learned commands"""
    from backend.learning import CommandLearner
    learner = CommandLearner()
    
    # Thêm xử lý đặc biệt cho URL không có {query}
    if url_template:
        # Nếu URL không có {query}, tự động thêm vào cuối
        if "{query}" not in url_template:
            if "?" in url_template:
                url_template += "&q={query}"
            else:
                url_template += "?q={query}"
                
        if learner.add_custom_platform(command_type, platform, url_template):
            speak(f"Great! I've learned how to {command_type} on {platform}. You can now ask me to {command_type} something on {platform}.")
            return True
        else:
            speak("Sorry, I couldn't learn this command. Please try again.")
            return False
    else:
        speak("I need a valid URL template. Let's try again later.")
        return False

@eel.expose
def cancel_teaching():
    """Cancel the teaching process"""
    speak("Teaching canceled.")
    return True

# Expose this function to JavaScript
@eel.expose
def takeAllCommand(message=None):
    print(f"takeAllCommand called with message: {message}")
    
    # Initialize the command learner
    from backend.learning import CommandLearner
    learner = CommandLearner()
    
    # Process text input
    if message is not None:
        query = message.lower()
        print(f"Processing text input: {query}")
        eel.DisplayMessage(query)
        eel.senderText(query)
        
        # Check for shutdown command in text input
        if query.strip() == "shutdown":
            print("Shutdown command received via text input")
            shutdown_app()
            return
        
        # Use centralized command processing
        process_command(query, learner)
        
        # Display main interface
        eel.ShowHood()
        return
    
    # If no text message, continue with voice recognition
    query = takecommand()
    if not query:
        eel.ShowHood()
        return
    
    print(f"Processing voice command: {query}")
    
    # Check for shutdown command from voice input
    if query.strip() == "shutdown":
        print("Shutdown command received via voice input")
        shutdown_app()
        return
    
    # Use centralized command processing
    process_command(query, learner)
    
    eel.ShowHood()
