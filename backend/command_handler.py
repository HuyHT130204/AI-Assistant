# backend/command_handler.py

import re
import webbrowser
from urllib.parse import quote
from backend.command import speak, takecommand
from backend.learning import CommandLearner
from backend.feature import openCommand, PlayYoutube, findContact, whatsApp, facebookMessage, facebookSearch, chatBot
import eel

class CommandHandler:
    def __init__(self):
        self.learner = CommandLearner()
        
    def handle_command(self, query):
        """Main function to handle all types of commands"""
        if not query:
            return False
            
        query = query.lower()
        print(f"Handling command: {query}")
        
        # First try with the command learner
        try:
            if self.learner.handle_command(query):
                return True
        except Exception as e:
            print(f"Error in command learner: {e}")
        
        # Then try with the predefined commands
        try:
            # Teaching commands
            if "teach" in query and "how to" in query:
                return self._handle_teaching(query)
                
            # System commands
            elif "open" in query:
                openCommand(query)
                return True
                
            # Communication commands
            elif "send message to" in query and "on facebook" in query:
                facebookMessage(query)
                return True
            elif "find" in query and "on facebook" in query:
                facebookSearch(query)
                return True
            elif "send message" in query or "phone call" in query or "video call" in query:
                return self._handle_contact_command(query)
                
            # Media commands
            elif "youtube" in query:
                PlayYoutube(query)
                return True
                
            # Information commands
            elif "what can you do" in query or "help" == query or "show commands" in query:
                return self._show_capabilities()
                
            # If no specific command matched, use chatbot
            else:
                chatBot(query)
                return True
                
        except Exception as e:
            print(f"Error processing command: {e}")
            speak("Sorry, I encountered an error processing your command")
            return False
            
    def _handle_teaching(self, query):
        """Handle teaching commands"""
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
        
        # Hiển thị dialog nhập URL thay vì sử dụng voice input
        eel.showURLTemplateInput(command_type, platform)
        return True
            
    def _handle_contact_command(self, query):
        """Handle contact-related commands"""
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
        return False
        
    def _show_capabilities(self):
        """Show what the assistant can do"""
        capabilities = [
            "I can open applications on your computer",
            "I can search for information on various platforms",
            "I can play music and videos on different services",
            "I can send messages and make calls to your contacts",
            "I can interact with Facebook to search and message",
            "I can play videos on YouTube",
            "I can learn new commands when you teach me"
        ]
        
        # Get supported platforms
        supported_platforms = self.learner.get_supported_platforms()
        
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