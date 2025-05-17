"""
File: backend/auth/face_manager.py
"""
import os
import sys
import cv2
import numpy as np
import shutil
from PIL import Image
import eel
import gc
import subprocess

def get_user_data_dir():
    """Lấy đường dẫn thư mục dữ liệu người dùng cho ứng dụng"""
    if sys.platform.startswith('win'):
        # Trên Windows, sử dụng AppData\Local\Programs\YourAppName
        app_name = "AI-Assistant"
        base_dir = os.path.join(os.environ['LOCALAPPDATA'], app_name)
    else:
        # Trên các hệ điều hành khác
        app_name = ".ai-assistant"
        base_dir = os.path.join(os.path.expanduser("~"), app_name)
    
    # Tạo thư mục nếu chưa tồn tại
    data_dir = os.path.join(base_dir, "face_data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    # Tạo thư mục samples và trainer nếu chưa tồn tại
    samples_dir = os.path.join(data_dir, "samples")
    trainer_dir = os.path.join(data_dir, "trainer")
    
    if not os.path.exists(samples_dir):
        os.makedirs(samples_dir, exist_ok=True)
    
    if not os.path.exists(trainer_dir):
        os.makedirs(trainer_dir, exist_ok=True)
    
    return data_dir

def is_face_id_setup():
    """Kiểm tra xem FaceID đã được thiết lập chưa"""
    data_dir = get_user_data_dir()
    trainer_file = os.path.join(data_dir, "trainer", "trainer.yml")
    samples_dir = os.path.join(data_dir, "samples")
    
    # Kiểm tra xem có file trainer.yml và có ít nhất một ảnh mẫu không
    has_trainer = os.path.exists(trainer_file)
    has_samples = False
    
    if os.path.exists(samples_dir):
        sample_files = [f for f in os.listdir(samples_dir) if f.startswith("face.")]
        has_samples = len(sample_files) > 0
    
    return has_trainer and has_samples

def create_face_id(face_id=1):
    """Tạo FaceID mới cho người dùng"""
    data_dir = get_user_data_dir()
    samples_dir = os.path.join(data_dir, "samples")
    
    # Đảm bảo thư mục samples tồn tại
    if not os.path.exists(samples_dir):
        os.makedirs(samples_dir, exist_ok=True)
    
    # Sử dụng haarcascade từ thư mục gốc
    cascade_file = "backend\\auth\\haarcascade_frontalface_default.xml"
    
    # Đảm bảo đóng tất cả các cửa sổ CV2 và camera trước khi bắt đầu
    cv2.destroyAllWindows()
    for i in range(5):
        cv2.waitKey(1)
    
    # Khởi tạo camera
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cam.isOpened():
        print("Không thể truy cập camera")
        return False
        
    cam.set(3, 640)  # Thiết lập chiều rộng frame
    cam.set(4, 480)  # Thiết lập chiều cao frame
    
    detector = cv2.CascadeClassifier(cascade_file)
    
    count = 0
    
    try:
        while True:
            ret, img = cam.read()
            if not ret:
                print("Không thể đọc frame từ camera")
                break
                
            converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(converted_image, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                count += 1
                
                # Lưu ảnh vào thư mục samples của người dùng
                sample_path = os.path.join(samples_dir, f"face.{face_id}.{count}.jpg")
                cv2.imwrite(sample_path, converted_image[y:y+h, x:x+w])
                
                cv2.imshow('Face ID Setup', img)
            
            # Hiển thị tiến trình
            cv2.putText(img, f"Progress: {count}/30", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Face ID Setup', img)
                
            k = cv2.waitKey(100) & 0xff  # Chờ phím được nhấn
            if k == 27:  # Nhấn ESC để thoát
                break
            elif count >= 30:  # Lấy 30 mẫu
                break
    finally:
        # Đảm bảo đóng camera và cửa sổ
        cam.release()
        cv2.destroyAllWindows()
        for i in range(5):
            cv2.waitKey(1)
    
    # Thực hiện huấn luyện mô hình
    if count > 0:
        train_model()
        return True
    return False

def train_model():
    """Huấn luyện mô hình nhận diện khuôn mặt từ các mẫu"""
    data_dir = get_user_data_dir()
    samples_dir = os.path.join(data_dir, "samples")
    trainer_dir = os.path.join(data_dir, "trainer")
    
    # Đảm bảo thư mục trainer tồn tại
    if not os.path.exists(trainer_dir):
        os.makedirs(trainer_dir, exist_ok=True)
    
    # Sử dụng haarcascade từ thư mục gốc
    cascade_file = "backend\\auth\\haarcascade_frontalface_default.xml"
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(cascade_file)
    
    # Hàm để lấy ảnh và nhãn
    def get_images_and_labels(directory):
        image_paths = [os.path.join(directory, f) for f in os.listdir(directory) if f.startswith("face.")]
        face_samples = []
        ids = []
        
        for image_path in image_paths:
            try:
                pil_img = Image.open(image_path).convert('L')  # Chuyển đổi sang grayscale
                img_array = np.array(pil_img, 'uint8')
                
                # Lấy id từ tên file (face.ID.count.jpg)
                id = int(os.path.split(image_path)[-1].split(".")[1])
                faces = detector.detectMultiScale(img_array)
                
                for (x, y, w, h) in faces:
                    face_samples.append(img_array[y:y+h, x:x+w])
                    ids.append(id)
            except Exception as e:
                print(f"Lỗi khi xử lý ảnh {image_path}: {e}")
        
        return face_samples, ids
    
    print("Đang huấn luyện mô hình nhận diện khuôn mặt...")
    
    faces, ids = get_images_and_labels(samples_dir)
    
    if len(faces) == 0 or len(ids) == 0:
        print("Không có đủ dữ liệu để huấn luyện")
        return False
    
    recognizer.train(faces, np.array(ids))
    
    # Lưu mô hình đã huấn luyện
    model_path = os.path.join(trainer_dir, "trainer.yml")
    recognizer.write(model_path)
    
    print(f"Đã huấn luyện mô hình với {len(faces)} mẫu khuôn mặt")
    return True

def authenticate_face():
    """Xác thực khuôn mặt người dùng sử dụng mô hình đã huấn luyện"""
    data_dir = get_user_data_dir()
    trainer_file = os.path.join(data_dir, "trainer", "trainer.yml")
    
    # Kiểm tra nếu chưa có mô hình được huấn luyện
    if not os.path.exists(trainer_file):
        print("Chưa thiết lập FaceID")
        return 0
    
    # Khởi tạo recognizer và load mô hình
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(trainer_file)
    
    # Sử dụng haarcascade từ thư mục gốc
    cascade_file = "backend\\auth\\haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascade_file)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # ID của người dùng (mặc định là 1)
    id = 1
    names = ['', 'User']  # index 0 để trống, 1 là User
    
    # Đảm bảo đóng tất cả các cửa sổ CV2 và camera trước khi bắt đầu
    cv2.destroyAllWindows()
    for i in range(5):
        cv2.waitKey(1)
    
    # Thêm độ trễ để đảm bảo camera đã được giải phóng hoàn toàn
    import time
    time.sleep(2)  # Tăng thời gian chờ lên 2 giây
    
    # Khởi tạo biến camera
    cam = None
    
    try:
        # Khởi tạo camera với thử nhiều lần
        camera_success = False
        for attempt in range(5):  # Tăng số lần thử lên 5
            try:
                print(f"Đang thử khởi tạo camera... (lần {attempt+1})")
                # Đảm bảo camera được giải phóng trước khi khởi tạo lại
                if cam is not None:
                    cam.release()
                    time.sleep(1)  # Tăng thời gian chờ lên 1 giây
                
                # Thử khởi tạo camera với các tham số khác nhau
                if attempt % 2 == 0:
                    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                else:
                    cam = cv2.VideoCapture(0)
                
                # Kiểm tra xem camera đã được mở thành công chưa
                if cam.isOpened():
                    # Thử đọc một frame để kiểm tra camera hoạt động
                    ret, _ = cam.read()
                    if ret:
                        camera_success = True
                        break
                    else:
                        cam.release()
                        time.sleep(1)
                else:
                    # Đóng camera và thử lại
                    cam.release()
                    time.sleep(1)
            except Exception as e:
                print(f"Lỗi khi khởi tạo camera (thử lần {attempt+1}): {e}")
                time.sleep(1)
        
        if not camera_success:
            print("Không thể khởi tạo camera sau nhiều lần thử")
            return 0
            
        # Thiết lập kích thước frame
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Kích thước tối thiểu để nhận diện là khuôn mặt
        minW = 0.1 * cam.get(3)
        minH = 0.1 * cam.get(4)
        
        # Ngưỡng độ chính xác
        accuracy_threshold = 45
        
        flag = 0
        
        # Bộ đếm thời gian để tránh vòng lặp vô hạn
        start_time = time.time()
        max_time = 30  # Tối đa 30 giây
        
        confirmation_count = 0  # Số lần nhận diện thành công liên tiếp
        last_recognition_time = time.time()  # Thời gian nhận diện thành công cuối cùng
        
        while True:
            # Kiểm tra thời gian
            current_time = time.time()
            if current_time - start_time > max_time:
                print("Đã vượt quá thời gian tối đa cho xác thực")
                break
                
            # Kiểm tra nếu camera vẫn mở
            if not cam.isOpened():
                print("Camera đã bị đóng")
                break
                
            ret, img = cam.read()
            if not ret:
                print("Không thể đọc frame từ camera")
                break
                
            converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                converted_image,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(int(minW), int(minH))
            )
            
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                id, confidence = recognizer.predict(converted_image[y:y+h, x:x+w])
                
                # Kiểm tra độ chính xác
                if confidence < accuracy_threshold:
                    id = names[id]
                    confidence = f"{100 - confidence:.2f}%"
                    
                    # Tăng bộ đếm xác nhận
                    confirmation_count += 1
                    last_recognition_time = time.time()
                    
                    # Nếu đã xác nhận đủ số lần liên tiếp
                    if confirmation_count >= 3:
                        flag = 1
                        break
                else:
                    id = "unknown"
                    confidence = f"{100 - confidence:.2f}%"
                    confirmation_count = 0
                
                cv2.putText(img, str(id), (x+5, y-5), font, 1, (255, 255, 255), 2)
                cv2.putText(img, str(confidence), (x+5, y+h-5), font, 1, (255, 255, 0), 1)
            
            # Kiểm tra nếu đã xác thực thành công
            if flag == 1:
                break
                
            # Kiểm tra nếu đã quá lâu kể từ lần nhận diện thành công cuối
            if time.time() - last_recognition_time > 5:
                confirmation_count = 0
            
            cv2.imshow('Face Authentication', img)
            
            k = cv2.waitKey(10) & 0xff
            if k == 27:
                break
    finally:
        # Đảm bảo đóng camera và cửa sổ
        if cam is not None:
            cam.release()
        cv2.destroyAllWindows()
        for i in range(5):
            cv2.waitKey(1)
        
        # Thêm độ trễ để đảm bảo camera đã được giải phóng hoàn toàn
        time.sleep(2)  # Tăng thời gian chờ lên 2 giây
    
    return flag

def remove_face_id():
    """Xóa dữ liệu FaceID đã lưu"""
    data_dir = get_user_data_dir()
    
    try:
        # Xóa thư mục samples
        samples_dir = os.path.join(data_dir, "samples")
        if os.path.exists(samples_dir):
            shutil.rmtree(samples_dir)
            os.makedirs(samples_dir, exist_ok=True)
        
        # Xóa file trainer.yml
        trainer_file = os.path.join(data_dir, "trainer", "trainer.yml")
        if os.path.exists(trainer_file):
            os.remove(trainer_file)
        
        return True
    except Exception as e:
        print(f"Lỗi khi xóa FaceID: {e}")
        return False

@eel.expose
def restart_application():
    print("==> restart_application CALLED")
    try:
        gc.collect()
        python = sys.executable
        current_script = os.path.abspath(__file__)
        print(f"Restarting with: {python} {current_script}")
        subprocess.Popen([python, current_script], creationflags=subprocess.CREATE_NEW_CONSOLE)
        print("==> Subprocess started, exiting main app...")
        sys.exit(0)
        return True
    except Exception as e:
        print(f"Lỗi khi khởi động lại: {e}")
        return False

if __name__ == "__main__":
    eel.init('frontend')
    eel.start('index.html', size=(1000, 700))