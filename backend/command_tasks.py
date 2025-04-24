import os
import subprocess
import time
import webbrowser
import pyautogui
from urllib.parse import quote
import psutil
import platform
from datetime import datetime
from backend.command import speak
from backend.helper import remove_words

class TaskManager:
    """Base class for all task managers"""
    def __init__(self):
        pass

class SystemTasks:
    """Handle system-related tasks"""
    def open_application(self, query):
        """Open an application based on query"""
        query_lower = query.lower()
        app_map = {
            "browser": "chrome.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "music": "spotify.exe",
            "spotify": "spotify.exe",
            "vlc": "vlc.exe",
            "media player": "wmplayer.exe",
            "notepad": "notepad.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "calculator": "calc.exe",
            "terminal": "cmd.exe",
            "command prompt": "cmd.exe",
            "file explorer": "explorer.exe",
            "files": "explorer.exe",
            "email": "outlook.exe",
            "outlook": "outlook.exe",
            "paint": "mspaint.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "settings": "ms-settings:",
            "system settings": "ms-settings:",
        }
        
        # Find which app is mentioned in the query
        app_name = None
        for app in app_map:
            if app in query_lower:
                app_name = app
                break
                
        # If specific app mentioned, open it
        if app_name:
            try:
                app_path = app_map[app_name]
                speak(f"Opening {app_name}")
                if app_path.startswith("ms-"):
                    os.system(f"start {app_path}")
                else:
                    subprocess.Popen(app_path, shell=True)
                return True
            except Exception as e:
                speak(f"I couldn't open {app_name}. {str(e)}")
                return False
        else:
            # If no specific app mentioned, try to extract app name from query
            words = query_lower.split()
            for word in words:
                if len(word) > 3 and word not in ["open", "launch", "start", "run", "please", "the", "app", "application"]:
                    try:
                        speak(f"Trying to open {word}")
                        subprocess.Popen(word + ".exe", shell=True)
                        return True
                    except:
                        continue
            
            speak("I'm not sure which application you want me to open")
            return False

    def close_application(self, query):
        """Close an application based on query"""
        query_lower = query.lower()
        app_map = {
            "browser": ["chrome.exe", "firefox.exe", "msedge.exe", "iexplore.exe"],
            "chrome": ["chrome.exe"],
            "firefox": ["firefox.exe"],
            "edge": ["msedge.exe"],
            "music": ["spotify.exe", "wmplayer.exe"],
            "spotify": ["spotify.exe"],
            "vlc": ["vlc.exe"],
            "media player": ["wmplayer.exe"],
            "notepad": ["notepad.exe"],
            "word": ["winword.exe"],
            "excel": ["excel.exe"],
            "powerpoint": ["powerpnt.exe"],
            "calculator": ["calc.exe"],
            "terminal": ["cmd.exe"],
            "command prompt": ["cmd.exe"],
        }
        
        # Find which app is mentioned in the query
        app_name = None
        for app in app_map:
            if app in query_lower:
                app_name = app
                break
                
        # If specific app mentioned, close it
        if app_name:
            try:
                app_processes = app_map[app_name]
                closed = False
                for process_name in app_processes:
                    os.system(f"taskkill /f /im {process_name}")
                    closed = True
                
                if closed:
                    speak(f"Closed {app_name}")
                    return True
                else:
                    speak(f"Couldn't find {app_name} running")
                    return False
            except Exception as e:
                speak(f"I couldn't close {app_name}. {str(e)}")
                return False
        else:
            # Try to extract app name from query
            words = query_lower.split()
            for word in words:
                if len(word) > 3 and word not in ["close", "exit", "quit", "terminate", "please", "the", "app", "application"]:
                    try:
                        speak(f"Trying to close {word}")
                        os.system(f"taskkill /f /im {word}.exe")
                        return True
                    except:
                        continue
            
            speak("I'm not sure which application you want me to close")
            return False

    def open_system_settings(self, query):
        """Open system settings based on query"""
        query_lower = query.lower()
        settings_map = {
            "display": "ms-settings:display",
            "screen": "ms-settings:display",
            "personalization": "ms-settings:personalization",
            "theme": "ms-settings:personalization",
            "background": "ms-settings:personalization-background",
            "colors": "ms-settings:colors",
            "network": "ms-settings:network",
            "wifi": "ms-settings:network-wifi",
            "ethernet": "ms-settings:network-ethernet",
            "vpn": "ms-settings:network-vpn",
            "bluetooth": "ms-settings:bluetooth",
            "devices": "ms-settings:devices",
            "printers": "ms-settings:printers",
            "mouse": "ms-settings:mousetouchpad",
            "keyboard": "ms-settings:keyboard",
            "time": "ms-settings:dateandtime",
            "language": "ms-settings:regionlanguage",
            "update": "ms-settings:windowsupdate",
            "backup": "ms-settings:backup",
            "privacy": "ms-settings:privacy",
            "account": "ms-settings:yourinfo",
            "user": "ms-settings:yourinfo",
            "notification": "ms-settings:notifications",
            "sound": "ms-settings:sound",
            "volume": "ms-settings:sound",
            "power": "ms-settings:powersleep",
            "battery": "ms-settings:batterysaver",
            "default apps": "ms-settings:defaultapps",
            "apps": "ms-settings:appsfeatures",
            "system": "ms-settings:system",
        }
        
        # Find which setting is mentioned in the query
        setting = None
        for s in settings_map:
            if s in query_lower:
                setting = s
                break
                
        # If specific setting mentioned, open it
        if setting:
            try:
                setting_path = settings_map[setting]
                speak(f"Opening {setting} settings")
                os.system(f"start {setting_path}")
                return True
            except Exception as e:
                speak(f"I couldn't open {setting} settings. {str(e)}")
                return False
        else:
            # If no specific setting, open main settings
            try:
                speak(f"Opening system settings")
                os.system("start ms-settings:")
                return True
            except Exception as e:
                speak(f"I couldn't open system settings. {str(e)}")
                return False

    def system_power_management(self, query):
        """Handle system power management commands (shutdown, restart, etc.)"""
        query_lower = query.lower()
        
        # Confirm critical actions
        from backend.command_handler import takecommand

        if "shutdown" in query_lower or "turn off" in query_lower or "power off" in query_lower:
            speak("Are you sure you want to shut down your computer?")
            confirmation = takecommand()
            if confirmation and ("yes" in confirmation.lower() or "ok" in confirmation.lower() or "sure" in confirmation.lower() or "confirm" in confirmation.lower()):
                try:
                    speak("Shutting down your computer in 30 seconds. To cancel, say 'cancel shutdown'")
                    os.system("shutdown /s /t 30")
                    return True
                except Exception as e:
                    speak(f"I couldn't shutdown the computer. {str(e)}")
                    return False
            else:
                speak("Shutdown cancelled")
                return True
                
        elif "restart" in query_lower or "reboot" in query_lower:
            speak("Are you sure you want to restart your computer?")
            confirmation = takecommand()
            if confirmation and ("yes" in confirmation.lower() or "ok" in confirmation.lower() or "sure" in confirmation.lower() or "confirm" in confirmation.lower()):
                try:
                    speak("Restarting your computer in 30 seconds. To cancel, say 'cancel restart'")
                    os.system("shutdown /r /t 30")
                    return True
                except Exception as e:
                    speak(f"I couldn't restart the computer. {str(e)}")
                    return False
            else:
                speak("Restart cancelled")
                return True
                
        elif "sleep" in query_lower:
            speak("Putting your computer to sleep")
            try:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return True
            except Exception as e:
                speak(f"I couldn't put the computer to sleep. {str(e)}")
                return False
                
        elif "log out" in query_lower or "sign out" in query_lower:
            speak("Are you sure you want to log out?")
            confirmation = takecommand()
            if confirmation and ("yes" in confirmation.lower() or "ok" in confirmation.lower() or "sure" in confirmation.lower() or "confirm" in confirmation.lower()):
                try:
                    speak("Logging out in 5 seconds")
                    os.system("shutdown /l")
                    return True
                except Exception as e:
                    speak(f"I couldn't log out. {str(e)}")
                    return False
            else:
                speak("Log out cancelled")
                return True
                
        elif "cancel" in query_lower:
            if "shutdown" in query_lower:
                try:
                    speak("Cancelling shutdown")
                    os.system("shutdown /a")
                    return True
                except Exception as e:
                    speak(f"I couldn't cancel the shutdown. {str(e)}")
                    return False
            elif "restart" in query_lower:
                try:
                    speak("Cancelling restart")
                    os.system("shutdown /a")
                    return True
                except Exception as e:
                    speak(f"I couldn't cancel the restart. {str(e)}")
                    return False
        
        return False

    def system_information(self, query):
        """Get system information"""
        query_lower = query.lower()
        
        # Get basic system information
        system_info = {
            "System": platform.system(),
            "Node Name": platform.node(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
        }
        
        # Get more detailed information based on query
        if "cpu" in query_lower or "processor" in query_lower:
            import psutil
            cpu_count = psutil.cpu_count(logical=False)
            logical_count = psutil.cpu_count(logical=True)
            cpu_usage = psutil.cpu_percent(interval=1)
            speak(f"Your CPU has {cpu_count} physical cores and {logical_count} logical cores. Current CPU usage is {cpu_usage}%")
            return True
            
        elif "memory" in query_lower or "ram" in query_lower:
            import psutil
            memory = psutil.virtual_memory()
            total_gb = round(memory.total / (1024 ** 3), 2)
            used_gb = round(memory.used / (1024 ** 3), 2)
            percentage = memory.percent
            speak(f"You have {total_gb} GB of RAM, with {used_gb} GB ({percentage}%) currently in use")
            return True
            
        elif "disk" in query_lower or "storage" in query_lower or "drive" in query_lower:
            import psutil
            partitions = psutil.disk_partitions()
            disk_info = []
            
            for partition in partitions:
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    total_gb = round(partition_usage.total / (1024 ** 3), 2)
                    used_gb = round(partition_usage.used / (1024 ** 3), 2)
                    percentage = partition_usage.percent
                    disk_info.append(f"Drive {partition.device}: {used_gb} GB used out of {total_gb} GB ({percentage}%)")
                except Exception:
                    # Some drives might not be accessible
                    continue
                    
            if disk_info:
                speak("\n".join(disk_info))
            else:
                speak("I couldn't access information about your disk drives")
            return True
            
        elif "network" in query_lower:
            import psutil
            network_info = []
            
            net_io = psutil.net_io_counters()
            bytes_sent_mb = round(net_io.bytes_sent / (1024 ** 2), 2)
            bytes_recv_mb = round(net_io.bytes_recv / (1024 ** 2), 2)
            network_info.append(f"Network usage: {bytes_sent_mb} MB sent, {bytes_recv_mb} MB received")
            
            try:
                addresses = psutil.net_if_addrs()
                for interface_name, interface_addresses in addresses.items():
                    for address in interface_addresses:
                        if str(address.family) == 'AddressFamily.AF_INET':
                            network_info.append(f"Interface: {interface_name}, IP: {address.address}")
            except:
                pass
                
            speak("\n".join(network_info))
            return True
            
        else:
            # Generic system information
            info_str = []
            for key, value in system_info.items():
                info_str.append(f"{key}: {value}")
                
            speak("\n".join(info_str))
            return True

    def battery_management(self, query):
        """Get battery information"""
        try:
            import psutil
            
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                power_plugged = battery.power_plugged
                
                status = "plugged in" if power_plugged else "on battery"
                
                if percent <= 20 and not power_plugged:
                    speak(f"Warning: Battery is low at {percent}%. Please connect your charger.")
                else:
                    speak(f"Battery is at {percent}% and is currently {status}.")
                
                if battery.secsleft > 0 and not power_plugged:
                    minutes_left = battery.secsleft // 60
                    hours_left = minutes_left // 60
                    minutes_left = minutes_left % 60
                    
                    speak(f"You have approximately {hours_left} hours and {minutes_left} minutes of battery life remaining.")
                
                return True
            else:
                speak("I couldn't find a battery on your system. You might be using a desktop or the battery information is not available.")
                return False
        except Exception as e:
            speak(f"I couldn't check the battery. {str(e)}")
            return False

    def task_management(self, query):
        """Manage system tasks/processes"""
        query_lower = query.lower()
        
        if "list" in query_lower or "show" in query_lower or "display" in query_lower:
            try:
                # Open task manager
                speak("Opening task manager")
                subprocess.Popen("taskmgr.exe", shell=True)
                return True
            except Exception as e:
                speak(f"I couldn't open task manager. {str(e)}")
                return False
                
        elif "kill" in query_lower or "terminate" in query_lower or "end" in query_lower:
            # Extract process name
            process_keywords = ["kill", "terminate", "end", "process", "task", "application", "app"]
            words = query_lower.split()
            
            process_name = None
            for word in words:
                if word not in process_keywords and len(word) > 3:
                    process_name = word
                    break
                    
            if process_name:
                try:
                    speak(f"Attempting to terminate {process_name}")
                    os.system(f"taskkill /f /im {process_name}.exe")
                    return True
                except Exception as e:
                    speak(f"I couldn't terminate {process_name}. {str(e)}")
                    return False
            else:
                speak("Please specify which process you want to terminate")
                return False
        
        # Default: show running tasks
        try:
            speak("Here are your active tasks")
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    # Get only user-visible applications
                    if proc.memory_info().rss > 50 * 1024 * 1024:  # Only show processes using more than 50MB
                        processes.append((proc.info['name'], proc.memory_info().rss))
                except:
                    pass
                    
            # Sort by memory usage (descending)
            processes.sort(key=lambda x: x[1], reverse=True)
            
            # Show top 5 processes
            speak("Top processes by memory usage:")
            for i, (name, memory) in enumerate(processes[:5]):
                memory_mb = round(memory / (1024 * 1024), 2)
                speak(f"{i+1}. {name}: {memory_mb} MB")
                
            # Also open task manager
            subprocess.Popen("taskmgr.exe", shell=True)
            
            return True
        except Exception as e:
            speak(f"I couldn't retrieve the task list. {str(e)}")
            return False

    def software_installation(self, query):
        """Handle software installation requests"""
        query_lower = query.lower()
        
        # Extract software name
        software_name = None
        install_keywords = ["install", "download", "get", "add"]
        
        for keyword in install_keywords:
            if keyword in query_lower:
                query_parts = query_lower.split(keyword)
                if len(query_parts) > 1:
                    software_name = query_parts[1].strip()
                    break
        
        if not software_name:
            # Try to extract from general query
            words = query_lower.split()
            for word in words:
                if word not in install_keywords + ["application", "app", "software", "program", "package", "please", "for", "me", "the"]:
                    software_name = word
                    break
        
        if software_name:
            # Common software
            software_map = {
                "vlc": "https://www.videolan.org/vlc/",
                "chrome": "https://www.google.com/chrome/",
                "firefox": "https://www.mozilla.org/firefox/",
                "edge": "https://www.microsoft.com/edge",
                "7zip": "https://www.7-zip.org/",
                "winrar": "https://www.win-rar.com/",
                "spotify": "https://www.spotify.com/download/",
                "steam": "https://store.steampowered.com/about/",
                "zoom": "https://zoom.us/download",
                "skype": "https://www.skype.com/get-skype/",
                "teams": "https://www.microsoft.com/microsoft-teams/download-app",
                "discord": "https://discord.com/download",
                "whatsapp": "https://www.whatsapp.com/download",
                "telegram": "https://desktop.telegram.org/",
                "adobe reader": "https://get.adobe.com/reader/",
                "office": "https://www.office.com/",
                "excel": "https://www.office.com/",
                "word": "https://www.office.com/",
                "powerpoint": "https://www.office.com/",
                "outlook": "https://www.office.com/",
            }
            
            # Check if the software is known
            for sw_name, sw_url in software_map.items():
                if sw_name in software_name:
                    try:
                        speak(f"Opening download page for {sw_name}")
                        webbrowser.open(sw_url)
                        return True
                    except Exception as e:
                        speak(f"I couldn't open the download page for {sw_name}. {str(e)}")
                        return False
            
            # If not known, search for it
            try:
                speak(f"Searching for {software_name} download")
                webbrowser.open(f"https://www.google.com/search?q=download+{quote(software_name)}")
                return True
            except Exception as e:
                speak(f"I couldn't search for {software_name}. {str(e)}")
                return False
        
        # Default: open Microsoft Store
        try:
            speak("Opening Microsoft Store")
            os.system("start ms-windows-store:")
            return True
        except Exception as e:
            speak(f"I couldn't open Microsoft Store. {str(e)}")
            return False

    def system_updates(self, query):
        """Check for system updates"""
        try:
            speak("Opening Windows Update settings")
            os.system("start ms-settings:windowsupdate")
            return True
        except Exception as e:
            speak(f"I couldn't open Windows Update settings. {str(e)}")
            return False

    def system_troubleshooting(self, query):
        """Troubleshoot system issues"""
        query_lower = query.lower()
        
        if "network" in query_lower or "internet" in query_lower or "wifi" in query_lower:
            try:
                speak("Running network troubleshooter")
                os.system("msdt.exe /id NetworkDiagnosticsWeb")
                return True
            except Exception as e:
                speak(f"I couldn't run the network troubleshooter. {str(e)}")
                return False
                
        elif "printer" in query_lower:
            try:
                speak("Running printer troubleshooter")
                os.system("msdt.exe /id PrinterDiagnostic")
                return True
            except Exception as e:
                speak(f"I couldn't run the printer troubleshooter. {str(e)}")
                return False
                
        elif "audio" in query_lower or "sound" in query_lower:
            try:
                speak("Running audio troubleshooter")
                os.system("msdt.exe /id AudioPlaybackDiagnostic")
                return True
            except Exception as e:
                speak(f"I couldn't run the audio troubleshooter. {str(e)}")
                return False
                
        elif "power" in query_lower or "battery" in query_lower:
            try:
                speak("Running power troubleshooter")
                os.system("msdt.exe /id PowerDiagnostic")
                return True
            except Exception as e:
                speak(f"I couldn't run the power troubleshooter. {str(e)}")
                return False
        
        # Default: open general troubleshooting
        try:
            speak("Opening Windows troubleshooter")
            os.system("start ms-settings:troubleshoot")
            return True
        except Exception as e:
            speak(f"I couldn't open the troubleshooter. {str(e)}")
            return False

    def system_monitoring(self, query):
        """Monitor system resources"""
        query_lower = query.lower()
        
        if "cpu" in query_lower:
            try:
                import psutil
                
                cpu_usage = psutil.cpu_percent(interval=2)
                cpu_count = psutil.cpu_count(logical=False)
                logical_cores = psutil.cpu_count(logical=True)
                
                speak(f"Current CPU usage is {cpu_usage}%. You have {cpu_count} physical cores and {logical_cores} logical cores.")
                
                # Also open Task Manager with CPU tab
                os.system("taskmgr.exe /0")
                
                return True
            except Exception as e:
                speak(f"I couldn't monitor CPU usage. {str(e)}")
                return False
                
        elif "memory" in query_lower or "ram" in query_lower:
            try:
                import psutil
                
                memory = psutil.virtual_memory()
                total_gb = round(memory.total / (1024 ** 3), 2)
                used_gb = round(memory.used / (1024 ** 3), 2)
                available_gb = round(memory.available / (1024 ** 3), 2)
                percent = memory.percent
                
                speak(f"Memory usage is at {percent}%. {used_gb} GB used out of {total_gb} GB total. You have {available_gb} GB available.")
                
                # Also open Task Manager with Memory tab
                os.system("taskmgr.exe /1")
                
                return True
            except Exception as e:
                speak(f"I couldn't monitor memory usage. {str(e)}")
                return False
                
        elif "disk" in query_lower:
            try:
                import psutil
                
                speak("Checking disk usage:")
                disks = psutil.disk_partitions()
                
                for disk in disks:
                    try:
                        disk_usage = psutil.disk_usage(disk.mountpoint)
                        total_gb = round(disk_usage.total / (1024 ** 3), 2)
                        used_gb = round(disk_usage.used / (1024 ** 3), 2)
                        percent = disk_usage.percent
                        
                        speak(f"Drive {disk.device}: {used_gb} GB used out of {total_gb} GB. {percent}% full.")
                    except:
                        # Some drives might not be accessible
                        continue
                
                # Also open Task Manager with Disk tab
                os.system("taskmgr.exe /2")
                
                return True
            except Exception as e:
                speak(f"I couldn't monitor disk usage. {str(e)}")
                return False
                
        elif "network" in query_lower:
            try:
                import psutil
                
                net_io = psutil.net_io_counters()
                bytes_sent_mb = round(net_io.bytes_sent / (1024 ** 2), 2)
                bytes_recv_mb = round(net_io.bytes_recv / (1024 ** 2), 2)
                
                speak(f"Network activity: {bytes_sent_mb} MB sent, {bytes_recv_mb} MB received.")
                
                # Also open Task Manager with Network tab
                os.system("taskmgr.exe /3")
                
                return True
            except Exception as e:
                speak(f"I couldn't monitor network usage. {str(e)}")
                return False
        
        # Default: open Resource Monitor
        try:
            speak("Opening Resource Monitor")
            os.system("resmon.exe")
            return True
        except Exception as e:
            speak(f"I couldn't open Resource Monitor. {str(e)}")
            return False

    def device_management(self, query):
        """Manage devices"""
        try:
            speak("Opening Device Manager")
            os.system("devmgmt.msc")
            return True
        except Exception as e:
            speak(f"I couldn't open Device Manager. {str(e)}")
            return False

    def printer_management(self, query):
        """Manage printers"""
        query_lower = query.lower()
        
        if "add" in query_lower:
            try:
                speak("Opening Add Printer wizard")
                os.system("rundll32.exe printui.dll,PrintUIEntry /il")
                return True
            except Exception as e:
                speak(f"I couldn't open Add Printer wizard. {str(e)}")
                return False
        
        # Default: open printer settings
        try:
            speak("Opening printer settings")
            os.system("start ms-settings:printers")
            return True
        except Exception as e:
            speak(f"I couldn't open printer settings. {str(e)}")
            return False

    def keyboard_shortcuts(self, query):
        """Show keyboard shortcuts"""
        common_shortcuts = [
            "Windows key: Open Start menu",
            "Alt + Tab: Switch between open applications",
            "Windows key + Tab: Task view",
            "Windows key + D: Show/hide desktop",
            "Windows key + E: Open File Explorer",
            "Windows key + I: Open Settings",
            "Windows key + L: Lock your computer",
            "Windows key + S: Search",
            "Ctrl + C: Copy",
            "Ctrl + X: Cut",
            "Ctrl + V: Paste",
            "Ctrl + Z: Undo",
            "Ctrl + Y: Redo",
            "Ctrl + A: Select all",
            "Ctrl + F: Find",
            "Ctrl + P: Print",
            "Ctrl + S: Save",
            "Ctrl + N: New",
            "Ctrl + O: Open",
            "Ctrl + W: Close tab/window",
            "Alt + F4: Close application",
            "F1: Help",
            "F2: Rename",
            "F5: Refresh",
        ]
        
        speak("Here are some common keyboard shortcuts:")
        for shortcut in common_shortcuts[:10]:  # Limit to 10 to avoid speaking too much
            speak(shortcut)
            
        try:
            speak("Opening Windows keyboard shortcuts guide")
            webbrowser.open("https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec")
            return True
        except Exception as e:
            speak(f"I couldn't open the shortcuts guide. {str(e)}")
            return False

    def clipboard_management(self, query):
        """Manage clipboard"""
        try:
            speak("Opening Windows clipboard history")
            pyautogui.hotkey('win', 'v')
            return True
        except Exception as e:
            speak(f"I couldn't open clipboard history. {str(e)}")
            return False

    def screen_capture(self, query):
        """Take screenshots"""
        query_lower = query.lower()
        
        if "window" in query_lower:
            try:
                speak("Press Alt+PrtScn to capture the active window")
                pyautogui.hotkey('alt', 'printscreen')
                speak("Screenshot of active window copied to clipboard")
                return True
            except Exception as e:
                speak(f"I couldn't take a screenshot. {str(e)}")
                return False
                
        elif "area" in query_lower or "region" in query_lower or "selection" in query_lower:
            try:
                speak("Press Windows+Shift+S to select an area to capture")
                pyautogui.hotkey('win', 'shift', 's')
                return True
            except Exception as e:
                speak(f"I couldn't start the snipping tool. {str(e)}")
                return False
        
        # Default: full screen screenshot
        try:
            speak("Taking a full screen screenshot")
            pyautogui.press('printscreen')
            speak("Screenshot taken and copied to clipboard")
            
            # Open Paint to paste the screenshot
            os.system("mspaint")
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'v')
            
            return True
        except Exception as e:
            speak(f"I couldn't take a screenshot. {str(e)}")
            return False

    def system_time(self, query):
        """Get system time"""
        try:
            from datetime import datetime
            
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            
            speak(f"The current time is {time_str} on {date_str}")
            return True
        except Exception as e:
            speak(f"I couldn't check the system time. {str(e)}")
            return False

    def taskbar_management(self, query):
        """Manage taskbar settings"""
        try:
            speak("Opening taskbar settings")
            os.system("start ms-settings:taskbar")
            return True
        except Exception as e:
            speak(f"I couldn't open taskbar settings. {str(e)}")
            return False

    def command_line_operations(self, query):
        """Run command line operations"""
        query_lower = query.lower()
        
        if "list" in query_lower or "directory" in query_lower or "files" in query_lower:
            try:
                speak("Opening Command Prompt to list files")
                os.system("start cmd /k dir")
                return True
            except Exception as e:
                speak(f"I couldn't open Command Prompt. {str(e)}")
                return False
        
        # Default: open Command Prompt
        try:
            speak("Opening Command Prompt")
            os.system("start cmd")
            return True
        except Exception as e:
            speak(f"I couldn't open Command Prompt. {str(e)}")
            return False


