"""
MiroFish Backend startup entry point
"""

import os
import sys

# Giải quyết vấn đề ký tự lộn xộn trên console Windows: thiết lập mã hóa UTF-8 trước tất cả import
if sys.platform == 'win32':
    # Thiết lập biến môi trường để đảm bảo Python sử dụng UTF-8
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    # Định cấu hình lại luồng đầu ra tiêu chuẩn thành UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Thêm thư mục gốc dự án vào đường dẫn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config import Config


def main():
    """Hàm chính"""
    # Kiểm tra cấu hình
    errors = Config.validate()
    if errors:
        print("Lỗi cấu hình:")
        for err in errors:
            print(f"  - {err}")
        print("\nVui lòng kiểm tra cấu hình trong tệp .env")
        sys.exit(1)

    # Tạo ứng dụng
    app = create_app()

    # Lấy cấu hình chạy
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5001))
    debug = Config.DEBUG

    # Khởi chạy dịch vụ
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    main()

