import os
import re
from shlex import quote
import sqlite3
import struct
import subprocess
import time
import webbrowser
import eel
from hugchat import hugchat 
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
import pygame
import sys  # Thêm import sys
from backend.config import ASSISTANT_NAME
from backend.command import speak, shutdown_app
from backend.helper import extract_yt_term, remove_words, extract_fb_term

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

# Initialize pygame mixer
pygame.mixer.init()

# Define the function to play sound
@eel.expose
def play_assistant_sound():
    sound_file = r"C:\Users\huyht\JARVIS\frontend\assets\audio\start_sound.mp3"
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

def openCommand(query):
    query = query.replace(ASSISTANT_NAME,"")
    query = query.replace("open","")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute( 
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)

def hotword():
    porcupine = None
    paud = None
    audio_stream = None
    try:
        # Path to your custom "Shutdown" PPN file
        shutdown_ppn_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'Shutdown_en_windows_v3_0_0.ppn')
        
        # Debug output for file path
        print(f"Looking for Shutdown PPF file at: {shutdown_ppn_path}")
        print(f"File exists: {os.path.exists(shutdown_ppn_path)}")
        
        if not os.path.exists(shutdown_ppn_path):
            print("Error: Shutdown PPF file not found! Cannot continue.")
            return
        
        # Only use the custom shutdown keyword
        keyword_names = ["shutdown"]
        
        # Create Porcupine instance with ONLY the custom shutdown keyword
        porcupine = pvporcupine.create(
            access_key="8j1GOv8pGZ91czRvzKOcGdBHr3Em72a0PutpNdiJw3aTF/8vLFmSEA==",
            keywords=[],  # Empty list for standard keywords
            keyword_paths=[shutdown_ppn_path]  # Only use custom shutdown keyword
        )
        
        print(f"Porcupine initialized with keywords: {keyword_names}")
        
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        
        print("Hotword detection started. Listening for shutdown keyword...")
        
        # Loop for streaming
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)

            # Processing keyword comes from mic 
            keyword_index = porcupine.process(keyword)

            # In the hotword function in paste-3.txt, modify the shutdown code:
            if keyword_index >= 0:
                print(f"Shutdown hotword detected! (index {keyword_index})")
                print("Shutdown command confirmed! Exiting application...")
                
                # Clean up resources before shutdown
                if audio_stream is not None:
                    audio_stream.close()
                if paud is not None:
                    paud.terminate()
                if porcupine is not None:
                    porcupine.delete()
                
                # Speak goodbye message directly without using eel functions
                try:
                    import pyttsx3
                    engine = pyttsx3.init('sapi5')
                    engine.say("See you soon Boss")
                    engine.runAndWait()
                except:
                    pass
                
                # Try calling closeWindow through eel
                try:
                    eel.closeWindow()
                except:
                    pass
                
                # Force immediate exit
                time.sleep(1)
                os._exit(0)  # Most aggressive exit method
                
    except Exception as e:
        print(f"Error in hotword detection: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # This should only run if the main loop exits without shutdown being triggered
        print("Cleaning up hotword detection resources...")
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()

def findContact(query):
    # Cải thiện danh sách từ cần loại bỏ để tìm tên chính xác hơn
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video',
                      'call to', 'send message to']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        print(f"Looking for contact: '{query}'")
        
        # Tìm kiếm chính xác trước
        cursor.execute("SELECT Phone, name FROM contacts WHERE LOWER(name) = ?", (query,))
        results = cursor.fetchall()
        
        # Nếu không tìm thấy, thử tìm kiếm tương đối
        if not results:
            cursor.execute("SELECT Phone, name FROM contacts WHERE LOWER(name) LIKE ?", ('%' + query + '%',))
            results = cursor.fetchall()
            
            # Nếu vẫn không tìm thấy, thử tìm kiếm từng phần của tên
            if not results:
                words = query.split()
                for word in words:
                    if len(word) > 2:  # Chỉ tìm kiếm với các từ có độ dài hợp lý
                        cursor.execute("SELECT Phone, name FROM contacts WHERE LOWER(name) LIKE ?", ('%' + word + '%',))
                        results = cursor.fetchall()
                        if results:
                            break
                            
        if results:
            mobile_number_str = str(results[0][0])
            actual_name = results[0][1]  # Lấy tên thực tế được lưu trữ
            print(f"Found contact: {actual_name} with number: {mobile_number_str}")

            if not mobile_number_str.startswith('+84'):
                mobile_number_str = '+84' + mobile_number_str

            return mobile_number_str, actual_name
        else:
            speak('Contact not found in your contacts')
            return 0, 0
    except Exception as e:
        print(f"Error finding contact: {e}")
        speak('Error occurred while searching contacts')
        return 0, 0
    
