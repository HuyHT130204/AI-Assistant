import os
import time
import pyttsx3
import speech_recognition as sr
import eel
import re
import webbrowser
import sys
from urllib.parse import quote
from backend.settings import Settings

# Biến toàn cục lưu engine pyttsx3 hiện tại
current_tts_engine = None

@eel.expose
def stop_speaking():
    global current_tts_engine
    try:
        if current_tts_engine is not None:
            current_tts_engine.stop()
            current_tts_engine = None
    except Exception as e:
        print(f"Error stopping TTS: {e}")
    return True

@eel.expose
def speak(text):
    try:
        text = str(text)
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        
        # Lấy cài đặt từ database
        settings = Settings()
        volume = settings.get_setting("voice", "volume", 100)
        voice_type = settings.get_setting("voice", "type", "male")
        
        # Set voice type
        voice_index = 0 if voice_type == "male" else 1
        if len(voices) > voice_index:
            engine.setProperty('voice', voices[voice_index].id)
        
        # Set volume (0-100)
        engine.setProperty('volume', volume / 100)
        engine.setProperty('rate', 174)
        
        eel.DisplayMessage(text)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speak function: {e}")
        # Fallback to basic speech if settings fail
        try:
            engine = pyttsx3.init('sapi5')
            engine.setProperty('rate', 174)
            eel.DisplayMessage(text)
            engine.say(text)
            engine.runAndWait()
        except Exception as e2:
            print(f"Fallback speech also failed: {e2}")

@eel.expose
def shutdown_app():
    """Function to shut down the application completely"""
    print("Executing shutdown_app function...")
    
    try:
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
    
    # Dừng toàn bộ process ngay lập tức
    finally:
        os._exit(0)

@eel.expose
def confirm_shutdown():
    """Function to confirm shutdown from JavaScript"""
    print("Shutdown confirmed from JavaScript")
    try:
        os._exit(0)
    except:
        sys.exit(0)

@eel.expose
def closeWindow():
    print("Executing closeWindow function...")
    try:
        print("Attempting to close browser window...")
        try:
            eel.DisplayMessage("Shutting down...")
        except Exception as e:
            print(f"Display error: {e}")
        try:
            eel.closeWindow()
        except Exception as e:
            print(f"closeWindow error: {e}")
        try:
            eel._js_call('window.close')
        except Exception as e:
            print(f"window.close error: {e}")
    except Exception as e:
        print(f"General shutdown error: {e}")
    finally:
        os._exit(0)

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

def process_command(query, command_handler=None):
    """Centralized command processing function to avoid code duplication"""
    if command_handler is None:
        from backend.command_handler import CommandHandler
        command_handler = CommandHandler()
    
    try:
        # Check for shutdown command first
        if query.strip() == "shutdown":
            print("Shutdown command detected in process_command")
            shutdown_app()
            return True
            
        # Sử dụng CommandHandler để xử lý tất cả các lệnh
        return command_handler.handle_command(query)
        
    except Exception as e:
        print(f"Error processing command: {e}")
        speak("Sorry, I encountered an error processing your command")
        return False

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

@eel.expose
def takeAllCommand(message=None):
    print(f"takeAllCommand called with message: {message}")
    
    # Initialize the command handler
    from backend.command_handler import CommandHandler
    command_handler = CommandHandler()
    
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
        
        # Use improved command processing
        process_command(query, command_handler)
        
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
    
    # Use improved command processing
    process_command(query, command_handler)
    
    eel.ShowHood()
