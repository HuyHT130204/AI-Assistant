import os
import sys
import eel
from threading import Thread

@eel.expose
def check_face_id_exists():
    """Kiểm tra xem đã tồn tại dữ liệu FaceID hay chưa"""
    from backend.auth.face_manager import is_face_id_setup
    
    # Kiểm tra thực sự xem có dữ liệu mẫu khuôn mặt trong thư mục hay không
    # thay vì chỉ dựa vào hàm is_face_id_setup đơn thuần
    exists = is_face_id_setup()
    
    # Thêm kiểm tra thủ công các file mẫu nếu cần thiết
    if not exists:
        # Kiểm tra trực tiếp thư mục samples
        base_dir = get_user_data_dir()
        sample_dir = os.path.join(base_dir, "face_data", "samples")
        
        if os.path.exists(sample_dir):
            # Kiểm tra xem có file ảnh nào trong thư mục không
            files = [f for f in os.listdir(sample_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
            if files:
                exists = True
                print(f"Tìm thấy {len(files)} mẫu FaceID đã tồn tại")
    
    return exists

@eel.expose
def show_face_id_setup_dialog():
    """Hiển thị hộp thoại yêu cầu thiết lập FaceID"""
    # Chỉ hiển thị nếu chưa có mẫu FaceID
    if not check_face_id_exists():
        return True
    else:
        # Nếu đã có mẫu, chuyển qua xác thực luôn
        authenticate_user()
        return False

@eel.expose
def setup_face_id():
    """Thiết lập FaceID cho người dùng"""
    from backend.auth.face_manager import create_face_id, train_model
    
    # Thực hiện việc thiết lập FaceID trong một thread riêng để không block UI
    def setup_thread():
        success = create_face_id()
        if success:
            # Báo cho frontend biết việc thiết lập đã hoàn thành thành công
            # Đăng ký là đây là lần đầu thiết lập để vào thẳng hệ thống
            _mark_first_setup_complete()
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
    # Không cho phép bỏ qua thiết lập FaceID
    eel.showRequiredFaceIdDialog()
    return False

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

def _mark_first_setup_complete():
    """Đánh dấu đây là lần đầu thiết lập FaceID thành công"""
    # Tạo file đánh dấu để biết đây là lần đầu thiết lập
    base_dir = get_user_data_dir()
    flag_file = os.path.join(base_dir, "first_setup.flag")
    with open(flag_file, "w") as f:
        f.write("1")

def _is_first_setup():
    """Kiểm tra xem đây có phải là lần đầu thiết lập FaceID không"""
    base_dir = get_user_data_dir()
    flag_file = os.path.join(base_dir, "first_setup.flag")
    
    # Nếu file tồn tại, đọc giá trị
    if os.path.exists(flag_file):
        with open(flag_file, "r") as f:
            value = f.read().strip()
            # Xóa file sau khi đọc để những lần sau không còn là lần đầu nữa
            os.remove(flag_file)
            return value == "1"
    
    return False

@eel.expose
def authenticate_user():
    """Xác thực người dùng bằng FaceID từ dialogs.py"""
    from backend.auth.face_manager import authenticate_face
    
    # Chạy duy nhất một phiên xác thực cùng lúc
    import threading
    
    # Kiểm tra xem có thread xác thực nào đang chạy không
    for thread in threading.enumerate():
        if thread.name == "face_auth_thread":
            print("Đã có một phiên xác thực đang chạy, bỏ qua yêu cầu mới")
            return False
    
    # Thực hiện việc xác thực FaceID trong một thread riêng
    def auth_thread():
        try:
            # Thêm một khoảng dừng nhỏ để đảm bảo UI đã được cập nhật
            import time
            time.sleep(0.2)
            
            # Gọi hàm xác thực
            flag = authenticate_face()
            
            if flag == 1:
                # Xác thực thành công
                # Đảm bảo đóng các cửa sổ CV2 còn sót lại
                import cv2
                cv2.destroyAllWindows()
                for i in range(5):
                    cv2.waitKey(1)
                
                # Cập nhật UI
                eel.hideStart()
                eel.showMainInterface()
            else:
                # Xác thực thất bại
                eel.showAuthFailedDialog()
                
        except Exception as e:
            print(f"Lỗi khi xác thực: {e}")
            eel.showAuthFailedDialog()
    
    # Khởi động thread với tên xác định để kiểm soát
    thread = Thread(target=auth_thread, name="face_auth_thread")
    thread.daemon = True
    thread.start()
    
    return True

@eel.expose
def retry_authentication():
    """Thử lại xác thực FaceID"""
    # Ẩn dialog thông báo thất bại trước
    eel.hideAuthFailedDialog()
    # Gọi lại hàm xác thực
    authenticate_user()
    return True