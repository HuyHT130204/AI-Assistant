import re
import sqlite3
import webbrowser
from urllib.parse import quote
import os
import requests
import json
from backend.command import speak
from backend.helper import remove_words

class CommandLearner:
    def __init__(self, db_path="jarvis.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._ensure_tables_exist()
        self.load_patterns()
        
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
        self.conn.commit()
        
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
            speak(f"I couldn't understand what to search for on {platform}")
            return False
            
        # Create URL template based on platform
        url_template = self._get_search_url_template(platform)
        if not url_template:
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
            speak(f"I couldn't understand what to play on {platform}")
            return False
            
        # Create URL template based on platform
        url_template = self._get_play_url_template(platform)
        if not url_template:
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
        # Đã thay đổi URL template để trực tiếp phát nội dung thay vì chỉ tìm kiếm
        templates = {
            "youtube": "https://www.youtube.com/embed?listType=search&list={query}&autoplay=1",
            "spotify": "spotify:search:{query}",  # Sử dụng URI scheme của Spotify
            "apple music": "https://embed.music.apple.com/us/album/{query}?autoplay=true",
            "nhaccuatui": "https://www.nhaccuatui.com/bai-hat/{query}.html",
            "zing mp3": "https://zingmp3.vn/bai-hat/{query}/autoplay",
            "soundcloud": "https://soundcloud.com/search/{query}/sounds?auto_play=true",
            "netflix": "https://www.netflix.com/watch/{query}"
        }
        
        return templates.get(platform.lower())
        
    def _find_best_match_youtube(self, query):
        """Find the best matching YouTube video ID for the query"""
        # Giả định: Sử dụng YouTube Data API để tìm video phù hợp nhất
        # Trong phiên bản thực: sử dụng API key và gọi API thực tế
        try:
            # Đây chỉ là code mẫu, thực tế cần API key của YouTube
            api_key = "YOUR_YOUTUBE_API_KEY"  # Thay bằng API key thực
            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={quote(query)}&type=video&key={api_key}"
            
            # Trong môi trường thực tế: gọi API và lấy video ID
            # response = requests.get(url)
            # data = response.json()
            # video_id = data['items'][0]['id']['videoId']
            # return f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
            
            # Do không thể gọi API thực nên trả về URL tìm kiếm
            return f"https://www.youtube.com/results?search_query={quote(query)}"
        except Exception as e:
            print(f"Error finding YouTube video: {e}")
            return f"https://www.youtube.com/results?search_query={quote(query)}"
    
    def _find_best_match_spotify(self, query):
        """Find the best matching Spotify track for the query"""
        try:
            # Đây chỉ là code mẫu, thực tế cần API của Spotify
            # Trong thực tế: sử dụng Spotify API để lấy URI của track phù hợp nhất
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
        speak(f"Searching for {search_term} on {platform}")
        webbrowser.open(url)
        
    def _execute_play(self, play_term, platform, url_template):
        """Execute a play command"""
        # Xử lý đặc biệt cho từng nền tảng để phát trực tiếp
        speak(f"Playing {play_term} on {platform}")
        
        if platform.lower() == "youtube":
            url = self._find_best_match_youtube(play_term)
        elif platform.lower() == "spotify":
            url = self._find_best_match_spotify(play_term)
        else:
            # Đối với các nền tảng khác, sử dụng template thông thường
            url = url_template.format(query=quote(play_term))
        
        webbrowser.open(url)
        
    def handle_command(self, query):
        """Handle a command based on learned patterns"""
        query = query.lower()
        command_type = self.detect_command_type(query)
        
        if not command_type:
            return False
            
        if command_type == "search":
            # Check if query matches any known search patterns
            for pattern, (platform, url_template) in self.search_patterns.items():
                regex_pattern = pattern.replace("(.*)", "(.*?)")
                match = re.search(regex_pattern, query, re.IGNORECASE)
                if match:
                    search_term = match.group(1)
                    self._execute_search(search_term, platform, url_template)
                    self._save_command_pattern("search", pattern, platform, url_template)
                    return True
                    
            # If no pattern matches, try to learn a new one
            return self.learn_search_command(query)
            
        elif command_type == "play":
            # Check if query matches any known play patterns
            for pattern, (platform, url_template) in self.play_patterns.items():
                regex_pattern = pattern.replace("(.*)", "(.*?)")
                match = re.search(regex_pattern, query, re.IGNORECASE)
                if match:
                    play_term = match.group(1)
                    self._execute_play(play_term, platform, url_template)
                    self._save_command_pattern("play", pattern, platform, url_template)
                    return True
                    
            # If no pattern matches, try to learn a new one
            return self.learn_play_command(query)
            
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
        # Kiểm tra và điều chỉnh URL template nếu cần
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