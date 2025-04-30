import os
import sys
import io
import eel
from backend.auth import recoganize
from backend.auth.recoganize import AuthenticateFace
from backend.feature import *
from backend.command import *

# Đặt UTF-8 cho stdout và stderr nếu chưa được đặt trong run.py
if sys.platform.startswith('win') and not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def start():
    # Xác định đường dẫn đến thư mục frontend
    if getattr(sys, 'frozen', False):
        # Nếu đang chạy từ file đã đóng gói
        application_path = os.path.dirname(sys.executable)
        frontend_path = os.path.join(application_path, "frontend")
    else:
        # Nếu đang chạy từ mã nguồn
        application_path = os.path.dirname(os.path.abspath(__file__))
        frontend_path = os.path.join(application_path, "frontend")
    
    # Kiểm tra xem thư mục frontend có tồn tại không
    if not os.path.exists(frontend_path):
        print("CẢNH BÁO: Không tìm thấy thư mục frontend tại:", frontend_path)
        print("Đang tìm kiếm thư mục frontend ở vị trí khác...")
        
        # Tìm kiếm trong thư mục cha
        parent_dir = os.path.dirname(application_path)
        frontend_path_alt = os.path.join(parent_dir, "frontend")
        
        if os.path.exists(frontend_path_alt):
            frontend_path = frontend_path_alt
            print("Đã tìm thấy thư mục frontend tại:", frontend_path)
        else:
            print("LỖI: Không tìm thấy thư mục frontend!")
            return
    
    print("Khởi tạo Eel với thư mục frontend:", frontend_path)
    eel.init(frontend_path)
    
    play_assistant_sound()
    
    @eel.expose
    def init():
        eel.hideLoader()
        speak("Welcome back my Boss")
        speak("Ready for Face Authentication")
        flag = recoganize.AuthenticateFace()
        if flag == 1:
            speak("Face recognized successfully")
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            speak("Welcome to Your Own Assistant")
            eel.hideStart()
            eel.showMainInterface()
            play_assistant_sound()
        else:
            speak("Face not recognized. Please try again")
    
    # Xác định cách khởi động Eel
    # Nếu được gọi từ Electron, không mở trình duyệt
    is_electron = os.environ.get('ELECTRON_RUN') == '1'
    
    if not is_electron:
        # Nếu chạy độc lập, mở trình duyệt
        try:
            print("Khởi động trình duyệt độc lập...")
            os.system('start msedge.exe --app="http://127.0.0.1:8000/index.html"')
        except Exception as e:
            print("Không thể khởi động trình duyệt:", e)
    
    # Khởi động server Eel
    try:
        print("Khởi động server Eel...")
        eel.start("index.html", mode=None, host="localhost", port=8000, block=True)
    except Exception as e:
        print("Lỗi khởi động Eel:", e)
        # Thử lại với cổng khác nếu cổng 8000 bị chiếm
        try:
            eel.start("index.html", mode=None, host="localhost", port=8001, block=True)
        except Exception as e2:
            print("Lỗi khởi động Eel (lần 2):", e2)
            sys.exit(1)
            