def whatsApp(Phone, message, flag, name):
    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name

    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)

def facebookSearch(query):
    search_term = extract_fb_term(query, "find")
    if search_term:
        speak(f"Searching for {search_term} on Facebook")
        # Construct Facebook search URL
        search_url = f"https://www.facebook.com/search/top?q={quote(search_term)}"
        webbrowser.open(search_url)
    else:
        speak("I couldn't understand who to search for on Facebook")

def facebookMessage(query):
    contact_name = extract_fb_term(query, "message")
    if contact_name:
        speak(f"Opening Facebook Messenger to message {contact_name}")
        
        # First open Facebook Messenger
        webbrowser.open("https://www.facebook.com/messages")
        time.sleep(7)  # Wait for page to load
        
        try:
            # Focus on the browser window
            screen_width, screen_height = pyautogui.size()
            pyautogui.click(screen_width//2, screen_height//2)
            time.sleep(1)
            
            # Look for the "Tìm kiếm trên Messenger" search box
            # Instead of using fixed coordinates, try to tab to the search field
            # or use the shortcut to focus on search
            
            # Option 1: Use the search box in the left sidebar
            # From your screenshot, I can see this field with "Tìm kiếm trên Messenger" text
            search_area_x = 150  # Approximate x coordinate of search area
            search_area_y = 250  # Updated y coordinate based on your screenshot
            
            pyautogui.click(search_area_x, search_area_y)
            time.sleep(1)
            
            # Clear any existing text and type contact name
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('delete')
            time.sleep(0.5)
            pyautogui.write(contact_name)
            time.sleep(2)
            
            # Navigate to SECOND result instead of first
            pyautogui.press('down')  # First down press
            time.sleep(0.5)
            pyautogui.press('down')  # Second down press to get to the second option
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)
            
            # Ask for message content
            speak("What message would you like to send?")
            # Import takecommand for the Facebook message function
            from backend.command import takecommand
            message_to_send = takecommand()
            
            if message_to_send:
                pyautogui.write(message_to_send)
                time.sleep(1)
                pyautogui.press('enter')
                speak(f"Message sent to {contact_name}")
            else:
                speak("No message was provided")
        except Exception as e:
            print(f"Error in Facebook messaging: {e}")
            speak("I encountered an error while trying to send a Facebook message")
    else:
        speak("I couldn't understand who to message on Facebook")

def chatBot(query):
    try:
        user_input = query.lower()
        print(f"Processing chat query: {user_input}")
        
        # Đường dẫn đúng đến cookie.json (sửa lỗi dấu gạch chéo)
        cookie_path = os.path.join(os.path.dirname(__file__), "cookie.json")
        print(f"Using cookie path: {cookie_path}")
        
        # Kiểm tra tồn tại của file cookie
        if not os.path.exists(cookie_path):
            print("Cookie file not found! Using fallback response.")
            response = "Tôi không thể kết nối với dịch vụ chat lúc này. Vui lòng thử lại sau."
        else:
            try:
                chatbot = hugchat.ChatBot(cookie_path=cookie_path)
                id = chatbot.new_conversation()
                chatbot.change_conversation(id)
                response = chatbot.chat(user_input)
            except Exception as e:
                print(f"HugChat error: {e}")
                response = "Xin lỗi, tôi đang gặp sự cố khi xử lý câu hỏi của bạn. Hãy thử lại sau."
        
        print(f"ChatBot response: {response}")
        speak(response)
        return True  # Trả về True để command_handler biết đã xử lý thành công
    except Exception as e:
        print(f"Error in chatBot function: {str(e)}")
        speak("Xin lỗi, tôi không thể trả lời câu hỏi của bạn lúc này.")
        return False  # Trả về False để biết có lỗi xảy ra

