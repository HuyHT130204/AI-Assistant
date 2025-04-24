import re
import sqlite3
import time
import webbrowser
from urllib.parse import quote
import os
import subprocess

from backend.command_tasks import (
    TaskManager,
    SystemTasks,
    FileTasks,
    WebTasks,
    MediaTasks,
    NetworkTasks
)

class CommandLearner:
    def __init__(self, db_path="jarvis.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._ensure_tables_exist()
        self.load_patterns()
        
        # Initialize task managers
        self.task_manager = TaskManager()
        self.system_tasks = SystemTasks()
        self.file_tasks = FileTasks()
        self.web_tasks = WebTasks()
        self.media_tasks = MediaTasks()
        self.network_tasks = NetworkTasks()
        
    def _ensure_tables_exist(self):
        """Ensure all necessary tables exist in the database"""
        # Create learned_commands table if it doesn't exist
        query = """
        CREATE TABLE IF NOT EXISTS learned_commands(
            id INTEGER PRIMARY KEY,
            command_type VARCHAR(50),
            pattern VARCHAR(200),
            platform VARCHAR(100),
            url_template VARCHAR(500),
            count INTEGER DEFAULT 1,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(query)

        # Table for command dataset
        query = """
        CREATE TABLE IF NOT EXISTS command_dataset(
            id INTEGER PRIMARY KEY,
            task_intent VARCHAR(100),
            command_text VARCHAR(500),
            function_name VARCHAR(100),
            parameters TEXT,
            count INTEGER DEFAULT 1,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def import_command_dataset(self, csv_path):
        """Import commands from CSV file"""
        import csv
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                counter = 0
                
                for row in reader:
                    # Check if the row has the expected columns
                    if 'Task/Intent' in row and 'command' in row:
                        task = row['Task/Intent']
                        command = row['command']
                        
                        # Create function name from task
                        function_name = task.lower().replace(' ', '_').replace('/', '_')
                        
                        # Check if the command already exists
                        self.cursor.execute(
                            "SELECT id FROM command_dataset WHERE command_text = ?",
                            (command,)
                        )
                        if not self.cursor.fetchone():
                            # Insert new command
                            self.cursor.execute(
                                "INSERT INTO command_dataset (task_intent, command_text, function_name) VALUES (?, ?, ?)",
                                (task, command, function_name)
                            )
                            counter += 1
                
                self.conn.commit()
                return counter
        except Exception as e:
            print(f"Error importing dataset: {e}")
            return 0

    def handle_dataset_command(self, query):
        """Process commands from the imported dataset"""
        query = query.lower()
        
        # Try exact match first
        self.cursor.execute(
            "SELECT task_intent, function_name, parameters FROM command_dataset WHERE LOWER(command_text) = ?",
            (query,)
        )
        result = self.cursor.fetchone()
        
        if not result:
            # Try partial match
            self.cursor.execute(
                """
                SELECT task_intent, function_name, parameters FROM command_dataset 
                WHERE LOWER(command_text) LIKE ? 
                ORDER BY LENGTH(command_text) ASC LIMIT 1
                """,
                (f"%{query}%",)
            )
            result = self.cursor.fetchone()
            
            if not result:
                # Try matching keywords
                keywords = query.split()
                for keyword in keywords:
                    if len(keyword) > 3:  # Only consider words longer than 3 characters
                        self.cursor.execute(
                            """
                            SELECT task_intent, function_name, parameters FROM command_dataset 
                            WHERE LOWER(command_text) LIKE ? 
                            ORDER BY LENGTH(command_text) ASC LIMIT 1
                            """,
                            (f"%{keyword}%",)
                        )
                        result = self.cursor.fetchone()
                        if result:
                            break
        
        if result:
            task_intent, function_name, parameters = result
            
            # Update usage count
            self.cursor.execute(
                "UPDATE command_dataset SET count = count + 1, last_used = CURRENT_TIMESTAMP WHERE function_name = ?",
                (function_name,)
            )
            self.conn.commit()
            
            # Process based on task intent
            return self._execute_task_intent(task_intent, query, parameters)
        
        return False

    def _execute_task_intent(self, task_intent, query, parameters=None):
        """Execute different tasks based on intent"""
        task_intent_lower = task_intent.lower()

        # 1. Opening/Closing Apps
        if "open" in task_intent_lower or "launch" in task_intent_lower or "start" in task_intent_lower:
            return self.system_tasks.open_application(query)
            
        elif "close" in task_intent_lower or "exit" in task_intent_lower or "quit" in task_intent_lower:
            return self.system_tasks.close_application(query)
            
        # 2. System Settings
        elif "system" in task_intent_lower and "settings" in task_intent_lower:
            return self.system_tasks.open_system_settings(query)
            
        # 3. File Management
        elif "file" in task_intent_lower and ("management" in task_intent_lower or "browser" in task_intent_lower or "explorer" in task_intent_lower):
            return self.file_tasks.file_management(query)
            
        # 4. File Search
        elif "file" in task_intent_lower and "search" in task_intent_lower:
            return self.file_tasks.file_search(query)
            
        # 5. Web Browsing
        elif "web" in task_intent_lower or "browsing" in task_intent_lower or "browser" in task_intent_lower:
            return self.web_tasks.web_browsing(query)
            
        # 6. Media Control
        elif "media" in task_intent_lower or "play" in task_intent_lower or "music" in task_intent_lower or "song" in task_intent_lower:
            return self.media_tasks.media_control(query)
            
        # 7. System Shutdown/Restart
        elif ("system" in task_intent_lower and ("shutdown" in task_intent_lower or "restart" in task_intent_lower)) or "shutdown" in task_intent_lower or "restart" in task_intent_lower:
            return self.system_tasks.system_power_management(query)
            
        # 8. System Information
        elif "system" in task_intent_lower and "information" in task_intent_lower:
            return self.system_tasks.system_information(query)
            
        # 9. Battery Management
        elif "battery" in task_intent_lower:
            return self.system_tasks.battery_management(query)
            
        # 10. Task Management
        elif "task" in task_intent_lower or "process" in task_intent_lower:
            return self.system_tasks.task_management(query)
            
        # 11. Network Management
        elif "network" in task_intent_lower or "internet" in task_intent_lower or "wifi" in task_intent_lower:
            return self.network_tasks.network_management(query)
            
        # 12. Software Installation
        elif "software" in task_intent_lower or "install" in task_intent_lower or "package" in task_intent_lower:
            return self.system_tasks.software_installation(query)
            
        # 13. System Updates
        elif "update" in task_intent_lower or "upgrade" in task_intent_lower:
            return self.system_tasks.system_updates(query)
            
        # 14. File Backup
        elif "backup" in task_intent_lower:
            return self.file_tasks.file_backup(query)
            
        # 15. System Troubleshooting
        elif "troubleshoot" in task_intent_lower or "diagnose" in task_intent_lower:
            return self.system_tasks.system_troubleshooting(query)
            
        # 16. System Monitoring
        elif "monitor" in task_intent_lower:
            return self.system_tasks.system_monitoring(query)
            
        # 17. File Compression
        elif "compress" in task_intent_lower or "zip" in task_intent_lower:
            return self.file_tasks.file_compression(query)
            
        # 18. Cloud Storage
        elif "cloud" in task_intent_lower:
            return self.file_tasks.cloud_storage(query)
            
        # 19. Device Management
        elif "device" in task_intent_lower:
            return self.system_tasks.device_management(query)
            
        # 20. Printer Management
        elif "printer" in task_intent_lower:
            return self.system_tasks.printer_management(query)
            
        # 21. Keyboard Shortcuts
        elif "keyboard" in task_intent_lower and "shortcuts" in task_intent_lower:
            return self.system_tasks.keyboard_shortcuts(query)
            
        # 22. Clipboard Management
        elif "clipboard" in task_intent_lower:
            return self.system_tasks.clipboard_management(query)
            
        # 23. Screen Capture
        elif "screen" in task_intent_lower and ("capture" in task_intent_lower or "screenshot" in task_intent_lower):
            return self.system_tasks.screen_capture(query)
            
        # 24. System Time
        elif "time" in task_intent_lower:
            return self.system_tasks.system_time(query)
            
        # 25. Taskbar Management
        elif "taskbar" in task_intent_lower:
            return self.system_tasks.taskbar_management(query)
            
        # 26. File Permissions
        elif "permission" in task_intent_lower:
            return self.file_tasks.file_permissions(query)
            
        # 27. Creating/Editing Files
        elif "creat" in task_intent_lower or "edit" in task_intent_lower:
            return self.file_tasks.create_edit_files(query)
            
        # 28. Command Line Operations
        elif "command" in task_intent_lower and "line" in task_intent_lower:
            return self.system_tasks.command_line_operations(query)
            
        # 29. File Browsing
        elif "browsing" in task_intent_lower and "file" in task_intent_lower:
            return self.file_tasks.file_browsing(query)

        # 30. Internet Connectivity
        elif "internet" in task_intent_lower and "connectivity" in task_intent_lower:
            return self.network_tasks.check_internet_connectivity(query)

        # 31. Network Troubleshooting
        elif "network" in task_intent_lower and "troubleshooting" in task_intent_lower:
            return self.network_tasks.network_troubleshooting(query)

        return False

    def load_patterns(self):
        """Load existing command patterns from the database"""
        self.search_patterns = {}
        self.play_patterns = {}
        
        # Load search patterns
        self.cursor.execute("SELECT pattern, platform, url_template FROM learned_commands WHERE command_type = 'search'")
        for pattern, platform, url_template in self.cursor.fetchall():
            self.search_patterns[pattern] = (platform, url_template)
            
        # Load play patterns
        self.cursor.execute("SELECT pattern, platform, url_template FROM learned_commands WHERE command_type = 'play'")
        for pattern, platform, url_template in self.cursor.fetchall():
            self.play_patterns[pattern] = (platform, url_template)
            
    def detect_command_type(self, query):
        """Detect the type of command from the query"""
        query = query.lower()
        
        # Check for search commands
        search_keywords = ["search", "find", "look for", "look up"]
        for keyword in search_keywords:
            if keyword in query:
                return "search"
                
        # Check for play commands
        play_keywords = ["play", "listen to", "watch"]
        for keyword in play_keywords:
            if keyword in query:
                return "play"
                
        return None
        
    def extract_platform(self, query):
        """Extract the platform from the query"""
        query = query.lower()
        
        # Common platforms
        platforms = [
            "google", "youtube", "facebook", "instagram", "twitter", "tiktok",
            "spotify", "apple music", "nhaccuatui", "zing mp3", "soundcloud",
            "linkedin", "github", "amazon", "netflix", "pinterest"
        ]
        
        # Check for "on [platform]" pattern
        for platform in platforms:
            if f"on {platform}" in query:
                return platform
                
        return None
        
    def learn_search_command(self, query, platform=None):
        """Learn a new search command pattern"""
        if not platform:
            platform = self.extract_platform(query)
            if not platform:
                from backend.command import speak
                speak("I couldn't identify which platform you want to search on")
                return False
                
        # Extract the search term
        search_term = None
        search_patterns = [
            rf"search\s+(.*?)\s+on\s+{platform}",
            rf"find\s+(.*?)\s+on\s+{platform}",
            rf"look\s+for\s+(.*?)\s+on\s+{platform}",
            rf"look\s+up\s+(.*?)\s+on\s+{platform}"
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                search_term = match.group(1)
                break
                
        if not search_term:
            from backend.command import speak
            speak(f"I couldn't understand what to search for on {platform}")
            return False
            
        # Create URL template based on platform
        url_template = self._get_search_url_template(platform)
        if not url_template:
            from backend.command import speak
            speak(f"I don't know how to search on {platform} yet. Please teach me.")
            return False
            
        # Save the pattern to the database
        pattern = f"search (.*) on {platform}"
        self._save_command_pattern("search", pattern, platform, url_template)
        
        # Add to in-memory patterns
        self.search_patterns[pattern] = (platform, url_template)
        
        # Execute the search
        self._execute_search(search_term, platform, url_template)
        return True
        
    def learn_play_command(self, query, platform=None):
        """Learn a new play command pattern"""
        if not platform:
            platform = self.extract_platform(query)
            if not platform:
                from backend.command import speak
                speak("I couldn't identify which platform you want to play on")
                return False
                
        # Extract the play term
        play_term = None
        play_patterns = [
            rf"play\s+(.*?)\s+on\s+{platform}",
            rf"listen\s+to\s+(.*?)\s+on\s+{platform}",
            rf"watch\s+(.*?)\s+on\s+{platform}"
        ]
        
        for pattern in play_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                play_term = match.group(1)
                break
                
        if not play_term:
            from backend.command import speak
            speak(f"I couldn't understand what to play on {platform}")
            return False
            
        # Create URL template based on platform
        url_template = self._get_play_url_template(platform)
        if not url_template:
            from backend.command import speak
            speak(f"I don't know how to play content on {platform} yet. Please teach me.")
            return False
            
        # Save the pattern to the database
        pattern = f"play (.*) on {platform}"
        self._save_command_pattern("play", pattern, platform, url_template)
        
        # Add to in-memory patterns
        self.play_patterns[pattern] = (platform, url_template)
        
        # Execute the play command
        self._execute_play(play_term, platform, url_template)
        return True
        
    def _get_search_url_template(self, platform):
        """Get the URL template for searching on a platform"""
        templates = {
            "google": "https://www.google.com/search?q={query}",
            "youtube": "https://www.youtube.com/results?search_query={query}",
            "facebook": "https://www.facebook.com/search/top?q={query}",
            "instagram": "https://www.instagram.com/explore/tags/{query}/",
            "twitter": "https://twitter.com/search?q={query}",
            "tiktok": "https://www.tiktok.com/search?q={query}",
            "linkedin": "https://www.linkedin.com/search/results/all/?keywords={query}",
            "github": "https://github.com/search?q={query}",
            "amazon": "https://www.amazon.com/s?k={query}",
            "pinterest": "https://www.pinterest.com/search/pins/?q={query}"
        }
        
        return templates.get(platform.lower())
        
    def _get_play_url_template(self, platform):
        """Get the URL template for playing content on a platform"""
        templates = {
            "youtube": "https://www.youtube.com/embed?listType=search&list={query}&autoplay=1",
            "spotify": "spotify:search:{query}",
            "apple music": "https://embed.music.apple.com/us/album/{query}?autoplay=true",
            "nhaccuatui": "https://www.nhaccuatui.com/bai-hat/{query}.html",
            "zing mp3": "https://zingmp3.vn/bai-hat/{query}/autoplay",
            "soundcloud": "https://soundcloud.com/search/{query}/sounds?auto_play=true",
            "netflix": "https://www.netflix.com/search?q={query}"
        }
        
        return templates.get(platform.lower())
        
    def _find_best_match_youtube(self, query):
        """Find the best matching YouTube video ID for the query"""
        try:
            # In a real implementation: use YouTube Data API
            # For now, just return the search URL
            return f"https://www.youtube.com/results?search_query={quote(query)}"
        except Exception as e:
            print(f"Error finding YouTube video: {e}")
            return f"https://www.youtube.com/results?search_query={quote(query)}"
    
    def _find_best_match_spotify(self, query):
        """Find the best matching Spotify track for the query"""
        try:
            # In a real implementation: use Spotify API
            # For now, just return the search URL
            return f"https://open.spotify.com/search/{quote(query)}"
        except Exception as e:
            print(f"Error finding Spotify track: {e}")
            return f"https://open.spotify.com/search/{quote(query)}"
        
    def _save_command_pattern(self, command_type, pattern, platform, url_template):
        """Save a command pattern to the database"""
        # Check if pattern already exists
        self.cursor.execute(
            "SELECT id, count FROM learned_commands WHERE command_type = ? AND pattern = ? AND platform = ?",
            (command_type, pattern, platform)
        )
        result = self.cursor.fetchone()
        
        if result:
            # Update existing pattern
            self.cursor.execute(
                "UPDATE learned_commands SET count = ?, last_used = CURRENT_TIMESTAMP WHERE id = ?",
                (result[1] + 1, result[0])
            )
        else:
            # Insert new pattern
            self.cursor.execute(
                "INSERT INTO learned_commands (command_type, pattern, platform, url_template) VALUES (?, ?, ?, ?)",
                (command_type, pattern, platform, url_template)
            )
            
        self.conn.commit()
        
    def _execute_search(self, search_term, platform, url_template):
        """Execute a search command"""
        url = url_template.format(query=quote(search_term))
        from backend.command import speak
        speak(f"Searching for {search_term} on {platform}")
        webbrowser.open(url)
        
    def _execute_play(self, play_term, platform, url_template):
        """Execute a play command"""
        from backend.command import speak
        speak(f"Playing {play_term} on {platform}")
        
        if platform.lower() == "youtube":
            url = self._find_best_match_youtube(play_term)
        elif platform.lower() == "spotify":
            url = self._find_best_match_spotify(play_term)
        else:
            # For other platforms, use the regular template
            url = url_template.format(query=quote(play_term))
        
        webbrowser.open(url)
        
    def handle_command(self, query):
        """Handle a command based on learned patterns or dataset commands"""
        # First try to handle using dataset commands
        if self.handle_dataset_command(query):
            return True
            
        # If that fails, try learned patterns
        query_lower = query.lower()
        command_type = self.detect_command_type(query_lower)
        
        if not command_type:
            return False
            
        if command_type == "search":
            # Check if query matches any known search patterns
            for pattern, (platform, url_template) in self.search_patterns.items():
                regex_pattern = pattern.replace("(.*)", "(.*?)")
                match = re.search(regex_pattern, query_lower, re.IGNORECASE)
                if match:
                    search_term = match.group(1)
                    self._execute_search(search_term, platform, url_template)
                    self._save_command_pattern("search", pattern, platform, url_template)
                    return True
                    
            # If no pattern matches, try to learn a new one
            return self.learn_search_command(query_lower)
            
        elif command_type == "play":
            # Check if query matches any known play patterns
            for pattern, (platform, url_template) in self.play_patterns.items():
                regex_pattern = pattern.replace("(.*)", "(.*?)")
                match = re.search(regex_pattern, query_lower, re.IGNORECASE)
                if match:
                    play_term = match.group(1)
                    self._execute_play(play_term, platform, url_template)
                    self._save_command_pattern("play", pattern, platform, url_template)
                    return True
                    
            # If no pattern matches, try to learn a new one
            return self.learn_play_command(query_lower)
            
        return False
            
    def get_supported_platforms(self):
        """Get a list of supported platforms"""
        search_platforms = set()
        play_platforms = set()
        
        self.cursor.execute("SELECT DISTINCT platform FROM learned_commands WHERE command_type = 'search'")
        for (platform,) in self.cursor.fetchall():
            search_platforms.add(platform)
            
        self.cursor.execute("SELECT DISTINCT platform FROM learned_commands WHERE command_type = 'play'")
        for (platform,) in self.cursor.fetchall():
            play_platforms.add(platform)
            
        return {
            "search": list(search_platforms),
            "play": list(play_platforms)
        }
        
    def add_custom_platform(self, command_type, platform, url_template):
        """Add a custom platform with URL template"""
        # Ensure URL template includes query parameter
        if "{query}" not in url_template:
            if "?" in url_template:
                url_template += "&q={query}"
            else:
                url_template += "?q={query}"
                
        if command_type == "search":
            pattern = f"search (.*) on {platform}"
            self._save_command_pattern("search", pattern, platform, url_template)
            self.search_patterns[pattern] = (platform, url_template)
        elif command_type == "play":
            pattern = f"play (.*) on {platform}"
            self._save_command_pattern("play", pattern, platform, url_template)
            self.play_patterns[pattern] = (platform, url_template)
        else:
            return False
            
        return True
    