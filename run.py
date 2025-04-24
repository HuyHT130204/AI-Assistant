import multiprocessing
import os

def startJarvis():
    print ("Process 1 Starting...")
    from main import start
    start()
    
def listenHotword():
    print ("Process 2 Starting...")
    from backend.feature import hotword
    hotword()
    
# Thêm đoạn code sau vào hàm main hoặc nơi khởi động ứng dụng
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
            print(f"Đã tạo thư mục datasets tại: {datasets_folder}")
            
        # Kiểm tra xem dataset đã được import chưa
        processor = DatasetProcessor()
        processor.cursor.execute("SELECT COUNT(*) FROM command_dataset")
        count = processor.cursor.fetchone()[0]
        
        if count == 0:
            print("Bắt đầu import datasets...")
            # Import tất cả file CSV trong thư mục datasets
            imported = processor.import_all_datasets(datasets_folder)
            print(f"Đã import tổng cộng {imported} lệnh từ các datasets")
        else:
            print(f"Đã có {count} lệnh trong cơ sở dữ liệu. Bỏ qua import.")
    except Exception as e:
        print(f"Lỗi khi khởi tạo dataset: {e}")
        # Không làm chương trình dừng lại nếu gặp lỗi dataset
        pass

if __name__ == "__main__":
    # Di chuyển initialize_datasets ra khỏi khối if __main__ để tránh lỗi khi import
    initialize_datasets()
    
    process1 = multiprocessing.Process(target=startJarvis)
    process2 = multiprocessing.Process(target=listenHotword)
    process1.start()
    process2.start()
    process1.join()
    
    if process2.is_alive():
        process2.terminate()
        print("Process 2 terminated.")
        process2.join()
        
    print("System is terminated.")