class FileTasks:
    """Handle file-related tasks"""
    def file_management(self, query):
        """Handle file management commands"""
        # Just open file explorer by default
        try:
            speak("Opening file explorer")
            os.system("explorer")
            return True
        except Exception as e:
            speak(f"I couldn't open file explorer. {str(e)}")
            return False

    def file_search(self, query):
        """Search for files based on query"""
        query_lower = query.lower()
        
        # Extract file name or type to search for
        search_term = None
        file_type = None
        
        # Check for common file types
        file_types = {
            "document": [".doc", ".docx", ".pdf", ".txt", ".rtf"],
            "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "video": [".mp4", ".avi", ".mov", ".wmv", ".mkv"],
            "music": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
            "spreadsheet": [".xls", ".xlsx", ".csv"],
            "presentation": [".ppt", ".pptx"],
        }
        
        for ftype in file_types:
            if ftype in query_lower:
                file_type = ftype
                break
        
        # Try to extract search term
        words = query_lower.split()
        for i, word in enumerate(words):
            if word in ["search", "find", "locate", "look", "for"]:
                if i+1 < len(words):
                    # Take a few words after the search keyword as the search term
                    search_term = " ".join(words[i+1:])
                    # Remove filler words
                    search_term = search_term.replace("for", "").replace("a", "").replace("an", "").replace("the", "").strip()
                    break
        
        # If search term is found, search for it
        if search_term:
            try:
                speak(f"Searching for {search_term}")
                
                # If it's a specific file type, open the search with type filter
                if file_type:
                    file_extensions = " OR ".join([f"ext:{ext[1:]}" for ext in file_types[file_type]])
                    os.system(f'start search-ms:query={search_term} {file_extensions}')
                else:
                    # General search
                    os.system(f'start search-ms:query={search_term}')
                
                return True
            except Exception as e:
                speak(f"I couldn't search for {search_term}. {str(e)}")
                return False
        else:
            # If no search term, just open search
            try:
                speak("Opening Windows search")
                pyautogui.hotkey('win', 's')
                return True
            except Exception as e:
                speak(f"I couldn't open search. {str(e)}")
                return False

    def file_backup(self, query):
        """Handle file backup requests"""
        query_lower = query.lower()
        
        # Open backup settings
        try:
            speak("Opening Windows backup settings")
            os.system("start ms-settings:backup")
            return True
        except Exception as e:
            speak(f"I couldn't open backup settings. {str(e)}")
            return False

    def file_compression(self, query):
        """Handle file compression requests"""
        speak("To compress files, please right-click on the file or folder, select 'Send to', and then 'Compressed (zipped) folder'.")
        
        # Open File Explorer
        try:
            os.system("explorer")
            return True
        except Exception as e:
            speak(f"I couldn't open File Explorer. {str(e)}")
            return False

    def cloud_storage(self, query):
        """Handle cloud storage requests"""
        query_lower = query.lower()
        
        # Check if a specific cloud service is mentioned
        cloud_services = {
            "onedrive": "https://onedrive.live.com",
            "google drive": "https://drive.google.com",
            "dropbox": "https://www.dropbox.com",
            "box": "https://app.box.com",
            "icloud": "https://www.icloud.com",
        }
        
        for service, url in cloud_services.items():
            if service in query_lower:
                try:
                    speak(f"Opening {service}")
                    webbrowser.open(url)
                    return True
                except Exception as e:
                    speak(f"I couldn't open {service}. {str(e)}")
                    return False
        
        # Default to OneDrive
        try:
            speak("Opening OneDrive")
            webbrowser.open("https://onedrive.live.com")
            return True
        except Exception as e:
            speak(f"I couldn't open OneDrive. {str(e)}")
            return False

    def file_permissions(self, query):
        """Manage file permissions"""
        speak("To change file permissions, please right-click on the file, select Properties, and go to the Security tab.")
        
        # Open File Explorer
        try:
            os.system("explorer")
            return True
        except Exception as e:
            speak(f"I couldn't open File Explorer. {str(e)}")
            return False

    def create_edit_files(self, query):
        """Create or edit files"""
        query_lower = query.lower()
        
        if "text" in query_lower or "document" in query_lower or "notepad" in query_lower:
            try:
                speak("Opening Notepad")
                os.system("notepad")
                return True
            except Exception as e:
                speak(f"I couldn't open Notepad. {str(e)}")
                return False
                
        elif "word" in query_lower:
            try:
                speak("Opening Microsoft Word")
                os.system("start winword")
                return True
            except Exception as e:
                speak(f"I couldn't open Microsoft Word. {str(e)}")
                return False
                
        elif "excel" in query_lower or "spreadsheet" in query_lower:
            try:
                speak("Opening Microsoft Excel")
                os.system("start excel")
                return True
            except Exception as e:
                speak(f"I couldn't open Microsoft Excel. {str(e)}")
                return False
                
        elif "powerpoint" in query_lower or "presentation" in query_lower:
            try:
                speak("Opening Microsoft PowerPoint")
                os.system("start powerpnt")
                return True
            except Exception as e:
                speak(f"I couldn't open Microsoft PowerPoint. {str(e)}")
                return False
        
        # Default: open Notepad
        try:
            speak("Opening Notepad to create a new file")
            os.system("notepad")
            return True
        except Exception as e:
            speak(f"I couldn't open Notepad. {str(e)}")
            return False

    def file_browsing(self, query):
        """Browse files in specific locations"""
        query_lower = query.lower()
        
        # Common locations
        locations = {
            "document": os.path.join(os.path.expanduser("~"), "Documents"),
            "download": os.path.join(os.path.expanduser("~"), "Downloads"),
            "picture": os.path.join(os.path.expanduser("~"), "Pictures"),
            "music": os.path.join(os.path.expanduser("~"), "Music"),
            "video": os.path.join(os.path.expanduser("~"), "Videos"),
            "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
            "home": os.path.expanduser("~"),
            "c": "C:\\",
            "program": "C:\\Program Files",
            "app": "C:\\Program Files",
        }
        
        # Find which location is mentioned
        for loc_keyword, loc_path in locations.items():
            if loc_keyword in query_lower:
                try:
                    speak(f"Opening {loc_keyword} folder")
                    os.system(f'explorer "{loc_path}"')
                    return True
                except Exception as e:
                    speak(f"I couldn't open {loc_keyword} folder. {str(e)}")
                    return False
        
        # Default: open File Explorer
        try:
            speak("Opening File Explorer")
            os.system("explorer")
            return True
        except Exception as e:
            speak(f"I couldn't open File Explorer. {str(e)}")
            return False


