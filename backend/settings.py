# backend/settings.py

import sqlite3
import json
import os
import eel
from backend.command import speak

class Settings:
    def __init__(self, db_path="jarvis.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._ensure_tables_exist()
        
    def _ensure_tables_exist(self):
        """Ensure all necessary tables exist in the database"""
        # Create settings table if it doesn't exist
        query = """
        CREATE TABLE IF NOT EXISTS settings(
            id INTEGER PRIMARY KEY,
            category VARCHAR(50),
            key VARCHAR(100),
            value TEXT,
            modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(query)
        self.conn.commit()
        
    def get_setting(self, category, key, default=None):
        """Get a setting value"""
        self.cursor.execute(
            "SELECT value FROM settings WHERE category = ? AND key = ?",
            (category, key)
        )
        result = self.cursor.fetchone()
        
        if result:
            try:
                return json.loads(result[0])
            except:
                return result[0]
        return default
        
    def set_setting(self, category, key, value):
        """Set a setting value"""
        if isinstance(value, (dict, list, tuple)):
            value = json.dumps(value)
            
        self.cursor.execute(
            "SELECT id FROM settings WHERE category = ? AND key = ?",
            (category, key)
        )
        result = self.cursor.fetchone()
        
        if result:
            self.cursor.execute(
                "UPDATE settings SET value = ?, modified = CURRENT_TIMESTAMP WHERE id = ?",
                (value, result[0])
            )
        else:
            self.cursor.execute(
                "INSERT INTO settings (category, key, value) VALUES (?, ?, ?)",
                (category, key, value)
            )
            
        self.conn.commit()
        return True
        
    def get_all_settings(self, category=None):
        """Get all settings, optionally filtered by category"""
        if category:
            self.cursor.execute(
                "SELECT category, key, value FROM settings WHERE category = ?",
                (category,)
            )
        else:
            self.cursor.execute(
                "SELECT category, key, value FROM settings"
            )
            
        results = {}
        for category, key, value in self.cursor.fetchall():
            if category not in results:
                results[category] = {}
                
            try:
                results[category][key] = json.loads(value)
            except:
                results[category][key] = value
                
        return results
        
    def export_settings(self, file_path):
        """Export settings to a JSON file"""
        settings = self.get_all_settings()
        
        try:
            with open(file_path, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
            
    def import_settings(self, file_path):
        """Import settings from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                settings = json.load(f)
                
            for category, category_settings in settings.items():
                for key, value in category_settings.items():
                    self.set_setting(category, key, value)
                    
            return True
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
            
    def list_learned_commands(self):
        """List all learned commands"""
        self.cursor.execute(
            """
            SELECT command_type, pattern, platform, url_template, count, last_used 
            FROM learned_commands 
            ORDER BY command_type, count DESC
            """
        )
        
        results = []
        for command_type, pattern, platform, url_template, count, last_used in self.cursor.fetchall():
            results.append({
                "type": command_type,
                "pattern": pattern,
                "platform": platform,
                "url_template": url_template,
                "usage_count": count,
                "last_used": last_used
            })
            
        return results
        
    def delete_learned_command(self, command_type, platform):
        """Delete a learned command"""
        self.cursor.execute(
            "DELETE FROM learned_commands WHERE command_type = ? AND platform = ?",
            (command_type, platform)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0
        
    def modify_learned_command(self, command_type, platform, new_url_template):
        """Modify a learned command's URL template"""
        self.cursor.execute(
            "UPDATE learned_commands SET url_template = ? WHERE command_type = ? AND platform = ?",
            (new_url_template, command_type, platform)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0


# Expose some settings functions to JavaScript through eel
@eel.expose
def get_learned_commands():
    settings = Settings()
    return settings.list_learned_commands()

@eel.expose
def delete_command(command_type, platform):
    settings = Settings()
    success = settings.delete_learned_command(command_type, platform)
    if success:
        speak(f"Successfully removed {command_type} command for {platform}")
    else:
        speak(f"Could not find {command_type} command for {platform}")
    return success

@eel.expose
def modify_command(command_type, platform, new_url_template):
    settings = Settings()
    success = settings.modify_learned_command(command_type, platform, new_url_template)
    if success:
        speak(f"Successfully updated {command_type} command for {platform}")
    else:
        speak(f"Could not update {command_type} command for {platform}")
    return success

@eel.expose
def export_learned_commands(file_path):
    settings = Settings()
    success = settings.export_settings(file_path)
    if success:
        speak("Successfully exported settings")
    else:
        speak("Failed to export settings")
    return success

@eel.expose
def import_learned_commands(file_path):
    settings = Settings()
    success = settings.import_settings(file_path)
    if success:
        speak("Successfully imported settings")
    else:
        speak("Failed to import settings")
    return success