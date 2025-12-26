# 🔥 Firebase Setup Guide

## Bước 1: Tạo Firebase Project

1. Truy cập [Firebase Console](https://console.firebase.google.com/)
2. Đăng nhập bằng tài khoản Google
3. Click **"Add project"** (Thêm dự án)
4. Đặt tên project: `ai-leafguard` (hoặc tên bạn muốn)
5. Click **Continue**
6. Tắt Google Analytics (hoặc bật nếu muốn)
7. Click **"Create project"**
8. Đợi ~30 giây
9. Click **"Continue"**

## Bước 2: Enable Authentication

1. Trong Firebase Console, click **"Authentication"** ở menu bên trái
2. Click **"Get started"**
3. Chọn tab **"Sign-in method"**
4. Enable **Email/Password**:
   - Click vào "Email/Password"
   - Toggle "Enable" → Save
5. (Optional) Enable **Google Sign-In** nếu muốn

## Bước 3: Enable Firestore Database

1. Click **"Firestore Database"** ở menu bên trái
2. Click **"Create database"**
3. Chọn **"Start in test mode"** (dễ dàng cho development)
4. Chọn location: **`asia-southeast1`** (Singapore - gần VN)
5. Click **"Enable"**
6. Đợi database được tạo

## Bước 4: Tạo Service Account Key

1. Click icon ⚙️ (Settings) → **"Project settings"**
2. Chọn tab **"Service accounts"**
3. Click **"Generate new private key"**
4. Click **"Generate key"** để confirm
5. File JSON sẽ được download về máy

## Bước 5: Setup trong dự án

### 5.1. Di chuyển file credentials

```bash
# Di chuyển file JSON vừa download vào thư mục dự án
# Đổi tên thành: firebase-credentials.json
# Đặt ở root của project (cùng cấp với app.py)
```

**Cấu trúc thư mục:**
```
AI_LeafGuard_Team/
├── app.py
├── firebase-credentials.json  ← File này
├── .env.example
├── src/
├── pages/
└── ...
```

### 5.2. Copy .env.example thành .env

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

### 5.3. Cài đặt dependencies

```bash
# Activate virtual environment nếu dùng
# .venv\Scripts\activate  (Windows)
# source .venv/bin/activate  (Linux/Mac)

# Cài đặt packages mới
pip install firebase-admin python-dotenv
```

Hoặc cài tất cả từ requirements.txt:

```bash
pip install -r requirements.txt
```

## Bước 6: Verify Setup

Chạy ứng dụng:

```bash
streamlit run app.py
```

Nếu thấy lỗi về Firebase credentials:
- Kiểm tra file `firebase-credentials.json` có đúng vị trí không
- Kiểm tra file có đúng format JSON không
- Xem console có error message gì

## Bước 7: Test Authentication

1. Mở ứng dụng trong browser
2. Click **"Đăng ký"** ở sidebar
3. Điền form đăng ký
4. Submit
5. Kiểm tra Firebase Console → Authentication → Users
6. Bạn sẽ thấy user vừa tạo

## 🎉 Hoàn tất!

Bây giờ bạn có thể:
- ✅ Đăng ký / Đăng nhập
- ✅ Chẩn đoán bệnh cây
- ✅ Lưu lịch sử tự động
- ✅ Xem thống kê
- ✅ Quản lý profile

---

## 🔧 Troubleshooting

### Lỗi: "Firebase credentials file not found"

**Giải pháp:**
- Check file `firebase-credentials.json` ở đúng vị trí
- Check tên file đúng chính xác
- Check file không bị corrupted

### Lỗi: "Permission denied" khi truy cập Firestore

**Giải pháp:**
- Check Firestore Rules đã set thành "test mode"
- Hoặc update rules trong Firebase Console

### Lỗi: "Email already exists"

**Giải pháp:**
- Email đã được đăng ký rồi
- Dùng email khác hoặc đăng nhập

---

## 🚀 Deploy lên Streamlit Cloud (Sau này)

Khi deploy lên Streamlit Cloud:

1. **KHÔNG** push file `firebase-credentials.json` lên GitHub
2. Dùng **Streamlit Secrets** để lưu credentials
3. Tạo file `.streamlit/secrets.toml`:

```toml
# Copy toàn bộ nội dung của firebase-credentials.json vào đây
# Theo format TOML
```

Chi tiết deploy sẽ hướng dẫn sau khi app hoàn thiện.