class WebTasks:
    """Handle web-related tasks"""
    def web_browsing(self, query):
        """Handle web browsing commands"""
        query_lower = query.lower()
        
        # Check if a specific URL or website is mentioned
        websites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "github": "https://www.github.com",
            "amazon": "https://www.amazon.com",
            "netflix": "https://www.netflix.com",
            "bing": "https://www.bing.com",
            "yahoo": "https://www.yahoo.com",
            "wikipedia": "https://www.wikipedia.org",
            "reddit": "https://www.reddit.com",
        }
        
        # Check if a specific website is mentioned
        for site in websites:
            if site in query_lower:
                speak(f"Opening {site}")
                webbrowser.open(websites[site])
                return True
        
        # Check if user wants to search for something
        search_keywords = ["search", "look for", "find", "google"]
        for keyword in search_keywords:
            if keyword in query_lower:
                # Extract search term
                query_parts = query_lower.split(keyword)
                if len(query_parts) > 1:
                    search_term = query_parts[1].strip()
                    speak(f"Searching for {search_term}")
                    webbrowser.open(f"https://www.google.com/search?q={quote(search_term)}")
                    return True
        
        # If just general browsing, open default browser
        try:
            speak("Opening your browser")
            webbrowser.open("https://www.google.com")
            return True
        except Exception as e:
            speak(f"I couldn't open the browser. {str(e)}")
            return False


