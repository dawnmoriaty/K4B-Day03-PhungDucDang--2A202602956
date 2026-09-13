# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Phùng Đức Đăng 
> **Mã Sinh Viên / Mã Học viên:** 2A202602956
> **Chủ đề Lựa chọn:** Trợ lý AI Tư vấn & Đặt Set Thực phẩm / Đồ ăn

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá           | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm                                                                                      |
| :-------------------------- | :------------: | :----------------------------------------------------------------------------------------------------------------------- |
| **1. Multi-step Reasoning** |      5/ 5      | Nhận diện nhu cầu/dị ứng của khách →→ Tra cứu set phù hợp →→ Xác nhận với khách →→ Gọi tool đặt hàng.                    |
| **2. Tool Interaction**     |      5/ 5      | Phải kết nối MCP Server để lấy dữ liệu thực đơn thời gian thực và tạo đơn đặt hàng                                       |
| **3. Dynamic Decision**     |      4/ 5      | Phụ thuộc kết quả bước trước: nếu set đồ ăn hết hàng hoặc chứa chất gây dị ứng cho khách →→ đổi phương án sang set khác. |
| **4. Long Horizon Goal**    |      3/ 5      | Duy trì mục tiêu tư vấn cho đến khi chốt đơn thành công.Retry tối đa 5 lần nếu không có mục tiêu trong đoạn chat         |
| **TỔNG ĐIỂM AGENTIC FIT**   |   **17/ 20**   | *Nếu tổng điểm > 12/20: Bài toán rất phù hợp triển khai Agentic System.*                                                 |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "Tôi muốn đặt 2 suất set ăn 'SET-CLEAN-01' giao đến số 12 Chùa Bộc vào lúc 12:00 trưa nay, người nhận là Đăng (SĐT: 0912345678).",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "check_voucher",
    "arguments": {
      "order_time": "12:00"
    },
    "observation": {
      "status": "SUCCESS",
      "has_voucher": true,
      "voucher_code": "LUNCH15",
      "discount_amount": 15000,
      "description": "Giảm ngay 15.000 VNĐ cho mọi đơn hàng giao trong khung giờ trưa từ 11:00 đến 13:30."
    },
    "latency_ms": 5009.32
  },
  {
    "step": 2,
    "query": "Tôi muốn đặt 2 suất set ăn 'SET-CLEAN-01' giao đến số 12 Chùa Bộc vào lúc 12:00 trưa nay, người nhận là Đăng (SĐT: 0912345678).",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "order_food_set",
    "arguments": {
      "customer_name": "Đăng",
      "phone": "0912345678",
      "delivery_address": "12 Chùa Bộc",
      "delivery_time": "12:00",
      "set_code": "SET-CLEAN-01",
      "quantity": 2,
      "voucher_code": "LUNCH15"
    },
    "observation": {
      "status": "SUCCESS",
      "order_id": "ORD-CLEAN-01-2026",
      "customer_name": "Đăng",
      "set_code": "SET-CLEAN-01",
      "set_name": "Set Eat Clean Ức Gà Nướng Thảo Mộc Quinoa",
      "quantity": 2,
      "delivery_address": "12 Chùa Bộc",
      "delivery_time": "12:00",
      "phone": "0912345678",
      "voucher_applied": "LUNCH15",
      "discount_amount": "15,000 VNĐ",
      "total_payment": "135,000 VNĐ",
      "notes": "Giao hàng cẩn thận",
      "message": "Đặt đơn thành công cho khách Đăng! Đơn hàng ORD-CLEAN-01-2026 (2 suất Set Eat Clean Ức Gà Nướng Thảo Mộc Quinoa) sẽ được giao tới 12 Chùa Bộc vào lúc 12:00. Tổng thanh toán sau giảm giá: 135,000 VNĐ."
    },
    "latency_ms": 3578.68
  },
  {
    "step": 3,
    "query": "Tôi muốn đặt 2 suất set ăn 'SET-CLEAN-01' giao đến số 12 Chùa Bộc vào lúc 12:00 trưa nay, người nhận là Đăng (SĐT: 0912345678).",
    "action_type": "FINAL_ANSWER",
    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
    "output": "Dạ, em đã đặt thành công đơn hàng cho anh Đăng rồi ạ! Dưới đây là thông tin chi tiết đơn hàng của anh:\n- Người nhận: Đăng (SĐT: 0912345678)\n- Món ăn: 2x Set Eat Clean Ức Gà Nướng Thảo Mộc Quinoa (SET-CLEAN-01)\n- Địa chỉ giao hàng: 12 Chùa Bộc\n- Thời gian giao hàng: 12:00 trưa nay\n- Ưu đãi áp dụng: Voucher LUNCH15 (Giảm 15.000 VNĐ)\n- Tổng tiền thanh toán: 135.000 VNĐ\nĐơn hàng sẽ được chuẩn bị và giao tới đúng 12:00.",
    "latency_ms": 5173.22
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini `gemini-3.6-flash`).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 10 lượt.
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
