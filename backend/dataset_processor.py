import os
import csv
import sqlite3
from backend.command import speak

class DatasetProcessor:
    def __init__(self, db_path="jarvis.db"):
        """Khởi tạo bộ xử lý dataset với đường dẫn tới file cơ sở dữ liệu"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._ensure_tables_exist()
        
    def _ensure_tables_exist(self):
        """Đảm bảo bảng command_dataset tồn tại"""
        query = """
        CREATE TABLE IF NOT EXISTS command_dataset(
            id INTEGER PRIMARY KEY,
            task_intent VARCHAR(100),
            command_text VARCHAR(500),
            function_name VARCHAR(100),
            parameters TEXT,
            count INTEGER DEFAULT 1,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(query)
        self.conn.commit()
        
    def import_all_datasets(self, dataset_folder):
        """Import tất cả các file dataset trong thư mục"""
        if not os.path.exists(dataset_folder):
            print(f"Thư mục {dataset_folder} không tồn tại")
            return 0
            
        total_imported = 0
        for file in os.listdir(dataset_folder):
            if file.endswith('.csv'):
                file_path = os.path.join(dataset_folder, file)
                imported = self.import_dataset(file_path)
                total_imported += imported
                print(f"Đã import {imported} lệnh từ {file}")
                
        return total_imported
    
    def import_dataset(self, csv_path):
        """Import một file dataset CSV cụ thể"""
        if not os.path.exists(csv_path):
            print(f"File {csv_path} không tồn tại")
            return 0
            
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                counter = 0
                
                for row in reader:
                    # Xử lý theo định dạng của Kaggle dataset
                    if 'Task/Intent' in row and 'command' in row:
                        task = row['Task/Intent']
                        command = row['command']
                        
                        # Tạo tên hàm từ task
                        function_name = task.lower().replace(' ', '_')
                        
                        # Kiểm tra lệnh đã tồn tại chưa
                        self.cursor.execute(
                            "SELECT id FROM command_dataset WHERE command_text = ?",
                            (command,)
                        )
                        if not self.cursor.fetchone():
                            # Chèn lệnh mới
                            self.cursor.execute(
                                "INSERT INTO command_dataset (task_intent, command_text, function_name) VALUES (?, ?, ?)",
                                (task, command, function_name)
                            )
                            counter += 1
                
                self.conn.commit()
                return counter
        except Exception as e:
            print(f"Lỗi khi import dataset: {e}")
            return 0
            
    def get_command_counts(self):
        """Lấy số lượng lệnh theo từng loại task"""
        self.cursor.execute(
            "SELECT task_intent, COUNT(*) FROM command_dataset GROUP BY task_intent"
        )
        return self.cursor.fetchall()
        
    def __del__(self):
        """Đóng kết nối khi đối tượng bị hủy"""
        if hasattr(self, 'conn'):
            self.conn.close()