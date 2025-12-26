# LeafGuard: Hệ thống Phân loại Bệnh Cây từ Ảnh Lá

## Tổng quan Dự án

**1. AI Problem Definition:**
- Ý tưởng AI : Phân loại bệnh cây từ ảnh lá cây (Nhận diện bệnh cây)
Phát hiện bệnh cây giúp nông dân chẩn đoán sớm → tăng năng suất, giảm chi phí.
Đây là một trong những ứng dụng AI phổ biến nhất trong nông nghiệp thông minh (AgriTech).

**2. Problem Statement & Research Question:**
- Problem Statement :
   Bệnh trên lá cây là một trong những nguyên nhân gây suy giảm năng suất và chất lượng nông sản, đặc biệt tại các khu vực nông nghiệp quy mô nhỏ. Việc phát hiện bệnh chủ yếu dựa vào quan sát thủ công của nông dân, vốn dễ nhầm lẫn, tốn thời gian và phụ thuộc nhiều vào kinh nghiệm cá nhân. Điều này dẫn đến chẩn đoán chậm trễ, sử dụng sai thuốc và thiệt hại kinh tế đáng kể.
   Dự án này nhằm xây dựng một mô hình học sâu có khả năng nhận diện và phân loại bệnh cây dựa trên hình ảnh lá, giúp tự động hóa quá trình chẩn đoán, hỗ trợ nông dân phát hiện bệnh sớm và đưa ra quyết định xử lý kịp thời. Mục tiêu là phát triển một giải pháp AI có độ chính xác cao, dễ triển khai và phù hợp với điều kiện thực tế của lĩnh vực nông nghiệp.

Dự án LeaffGuard sử dụng mô hình Học Sâu (Deep Learning) **MobileNetV2** (áp dụng Transfer Learning) để tự động nhận diện và phân loại bệnh dựa trên hình ảnh lá cây. Mục tiêu cuối cùng là cung cấp một giải pháp chẩn đoán sớm, chính xác, dễ dàng triển khai trên thiết bị di động (sử dụng TFLite) để hỗ trợ nông dân nâng cao năng suất cây trồng.

**Mục tiêu Chính:** Xây dựng mô hình phân loại đa lớp (38 Class) đạt **F1-Score trên 90%** trên tập dữ liệu kiểm thử.

-----

## Tính năng & Kết quả mong đợi

  * **Phân loại Ảnh Lá:** Nhận diện và phân loại 38 lớp (loại cây và bệnh) khác nhau từ dataset PlantVillage.
  * **Transfer Learning:** Sử dụng kiến trúc **MobileNetV2** đã được huấn luyện trước trên ImageNet để đạt độ chính xác cao trong thời gian huấn luyện ngắn.
  * **Tối ưu hóa Mobile:** Chuyển đổi mô hình sang định dạng **TensorFlow Lite (TFLite)** và áp dụng **Quantization** để giảm kích thước và tăng tốc độ suy luận, chuẩn bị cho việc triển khai trên thiết bị di động.
  * **Tài liệu Hóa:** Cung cấp đầy đủ **Data Pipeline Flowchart** và **Model Architecture Diagram** trong thư mục `docs/`.

-----

## Công nghệ và Thư viện (Technologies)

| Lĩnh vực | Công nghệ | Mục đích |
| :--- | :--- | :--- |
| **Model Development** | TensorFlow, Keras | Xây dựng, huấn luyện và quản lý mô hình Deep Learning. |
| **Data Processing** | NumPy, Pandas, Matplotlib | Tiền xử lý dữ liệu, Data Augmentation và trực quan hóa kết quả. |
| **Model Optimization** | TensorFlow Lite (TFLite) | Tối ưu hóa mô hình cho triển khai trên thiết bị di động (RQ4). |
| **Version Control** | Git, GitHub | Cộng tác nhóm, theo dõi lịch sử và quản lý mã nguồn. |

-----

## Cấu trúc Dự án (Repository Structure)
(có thể thay đổi trong quá trình làm dự án)

```
LeafGuard/
├── data/                  # Chứa dữ liệu (Raw và Processed - Bỏ qua trên Git)
├── notebooks/             # Quy trình làm việc (.ipynb) theo thứ tự 1-2-3
├── src/                   # Source code Python có thể tái sử dụng
├── models/                # Mô hình đã train (.h5) và tối ưu hóa (.tflite)
├── docs/                  # Tài liệu và Sơ đồ quan trọng
├── README.md              # File bạn đang đọc
└── requirements.txt       # Danh sách dependencies
```

-----

## Dữ liệu (Dataset)

Dự án sử dụng bộ dữ liệu PlantVillage để huấn luyện và kiểm thử mô hình.

  * **Nguồn:** Kaggle PlantVillage Dataset (phiên bản đã chọn lọc).
  * **Tiền xử lý:** Tất cả ảnh được Resize về **224x224**, Normalization, và sử dụng các kỹ thuật **Augmentation** để tăng tính đa dạng.
  * **Chia tập:** Dữ liệu được chia **70/15/15** (Train/Validation/Test) và được cân bằng lớp (Class Balancing) qua Oversampling.

### Link Tải Dữ liệu

Do kích thước lớn, dữ liệu được lưu trữ ngoài GitHub. Vui lòng tải về và giải nén vào thư mục `data/` trước khi chạy Notebook:

  * **[Link]**

-----

## Hướng dẫn Chạy dự án

Thực hiện theo các bước sau để thiết lập môi trường và tái tạo kết quả của dự án:

### 1\. Yêu cầu Tiên quyết (Prerequisites)

  * Node.js (nếu sử dụng công cụ frontend)
  * Python 3.8+
  * Git

### 2\. Nhân bản Repository

```bash
# Clone dự án về máy
$ git clone https://github.com/YourUsername/LeafGuard.git
$ cd LeafGuard
```

### 3\. Cài đặt Thư viện

Sử dụng file `requirements.txt` để cài đặt tất cả các dependencies cần thiết:

```bash
$ pip install -r requirements.txt
```
(to be continue)

### tạo file .env để tạo kết nối với database
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Your_password
DB_NAME=leafguard_db
```
   git pull
   python database/init_db.py  # Tự động cập nhật
-----

## 👥 Nhóm Phát triển (Team)

| Thành viên | Nhiệm vụ chính |
| :--- | :--- |
| **Trương Tuyết Trinh** |  |
| **Trần Bảo Nhi** |  |
| **Phan Thị Thùy Nhung** |  |
| **Nguyễn Hoàng Thanh Trâm** |  |

-----

