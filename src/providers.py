"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
from typing import Dict, Any, List
import re
import unicodedata
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()


def strip_accents(text: str) -> str:
    """Chuẩn hóa loại bỏ dấu tiếng Việt để đối sánh linh hoạt (hỗ trợ cả có dấu, không dấu, viết tắt)"""
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = text.replace('đ', 'd').replace('Đ', 'D')
    return unicodedata.normalize('NFC', text).lower().strip()


class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key (Tuân thủ chuẩn Codelab VinUni)"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Chatbot Baseline (Cấp 2 - Không dùng Tool):
        Không kết nối MCP Server thời gian thực, do đó phản hồi rõ ràng không có thông tin chi tiết.
        """
        clean = strip_accents(prompt)
        if re.search(r'\b(bo|beef|ga|chicken|chay|vegan|keto|mon|set|dat|gia|menu|thuc don)\b', clean):
            return (
                f"[Healthy Food Chatbot (Baseline)]: Chào bạn! Mình đã nhận được yêu cầu về '{prompt}'. "
                "Tuy nhiên, ở chế độ Chatbot Baseline (Cấp độ 2 - Không dùng Tool), mình KHÔNG CÓ THÔNG TIN "
                "chi tiết và bảng giá thời gian thực từ cơ sở dữ liệu để tra cứu hay đặt món cho bạn. "
                "Bạn vui lòng chuyển sang chế độ 'ReAct Agent' ở góc trên để hệ thống tự động kết nối MCP Server "
                "tra cứu thực đơn và chốt đơn nhé!"
            )
        return (
            f"[Healthy Food Chatbot (Baseline)]: Xin chào! Mình là Chatbot tư vấn ẩm thực (Chế độ Baseline). "
            f"Về yêu cầu '{prompt}', mình KHÔNG CÓ THÔNG TIN dữ liệu thời gian thực do không kết nối MCP Server. "
            "Bạn hãy bật chế độ 'ReAct Agent' để trải nghiệm đầy đủ tính năng tra cứu và xử lý nhé!"
        )

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        clean = strip_accents(prompt)
        
        # 1. Đã có đủ thông tin sau quan sát (Observation) -> Xuất Final Answer
        if "kết quả công cụ (observation):" in prompt_lower or "observation" in prompt_lower:
            if "set-beef" in prompt_lower or "tang_co" in prompt_lower or "bò" in prompt_lower or "bo" in clean:
                res = {
                    "type": "text",
                    "content": (
                        "[Healthy Food Assistant]: Dạ, mình đã tra cứu thực đơn thời gian thực cho bạn! Dưới đây là các set Bò Úc giàu đạm:\n"
                        "1. 🥩 Set Bò Úc Áp Chảo Măng Tây (SET-BEEF-01) - 110.000đ | 620 kcal (48g Protein)\n"
                        "2. 🍛 Cơm Gạo Lứt Bò Xào Nấm Kim Châm (SET-BEEF-02) - 95.000đ | 580 kcal (42g Protein)\n"
                        "💡 Ưu đãi: Khung giờ trưa có voucher LUNCH15 giảm 15k, tối có DINNER20 giảm 20k! "
                        "Bạn muốn đặt set nào và giao đến đâu để mình chốt đơn giúp bạn ạ?"
                    ),
                    "thought": "Đã nhận được dữ liệu món ăn từ MCP Server. Tôi tổng hợp danh sách món Bò Úc kèm calo, giá niêm yết và voucher cho khách hàng."
                }
            elif "eat_clean" in prompt_lower or "set-clean" in prompt_lower:
                res = {
                    "type": "text",
                    "content": (
                        "[Healthy Food Assistant]: Dạ, mình đã kiểm tra kho món Eat Clean:\n"
                        "1. 🥗 Set Eat Clean Ức Gà Nướng Quinoa (SET-CLEAN-01) - 75.000đ | 480 kcal\n"
                        "2. 🥑 Salad Cá Hồi Áp Chảo Bơ Sáp (SET-CLEAN-02) - 120.000đ | 520 kcal\n"
                        "💡 Các món đều an toàn, tươi mới trong ngày và áp dụng voucher giờ vàng. Bạn muốn đặt giao đến địa chỉ nào ạ?"
                    ),
                    "thought": "Đã nhận được dữ liệu quan sát từ MCP Server. Tôi xuất câu trả lời gợi ý Eat Clean kèm giá và calo."
                }
            else:
                res = {
                    "type": "text",
                    "content": "Dạ mình đã tổng hợp đầy đủ thông tin từ hệ thống MCP Server: Thực phẩm luôn tươi mới trong ngày, an toàn thực phẩm 100% và sẵn sàng phục vụ quý khách! Bạn cần tư vấn thêm set nào nữa không ạ?",
                    "thought": "Đã nhận được dữ liệu quan sát từ MCP Server. Tôi sẽ xuất câu trả lời hoàn chỉnh cho khách hàng."
                }
        # 2. Xử lý kịch bản Đặt set đồ ăn & Tra cứu theo nhu cầu (Food Assistant)
        elif re.search(r'\b(bo|beef)\b', clean) and "query_food_set" not in clean and "set-beef" not in clean:
            res = {
                "type": "tool_call",
                "tool_name": "query_food_set",
                "arguments": {"category": "tang_co", "min_items": 3},
                "thought": "Khách hàng muốn ăn cơm bò (nhận diện từ khóa 'bò' / 'bo'). Tôi sẽ gọi tool query_food_set với danh mục 'tang_co' để tra cứu các set Bò Úc giàu đạm từ database."
            }
        elif (re.search(r'\b(ga|chicken)\b', clean) or "eat clean" in clean or "giam can" in clean or "giam mo" in clean) and "query_food_set" not in clean:
            res = {
                "type": "tool_call",
                "tool_name": "query_food_set",
                "arguments": {"category": "eat_clean", "min_items": 3},
                "thought": "Khách hàng quan tâm đến món gà hoặc chế độ Eat Clean giảm cân. Tôi sẽ gọi tool query_food_set lọc danh mục 'eat_clean'."
            }
        elif re.search(r'\b(chay|vegan)\b', clean) and "query_food_set" not in clean:
            res = {
                "type": "tool_call",
                "tool_name": "query_food_set",
                "arguments": {"category": "chay", "min_items": 3},
                "thought": "Khách hàng muốn tìm món thuần chay. Tôi sẽ gọi tool query_food_set lọc danh mục thực đơn thuần chay 'chay'."
            }
        elif ("di ung" in clean or "diung" in clean or "allergy" in clean) and "check_allergy" not in clean:
            res = {
                "type": "tool_call",
                "tool_name": "check_allergy",
                "arguments": {"allergy_info": "dị ứng hải sản"},
                "thought": "Khách hàng có đề cập đến tiền sử dị ứng thực phẩm. Tôi cần gọi tool check_allergy trước để đảm bảo an toàn tuyệt đối."
            }
        elif ("an toi" in clean or "toi nay" in clean or "18:30" in clean or "an trua" in clean or "trua nay" in clean or "voucher" in clean) and "check_voucher" not in clean:
            order_time = "12:00 trưa" if ("trua" in clean) else "18:30 tối"
            res = {
                "type": "tool_call",
                "tool_name": "check_voucher",
                "arguments": {"order_time": order_time},
                "thought": f"Khách hàng muốn ăn/giao vào khung giờ {order_time}. Tôi sẽ kiểm tra mã ưu đãi giờ vàng bằng tool check_voucher."
            }
        elif ("dat 2 suat" in clean or "dat hang" in clean or ("dat" in clean and "chua boc" in clean)) and "order_food_set" not in clean:
            res = {
                "type": "tool_call",
                "tool_name": "order_food_set",
                "arguments": {
                    "customer_name": "Đăng",
                    "set_code": "SET-CLEAN-01",
                    "delivery_address": "số 12 Chùa Bộc",
                    "quantity": 2,
                    "delivery_time": "12:00 trưa nay",
                    "phone": "0912345678"
                },
                "thought": "Khách hàng yêu cầu đặt món với đầy đủ thông tin địa chỉ và thời gian. Tôi sẽ tiến hành gọi tool order_food_set để tạo đơn hàng."
            }
        elif "set-vip-9999" in clean:
            res = {
                "type": "tool_call",
                "tool_name": "query_food_set",
                "arguments": {"set_code": "SET-VIP-9999"},
                "thought": "Khách hàng muốn tra cứu thông tin set ăn có mã SET-VIP-9999. Tôi sẽ gọi tool query_food_set."
            }
        elif "set-clean-01" in clean or "tra cuu thong tin chi tiet" in clean:
            res = {
                "type": "tool_call",
                "tool_name": "query_food_set",
                "arguments": {"set_code": "SET-CLEAN-01"},
                "thought": "Khách hàng muốn tra cứu thông tin dinh dưỡng set SET-CLEAN-01. Tôi sẽ gọi tool query_food_set."
            }
        elif "sv2026001" in clean and "dat lich" in clean:
            res = {
                "type": "tool_call",
                "tool_name": "schedule_appointment",
                "arguments": {"student_id": "SV2026001", "datetime_str": "14:00 15/09/2026", "advisor_name": "PGS.TS Nguyễn Văn A"},
                "thought": "Người dùng yêu cầu đặt lịch hẹn tư vấn cho sinh viên SV2026001. Tôi sẽ gọi tool schedule_appointment."
            }
        elif "sv2026001" in clean or "tra cuu thong tin hoc vu" in clean:
            res = {
                "type": "tool_call",
                "tool_name": "academic_query",
                "arguments": {"student_id": "SV2026001"},
                "thought": "Người dùng muốn tra cứu thông tin học vụ của sinh viên SV2026001. Tôi sẽ gọi tool academic_query."
            }
        else:
            res = {
                "type": "text",
                "content": "[Healthy Food Assistant]: Chào bạn! Quán chúng mình chuyên cung cấp các set ăn lành mạnh gồm: Eat Clean (giảm mỡ), Thuần chay (dưỡng sinh), Bò Úc (tăng cơ) và Keto. Quán có giao hàng tận nơi từ 07:00 đến 21:30 hàng ngày với nhiều voucher giờ vàng hấp dẫn!",
                "thought": "Câu hỏi chung về thực đơn và chính sách của quán, trả lời trực tiếp từ System Prompt mà không cần gọi Tool."
            }
            
        p_tokens = max(20, len(prompt) // 4)
        c_tokens = max(25, len(res.get("content", "")) // 4 if res.get("type") == "text" else 45)
        res["usage"] = {
            "prompt_tokens": p_tokens,
            "completion_tokens": c_tokens,
            "total_tokens": p_tokens + c_tokens
        }
        return res


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider (Native Tool Calling với Google GenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-3.6-flash"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return MockOfflineProvider().generate(prompt, system_prompt)
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate(prompt, system_prompt)

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("ℹ️ [Gemini Provider]: Chưa tìm thấy GEMINI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)
        
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            
            # Chuẩn hóa function declarations cho Gemini SDK
            function_declarations = []
            for tool in tools_schema:
                # Bỏ qua các tool schema chưa được định nghĩa hoàn chỉnh
                if not tool.get("name") or not tool.get("parameters"):
                    continue
                function_declarations.append({
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                })

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                tools=[{"function_declarations": function_declarations}] if function_declarations else None,
                temperature=0.2
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Trích xuất thống kê Token thực tế
            usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                usage["prompt_tokens"] = getattr(response.usage_metadata, 'prompt_token_count', 0) or 0
                usage["completion_tokens"] = getattr(response.usage_metadata, 'candidates_token_count', 0) or 0
                usage["total_tokens"] = getattr(response.usage_metadata, 'total_token_count', 0) or (usage["prompt_tokens"] + usage["completion_tokens"])
            if usage["total_tokens"] == 0:
                usage["prompt_tokens"] = max(10, len(prompt) // 4)
                usage["completion_tokens"] = max(10, len(response.text or '') // 4) if not response.function_calls else 45
                usage["total_tokens"] = usage["prompt_tokens"] + usage["completion_tokens"]

            # Kiểm tra xem Gemini có trả về Tool Call không
            if response.function_calls:
                call = response.function_calls[0]
                args = dict(call.args) if hasattr(call, 'args') and call.args else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.name,
                    "arguments": args,
                    "thought": f"Gemini quyết định gọi công cụ '{call.name}' với tham số: {json.dumps(args, ensure_ascii=False)}",
                    "usage": usage
                }
            else:
                return {
                    "type": "text",
                    "content": response.text or "",
                    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
                    "usage": usage
                }

        except Exception as e:
            print(f"⚠️ [Gemini API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (Native Tool Calling với OpenAI SDK)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return MockOfflineProvider().generate(prompt, system_prompt)
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate(prompt, system_prompt)

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print("ℹ️ [OpenAI Provider]: Chưa tìm thấy OPENAI_API_KEY hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None
            )

            usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            if hasattr(response, 'usage') and response.usage:
                usage["prompt_tokens"] = getattr(response.usage, 'prompt_tokens', 0) or 0
                usage["completion_tokens"] = getattr(response.usage, 'completion_tokens', 0) or 0
                usage["total_tokens"] = getattr(response.usage, 'total_tokens', 0) or (usage["prompt_tokens"] + usage["completion_tokens"])

            msg = response.choices[0].message
            if msg.tool_calls:
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments) if call.function.arguments else {}
                return {
                    "type": "tool_call",
                    "tool_name": call.function.name,
                    "arguments": args,
                    "thought": f"OpenAI quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}",
                    "usage": usage
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "OpenAI phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
                    "usage": usage
                }
        except Exception as e:
            print(f"⚠️ [OpenAI API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


def get_llm_provider() -> BaseLLMProvider:
    """Factory function khởi tạo Provider theo LLM_PROVIDER env variable"""
    provider_type = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    if provider_type == "gemini":
        key = os.getenv("GEMINI_API_KEY")
        if key and key != "your_gemini_api_key_here":
            return GeminiProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_openai_api_key_here":
            return OpenAIProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()