class MediaTasks:
    """Handle media-related tasks"""
    def media_control(self, query):
        """Handle media control commands"""
        query_lower = query.lower()
        
        # Check if user wants to play something specific
        if "play" in query_lower:
            play_term = None
            play_platforms = ["spotify", "youtube", "music"]
            platform = None
            
            # Check if a specific platform is mentioned
            for p in play_platforms:
                if p in query_lower:
                    platform = p
                    break
            
            # Extract play term
            words = query_lower.split()
            play_index = words.index("play") if "play" in words else -1
            
            if play_index >= 0 and play_index + 1 < len(words):
                # Take words after "play" as the play term
                play_term = " ".join(words[play_index+1:])
                
                # Remove platform name from play term if present
                if platform:
                    play_term = play_term.replace(platform, "").strip()
                
                # Remove filler words
                play_term = play_term.replace("some", "").replace("on", "").strip()
            
            # If play term is found, play it
            if play_term:
                if platform == "spotify":
                    try:
                        speak(f"Playing {play_term} on Spotify")
                        # Try to open Spotify with the search
                        webbrowser.open(f"spotify:search:{quote(play_term)}")
                        return True
                    except:
                        try:
                            # Fallback: open in browser
                            webbrowser.open(f"https://open.spotify.com/search/{quote(play_term)}")
                            return True
                        except Exception as e:
                            speak(f"I couldn't play {play_term} on Spotify. {str(e)}")
                            return False
                elif platform == "youtube":
                    try:
                        speak(f"Playing {play_term} on YouTube")
                        webbrowser.open(f"https://www.youtube.com/results?search_query={quote(play_term)}")
                        return True
                    except Exception as e:
                        speak(f"I couldn't play {play_term} on YouTube. {str(e)}")
                        return False
                else:
                    # Default to Windows Media Player
                    try:
                        speak(f"Trying to play {play_term}")
                        subprocess.Popen("wmplayer.exe", shell=True)
                        return True
                    except Exception as e:
                        speak(f"I couldn't play {play_term}. {str(e)}")
                        return False
        
        # Generic media control
        if "pause" in query_lower or "stop" in query_lower:
            pyautogui.press('playpause')
            speak("Media paused")
            return True
        elif "resume" in query_lower or "continue" in query_lower:
            pyautogui.press('playpause')
            speak("Media resumed")
            return True
        elif "next" in query_lower:
            pyautogui.press('nexttrack')
            speak("Next track")
            return True
        elif "previous" in query_lower:
            pyautogui.press('prevtrack')
            speak("Previous track")
            return True
        elif "volume up" in query_lower:
            pyautogui.press('volumeup', presses=5)
            speak("Volume increased")
            return True
        elif "volume down" in query_lower:
            pyautogui.press('volumedown', presses=5)
            speak("Volume decreased")
            return True
        elif "mute" in query_lower:
            pyautogui.press('volumemute')
            speak("Volume muted")
            return True
            
        # Just open media player
        try:
            speak("Opening media player")
            subprocess.Popen("wmplayer.exe", shell=True)
            return True
        except Exception as e:
            speak(f"I couldn't open media player. {str(e)}")
            return False


