import multiprocessing
import os
import sys
import signal
import time
import io
from bottle import route, run, static_file, response

# Đặt UTF-8 cho stdout và stderr để hỗ trợ in ký tự Unicode tiếng Việt
if sys.platform.startswith('win'):
    # Chỉ thực hiện trên Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Thêm thư mục gốc vào sys.path để tìm các module
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Dừng các quy trình khi nhận tín hiệu dừng
def signal_handler(sig, frame):
    print("Đang dừng JARVIS...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Kiểm tra xem server có hoạt động không
@route('/is_alive')
def is_alive():
    response.headers['Content-Type'] = 'application/json'
    return '{"status": "ok"}'

def startJarvis():
    print("Process 1 Starting...")
    from main import start
    start()

def listenHotword():
    print("Process 2 Starting...")
    from backend.feature import hotword
    hotword()

def initialize_datasets():
    """Khởi tạo và import datasets khi khởi động"""
    try:
        # Thêm đường dẫn gốc của dự án vào sys.path nếu cần
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from backend.dataset_processor import DatasetProcessor
        
        # Tạo thư mục datasets nếu chưa có
        datasets_folder = os.path.join(os.path.dirname(__file__), "datasets")
        if not os.path.exists(datasets_folder):
            os.makedirs(datasets_folder)
            print("Đã tạo thư mục datasets tại:", datasets_folder)
        
        # Kiểm tra xem dataset đã được import chưa
        processor = DatasetProcessor()
        processor.cursor.execute("SELECT COUNT(*) FROM command_dataset")
        count = processor.cursor.fetchone()[0]
        
        if count == 0:
            print("Bắt đầu import datasets...")
            # Import tất cả file CSV trong thư mục datasets
            imported = processor.import_all_datasets(datasets_folder)
            print("Đã import tổng cộng", imported, "lệnh từ các datasets")
        else:
            print("Đã có", count, "lệnh trong cơ sở dữ liệu. Bỏ qua import.")
    except Exception as e:
        print("Lỗi khi khởi tạo dataset:", e)
        # Không làm chương trình dừng lại nếu gặp lỗi dataset
        pass

def initialize_face_auth():
    """Khởi tạo các thư mục cần thiết cho FaceID"""
    try:
        from backend.auth.face_manager import get_user_data_dir
        
        # Đảm bảo thư mục dữ liệu người dùng đã được tạo
        data_dir = get_user_data_dir()
        print("Đã khởi tạo thư mục dữ liệu FaceID tại:", data_dir)
    except Exception as e:
        print("Lỗi khi khởi tạo thư mục FaceID:", e)
        pass

if __name__ == "__main__":
    # Xác định chế độ đang chạy (development hoặc production)
    is_frozen = getattr(sys, 'frozen', False)
    
    # Đảm bảo các đường dẫn hoạt động cho cả hai chế độ
    if is_frozen:
        # Nếu đang chạy từ file đã đóng gói
        application_path = os.path.dirname(sys.executable)
    else:
        # Nếu đang chạy từ mã nguồn
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Di chuyển đến thư mục gốc của ứng dụng
    os.chdir(application_path)
    
    # Khởi tạo datasets và thư mục FaceID
    initialize_datasets()
    initialize_face_auth()

    # Khởi động các quy trình
    process1 = multiprocessing.Process(target=startJarvis)
    process2 = multiprocessing.Process(target=listenHotword)
    
    process1.start()
    process2.start()
    
    # Đợi process1 kết thúc
    process1.join()
    
    # Kết thúc process2 nếu nó vẫn đang chạy
    if process2.is_alive():
        process2.terminate()
        print("Process 2 terminated.")
        process2.join()
    
    print("System is terminated.")