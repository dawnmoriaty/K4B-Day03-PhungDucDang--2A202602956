# 🖥️ REACT AGENT OBSERVABILITY DASHBOARD (VINUNI LAB 03)

**Học viên:** Phùng Đức Đăng — MSSV: `2A202602956` — VinUni AI Course Day 03

Giao diện Web tương tác trực quan hóa toàn bộ chuỗi suy luận của **ReAct Agent (MCP Enhanced)** theo chuẩn giáo trình bài giảng VinUni Day 03.

---

## 🌟 Các Tính Năng Nổi Bật

1. **Waterfall Trace Stream (ReAct Observability):**
   - Hiển thị từng bước suy luận: `Thought ➔ Action (MCP Tool) ➔ Observation (JSON-RPC) ➔ Final Answer`.
   - Đo thời gian phản hồi (`latency_ms`) của từng bước và toàn phiên.
   - Ghi nhận và cảnh báo tức thì các cơ chế phòng vệ:
     - 🛡️ **Duplicate Tool Call Detector**: Ngăn chặn gọi lại tool và tham số cũ.
     - 🛑 **Max Iterations Circuit Breaker**: Tự động ngắt khi chạm ngưỡng số bước tối đa.
2. **Loop Controller (Điều chỉnh số bước tối đa):**
   - Thanh trượt điều chỉnh `max_iterations` từ 1 đến 15 bước.
   - Đánh giá trạng thái an toàn / cảnh báo lãng phí token theo thời gian thực.
3. **Đo Lường Token & Chi Phí (Cost Calculator):**
   - Đo Input Tokens & Output Tokens của từng bước.
   - Tính toán chi phí thực tế theo biểu giá Gemini Flash / OpenAI bằng cả **USD ($)** và quy đổi **VNĐ (đ)**.
   - Thanh tiến trình Budget Ceiling Safeguard kiểm soát ngân sách an toàn.
4. **Hệ Thống Hint Buttons / Quick Chips:**
   - 7 nút bấm 1-click tích hợp các kịch bản test quan trọng:
     - 🥗 Tra cứu thực đơn tổng quan & Voucher giờ vàng
     - 🔍 Tra cứu chi tiết thành phần calo, protein, carb, fat (`SET-CLEAN-01`)
     - 📦 Đặt 2 suất trưa nhận voucher `LUNCH15`
     - ⚠️ Cảnh báo dị ứng hải sản & gợi ý món an toàn
     - 🛑 Xử lý lỗi set không tồn tại (`SET-VIP-9999`)
     - 🏋️ Tính toán định lượng dinh dưỡng cho người tập gym 70kg
     - ❓ Kịch bản Prompt thiếu thông tin (Hỏi lại & Gợi ý 3 món)
5. **Data Explorer (Thực đơn 21 món & Vouchers):**
   - Bảng tra cứu trực quan 21 set ăn thuộc các dòng Eat Clean, Thuần Chay, Tăng Cơ, Hải Sản, Keto, Bữa Sáng Healthy, Detox, Combo Gia Đình.
   - Tra cứu các mã voucher giờ vàng: `MORNING10`, `LUNCH15`, `DINNER20`, `HEALTHY10`, `COMBO50`.

---

## 🚀 Hướng Dẫn Khởi Chạy (1 Lệnh)

```bash
.venv/bin/python ui/server.py
```

Mở trình duyệt truy cập:
👉 **[http://localhost:5000](http://localhost:5000)** (hoặc `http://127.0.0.1:5000`)
