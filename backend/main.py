import eel
import cv2
import sys
import os
import gc
import psutil
import subprocess

@eel.expose
def restart_application():
    """Khởi động lại ứng dụng"""
    try:
        # Đóng tất cả các cửa sổ CV2
        cv2.destroyAllWindows()
        for i in range(5):
            cv2.waitKey(1)
        
        # Giải phóng tất cả tài nguyên
        gc.collect()
        
        # Lấy đường dẫn hiện tại của script
        current_script = os.path.abspath(__file__)
        
        # Lấy đường dẫn Python
        python = sys.executable
        
        # Tạo lệnh để khởi động lại ứng dụng
        if sys.platform.startswith('win'):
            # Trên Windows
            subprocess.Popen([python, current_script], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # Trên Linux/Mac
            subprocess.Popen([python, current_script])
        
        # Thoát ứng dụng hiện tại
        eel.close_window()
        sys.exit(0)
    except Exception as e:
        print(f"Lỗi khi khởi động lại: {e}")
        return False
    return True 