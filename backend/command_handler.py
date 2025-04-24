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
        # Command type patterns with keywords
        self.command_types = {
            "open": ["open", "launch", "start", "run"],
            "search": ["search", "find", "look for", "lookup"],
            "play": ["play", "watch", "listen to"],
            "communication": ["send message", "call", "phone call", "video call"],
            "system": ["shutdown", "restart", "update", "install", "backup", "restore"],
            "info": ["show", "list", "display", "give me", "tell me about"],
            "teaching": ["teach you", "learn how to"],
            "help": ["what can you do", "help", "show commands", "show features"]
        }
        
        # Common question patterns
        self.question_patterns = [
            r"^(what|who|when|where|why|how)\s.+\?$",
            r"^(is|are|was|were|do|does|did|can|could|would|should|will|have|has|had)\s.+\?$",
            r"^(what|who|when|where|why|how)\s.+",
            r"^can you tell me\s.+",
            r"^tell me\s.+",
            r"^do you know\s.+",
        ]
        
        # Load specific command database patterns
        self.load_command_patterns()
        
    def load_command_patterns(self):
        """Load common command patterns from database"""
        self.db_commands = {}
        try:
            # Try to get common commands from database for quick matching
            import sqlite3
            conn = sqlite3.connect("jarvis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT command_text, function_name FROM command_dataset")
            for cmd_text, func_name in cursor.fetchall():
                self.db_commands[cmd_text.lower()] = func_name
            conn.close()
        except Exception as e:
            print(f"Error loading command patterns: {e}")
            self.db_commands = {}
        
    def handle_command(self, query):
        """Main entry point for handling all user input"""
        if not query:
            return False
            
        query = query.lower().strip()
        print(f"Handling input: {query}")
        
        # First check if it's an exact match with a database command
        if query in self.db_commands:
            print(f"Exact command match found in database: {self.db_commands[query]}")
            return self.learner.handle_dataset_command(query)
        
        # Check for exact command patterns
        if self._is_direct_command(query):
            return self._process_command(query)
        
        # Classify the input more thoroughly
        input_type = self._classify_input(query)
        print(f"Input classified as: {input_type}")
        
        # Process based on classification
        if input_type == "question":
            chatBot(query)
            return True
        else:
            return self._process_command(query)
    
    def _is_direct_command(self, query):
        """Check if the query is directly matching a command pattern"""
        # Check for system commands
        if query == "shutdown":
            return True
            
        # Check command prefixes
        for cmd_type, keywords in self.command_types.items():
            for keyword in keywords:
                if query.startswith(f"{keyword} "):
                    return True
                    
        # Check platform-specific commands
        platform_indicators = [
            "on google", "on youtube", "on facebook", "on spotify", 
            "on instagram", "on twitter", "open", "play", "search for"
        ]
        
        for indicator in platform_indicators:
            if indicator in query:
                return True
                
        return False
    
    def _classify_input(self, query):
        """More robust classification of input as command or question"""
        # Strip punctuation for better matching
        clean_query = re.sub(r'[^\w\s]', '', query).strip()
        
        # 1. Check for exact command matches in database first
        for cmd in self.db_commands:
            if clean_query in cmd or cmd in clean_query:
                return "command"
        
        # 2. Check for command indicators by keyword
        for cmd_type, keywords in self.command_types.items():
            for keyword in keywords:
                # Full phrase match (e.g., "open chrome")
                if f"{keyword} " in query:
                    return "command"
                    
        # 3. Check for platform-specific commands
        platform_commands = [
            "on google", "on youtube", "on facebook", "on spotify", 
            "to facebook", "to whatsapp", "on instagram"
        ]
        
        for platform in platform_commands:
            if platform in query:
                return "command"
                
        # 4. Check for question patterns
        for pattern in self.question_patterns:
            if re.search(pattern, query):
                return "question"
                
        # 5. Check for question marks
        if query.endswith("?"):
            return "question"
            
        # 6. Check for Vietnamese-specific commands
        vn_command_indicators = ["mở", "phát", "tìm", "gọi", "nhắn tin", "tin nhắn"]
        if any(indicator in query for indicator in vn_command_indicators):
            return "command"
        
        # 7. Check for information/help requests
        help_indicators = ["what can you do", "help me", "list commands", "show features"]
        if any(indicator in query for indicator in help_indicators):
            return "command"
        
        # Default handling for ambiguous inputs
        # If it has command-like structure but no question pattern, treat as command
        if any(keyword in query for keyword in ["open", "play", "search", "find", "send", "call"]):
            return "command"
        
        # Default to treating as a question for conversational handling
        return "question"
            
    def _process_command(self, query):
        """Process identified commands with priority order"""
        try:
            # 1. First try to handle with dataset commands
            if self.learner.handle_dataset_command(query):
                return True
                
            # 2. Then try with learned commands
            if self.learner.handle_command(query):
                return True
                
            # 3. Try with built-in command handlers
            
            # Teaching commands
            if "teach" in query and "how to" in query:
                return self._handle_teaching(query)
                
            # System commands
            elif any(cmd in query for cmd in ["open", "launch", "start", "run"]):
                openCommand(query)
                return True
                
            # Communication commands
            elif "send message to" in query and "on facebook" in query:
                facebookMessage(query)
                return True
            elif "find" in query and "on facebook" in query:
                facebookSearch(query)
                return True
            elif any(cmd in query for cmd in ["send message", "phone call", "video call"]):
                return self._handle_contact_command(query)
                
            # Media commands
            elif "youtube" in query:
                PlayYoutube(query)
                return True
                
            # Help commands
            elif any(cmd in query for cmd in ["what can you do", "help", "show commands"]):
                return self._show_capabilities()
                
            # If no command handler matched but it was classified as a command
            speak("I don't understand that command. Say 'help' to see what I can do.")
            return False
                
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
            "I can learn new commands when you teach me",
            "I can answer your questions about various topics"
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
    