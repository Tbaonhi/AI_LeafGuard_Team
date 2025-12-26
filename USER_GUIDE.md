# 📚 User Guide - AI LeafGuard với Firebase Authentication

## Tổng quan

AI LeafGuard giờ đây đã có hệ thống authentication hoàn chỉnh, cho phép bạn:
- Tạo tài khoản cá nhân
- Lưu lịch sử chẩn đoán tự động
- Xem thống kê và insights
- Quản lý profile

---

## 🚀 Bắt đầu

### Lần đầu sử dụng

1. **Chạy ứng dụng:**
   ```bash
   streamlit run app.py
   ```

2. **Đăng ký tài khoản:**
   - Click nút **"📝 Đăng ký"** ở sidebar
   - Điền thông tin:
     - Tên hiển thị
     - Email
     - Password (tối thiểu 6 ký tự)
     - Xác nhận password
   - Tick ✓ "Đồng ý với Điều khoản"
   - Click **"🚀 Đăng ký"**
   - Hệ thống sẽ tự động đăng nhập sau khi đăng ký thành công

3. **Sử dụng ngay:**
   - Bạn đã sẵn sàng để chẩn đoán bệnh cây!

### Người dùng cũ

1. Chạy app
2. Click **"🔐 Đăng nhập"** ở sidebar
3. Nhập email và password
4. Click **"🚀 Đăng nhập"**

---

## 📋 Các tính năng chính

### 1. 🔍 Chẩn đoán Bệnh Cây

**Trang chính** (`app.py`)

1. Upload ảnh lá cây (JPG, PNG, JPEG)
2. Click **"🔍 Diagnose"**
3. Xem kết quả:
   - Loại cây
   - Tên bệnh
   - Độ tin cậy
   - Top-3 predictions
4. **Nếu đã đăng nhập:**
   - Kết quả tự động lưu vào lịch sử
   - Balloons celebration 🎈

### 2. 📊 Xem Lịch Sử

**Trang History** (Click "📊 Lịch sử" ở sidebar)

Features:
- Xem tất cả kết quả chẩn đoán trước đây
- Filter và sort
- 2 chế độ hiển thị:
  - **📄 Danh sách**: Dễ đọc, có actions
  - **📊 Bảng dữ liệu**: Export CSV
- Thống kê overview:
  - Số lượng cây khỏe mạnh vs có bệnh
  - Độ tin cậy trung bình
  - Số loại cây khác nhau
- **Insights tự động**
- **Export CSV** để phân tích thêm

### 3. 👤 Quản lý Profile

**Trang Profile** (Click "👤 Profile" ở sidebar)

Bạn có thể:
- Xem thông tin cá nhân
- Xem thống kê:
  - Tổng số chẩn đoán
  - Cây phổ biến nhất
  - Bệnh phát hiện nhiều nhất
  - Độ tin cậy trung bình
- **Chỉnh sửa tên hiển thị**
- **Đổi mật khẩu**
- **Đăng xuất**

### 4. 🔐 Bảo mật

- Mật khẩu được mã hóa bởi Firebase
- Session management an toàn
- Dữ liệu cá nhân được bảo vệ

---

## 💡 Tips & Best Practices

### Để có kết quả chẩn đoán tốt nhất:

1. **Chụp ảnh rõ nét**
   - Lá cây nên chiếm >50% khung hình
   - Ánh sáng tự nhiên
   - Không mờ, không bị cắt

2. **Một lá mỗi lần**
   - Tập trung vào một lá cây
   - Tránh chụp nhiều lá chồng lên nhau

3. **Độ tin cậy**
   - ≥80%: Rất tin cậy
   - 60-80%: Khá tin cậy
   - <60%: Nên chụp lại ảnh khác

### Quản lý tài khoản:

1. **Mật khẩu mạnh**
   - Ít nhất 8 ký tự
   - Có chữ hoa, số, ký tự đặc biệt
   - Không dùng mật khẩu dễ đoán

2. **Email**
   - Dùng email thật để nhận thông báo
   - Kiểm tra spam nếu không nhận được email

3. **Lịch sử**
   - Xem lại lịch sử thường xuyên
   - Export CSV để backup
   - Xóa các kết quả không cần thiết

---

## 🛠️ Troubleshooting

### "Email already exists"
→ Email đã được đăng ký. Dùng email khác hoặc đăng nhập.

### "Password phải có ít nhất 6 ký tự"
→ Mật khẩu quá ngắn. Đặt mật khẩu dài hơn.

### Không nhận được email reset password
→ Tính năng đang develop. Liên hệ admin.

### Lịch sử không hiển thị
→ Đảm bảo bạn đã đăng nhập. Chỉ user đã login mới có lịch sử.

### "Firebase credentials not found"
→ Đây là lỗi setup. Xem [FIREBASE_SETUP.md](FIREBASE_SETUP.md)

---

## 📞 Support

Nếu gặp vấn đề, liên hệ:
- Email: [your-email@example.com]
- GitHub Issues: [repository-url]

---

## 🎯 Future Features (Đang phát triển)

- [ ] Google Sign-In
- [ ] Email verification
- [ ] Password reset qua email
- [ ] Upload ảnh lên Cloud Storage
- [ ] Share diagnosis results
- [ ] Mobile app (Flutter)
- [ ] Admin dashboard

Hãy theo dõi để cập nhật những tính năng mới nhất! 🚀
