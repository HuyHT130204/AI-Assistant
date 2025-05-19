import os
import sys
import io
import eel
from backend.auth.face_manager import is_face_id_setup, create_face_id, authenticate_face
from backend.feature import *
from backend.command import *
from threading import Thread
from backend.settings import get_welcome_message
import cv2
import gc
import psutil
import subprocess

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
        welcome_message = get_welcome_message()
        speak(welcome_message)
        
        # Kiểm tra FaceID ngay lập tức
        face_id_exists = check_face_id_exists()
        
        if face_id_exists:
            print("FaceID đã được thiết lập, chuyển sang xác thực")
            speak("Ready for Face Authentication")
            # Đảm bảo dialog setup đã được ẩn
            eel.hideFaceIdSetupDialog()
            # Tiến hành xác thực
            authenticate_user()
        else:
            print("FaceID chưa được thiết lập, hiển thị hộp thoại thiết lập")
            speak("Face ID setup required")
            # Chỉ hiển thị dialog sau khi đã kiểm tra xong
            eel.showFaceIdSetupDialog()
    
    @eel.expose
    def check_face_id_exists():
        """Kiểm tra xem đã tồn tại dữ liệu FaceID hay chưa"""
        # Kiểm tra dựa trên hàm có sẵn
        from backend.auth.face_manager import is_face_id_setup
        
        setup_flag = is_face_id_setup()
        
        # Thêm kiểm tra thủ công các file mẫu
        if not setup_flag:
            # Kiểm tra trực tiếp thư mục samples
            base_dir = get_user_data_dir()
            sample_dir = os.path.join(base_dir, "face_data", "samples")
            trainer_file = os.path.join(base_dir, "face_data", "trainer", "trainer.yml")
            
            if os.path.exists(sample_dir) and os.path.exists(trainer_file):
                # Kiểm tra xem có file ảnh nào trong thư mục không
                files = [f for f in os.listdir(sample_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
                if files and os.path.getsize(trainer_file) > 0:
                    setup_flag = True
                    print(f"Tìm thấy {len(files)} mẫu FaceID và file huấn luyện")
        
        return setup_flag
    
    def get_user_data_dir():
        """Lấy đường dẫn thư mục dữ liệu người dùng cho ứng dụng"""
        if sys.platform.startswith('win'):
            # Trên Windows, sử dụng AppData\Local\AI-Assistant
            app_name = "AI-Assistant"
            base_dir = os.path.join(os.environ['LOCALAPPDATA'], app_name)
        else:
            # Trên các hệ điều hành khác
            app_name = ".ai-assistant"
            base_dir = os.path.join(os.path.expanduser("~"), app_name)
        
        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
        
        return base_dir
    
    @eel.expose
    def authenticate_user():
        """Xác thực người dùng bằng FaceID"""
        # Kiểm tra xem có thread xác thực nào đang chạy không
        import threading
        
        for thread in threading.enumerate():
            if thread.name == "face_auth_thread":
                print("Đã có một phiên xác thực đang chạy, bỏ qua yêu cầu mới")
                return False
        
        def auth_thread():
            import cv2
            # Chờ một chút để UI được cập nhật
            import time
            time.sleep(0.2)
            
            # Đóng tất cả các cửa sổ CV2 nếu có
            cv2.destroyAllWindows()
            for i in range(5):
                cv2.waitKey(1)
            
            flag = authenticate_face()
            if flag == 1:
                speak("Face recognized successfully")
                speak("Welcome to Your Own Assistant")
                
                # Đảm bảo đóng các cửa sổ CV2 còn sót lại
                cv2.destroyAllWindows()
                for i in range(5):
                    cv2.waitKey(1)
                
                # Chờ đủ thời gian để CV2 đóng hoàn toàn
                time.sleep(0.3)
                
                # Thực hiện cập nhật UI với mức độ ưu tiên cao
                eel.hideStart()
                eel.showMainInterface()
                play_assistant_sound()
            else:
                speak("Face not recognized. Please try again")
                speak("Authentication required to access the system")
                eel.showAuthFailedDialog()
        
        # Khởi động thread xác thực
        thread = Thread(target=auth_thread, name="face_auth_thread")
        thread.daemon = True
        thread.start()
        
        return True
    
    @eel.expose
    def setup_face_id():
        """Thiết lập FaceID cho người dùng"""
        # Thực hiện việc thiết lập FaceID trong một thread riêng để không block UI
        def setup_thread():
            success = create_face_id()
            if success:
                # Báo cho frontend biết việc thiết lập đã hoàn thành thành công
                eel.onFaceIdSetupComplete(True)
            else:
                # Báo lỗi nếu việc thiết lập thất bại
                eel.onFaceIdSetupComplete(False)
        
        # Khởi động thread
        thread = Thread(target=setup_thread)
        thread.daemon = True
        thread.start()
        
        return True
    
    @eel.expose
    def skip_face_id_setup():
        """Bỏ qua việc thiết lập FaceID"""
        # Người dùng không thể bỏ qua việc thiết lập FaceID
        # và vào trực tiếp hệ thống
        speak("Face ID setup is required for security reasons")
        # Hiển thị thông báo yêu cầu thiết lập FaceID
        eel.showRequiredFaceIdDialog()
        return False
    
    @eel.expose
    def retry_authentication():
        """Thử lại xác thực FaceID"""
        # Kiểm tra xem có thread xác thực nào đang chạy không
        import threading
        
        for thread in threading.enumerate():
            if thread.name == "face_auth_thread":
                print("Đã có một phiên xác thực đang chạy, bỏ qua yêu cầu thử lại")
                return False
        
        speak("Retrying Face Authentication")
        eel.hideAuthFailedDialog()
        
        # Đảm bảo đóng tất cả các cửa sổ CV2 trước khi thử lại
        import cv2
        cv2.destroyAllWindows()
        for i in range(5):
            cv2.waitKey(1)
        
        # Chờ một chút trước khi thử lại
        import time
        time.sleep(0.3)
        
        # Gọi hàm xác thực
        authenticate_user()
        return True
    
    @eel.expose
    def exit_application():
        """Thoát khỏi ứng dụng"""
        speak("Goodbye, have a nice day!")
        sys.exit(0)
    
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