class NetworkTasks:
    """Handle network-related tasks"""
    def network_management(self, query):
        """Manage network settings"""
        query_lower = query.lower()
        
        if "settings" in query_lower or "preferences" in query_lower:
            try:
                speak("Opening network settings")
                os.system("start ms-settings:network")
                return True
            except Exception as e:
                speak(f"I couldn't open network settings. {str(e)}")
                return False
                
        elif "wifi" in query_lower:
            try:
                speak("Opening Wi-Fi settings")
                os.system("start ms-settings:network-wifi")
                return True
            except Exception as e:
                speak(f"I couldn't open Wi-Fi settings. {str(e)}")
                return False
                
        elif "ethernet" in query_lower:
            try:
                speak("Opening ethernet settings")
                os.system("start ms-settings:network-ethernet")
                return True
            except Exception as e:
                speak(f"I couldn't open ethernet settings. {str(e)}")
                return False
                
        elif "vpn" in query_lower:
            try:
                speak("Opening VPN settings")
                os.system("start ms-settings:network-vpn")
                return True
            except Exception as e:
                speak(f"I couldn't open VPN settings. {str(e)}")
                return False
                
        elif "bluetooth" in query_lower:
            try:
                speak("Opening Bluetooth settings")
                os.system("start ms-settings:bluetooth")
                return True
            except Exception as e:
                speak(f"I couldn't open Bluetooth settings. {str(e)}")
                return False
        
        # Default: open network status
        try:
            speak("Checking network status")
            
            # Get network information
            import socket
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            speak(f"Your computer name is {hostname} and local IP address is {ip_address}")
            
            # Try to get public IP
            try:
                import requests
                public_ip = requests.get('https://api.ipify.org').text
                speak(f"Your public IP address is {public_ip}")
            except:
                pass
            
            # Open network settings
            os.system("start ms-settings:network-status")
            
            return True
        except Exception as e:
            speak(f"I couldn't check network status. {str(e)}")
            return False

    def check_internet_connectivity(self, query):
        """Check internet connectivity"""
        try:
            import socket
            
            # Try to connect to a well-known server
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            
            # Get IP information
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Try to get public IP
            public_ip = "unavailable"
            try:
                import requests
                public_ip = requests.get('https://api.ipify.org', timeout=3).text
            except:
                pass
            
            speak(f"Internet connection is active. Your local IP is {local_ip}, and your public IP is {public_ip}")
            
            return True
        except Exception as e:
            speak("Internet connection appears to be down. Please check your network settings.")
            return False

    def network_troubleshooting(self, query):
        """Troubleshoot network issues"""
        try:
            speak("Running network troubleshooter")
            
            # Run ipconfig /all in command prompt
            os.system("start cmd /k ipconfig /all")
            
            # Also open network troubleshooter
            os.system("msdt.exe /id NetworkDiagnosticsWeb")
            
            return True
        except Exception as e:
            speak(f"I couldn't run network diagnostics. {str(e)}")
            return False