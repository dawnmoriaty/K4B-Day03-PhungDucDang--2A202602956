"""
🔌 MULTI-PROVIDER LLM ADAPTER (Google Gemini, OpenAI & Offline Mock)
Hỗ trợ Native Tool Calling và chuyển đổi linh hoạt qua biến môi trường LLM_PROVIDER.
"""

import os
import sys
import json
from typing import Dict, Any, List
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho các LLM Provider hỗ trợ Native Tool Calling"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        raise NotImplementedError


class MockOfflineProvider(BaseLLMProvider):
    """Offline Mock Provider dùng để chạy thử mà không tốn API Key"""
    def __init__(self):
        self.model_name = "Offline-Mock-Model-2026"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        return f"[Mock Chatbot Response]: Xin chào! Tôi đã nhận được câu hỏi '{prompt}'. (Chế độ Chatbot không có Tool tra cứu dữ liệu thời gian thực hay đặt món)."

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        
        # 1. Đã có đủ thông tin sau quan sát -> Xuất Final Answer
        if "kết quả công cụ (observation):" in prompt_lower:
            res = {
                "type": "text",
                "content": "Dạ mình đã tổng hợp đầy đủ thông tin từ hệ thống: Khách hàng an toàn với các set gợi ý, áp dụng ưu đãi giờ vàng thành công và sẵn sàng phục vụ quý khách!",
                "thought": "Đã nhận được dữ liệu quan sát từ MCP Server. Tôi sẽ xuất câu trả lời hoàn chỉnh cho khách hàng."
            }
        # 2. Xử lý kịch bản Đặt set đồ ăn (Food Assistant)
        elif "dị ứng" in prompt_lower and "check_allergy" not in prompt_lower:
            res = {
                "type": "tool_call",
                "tool_name": "check_allergy",
                "arguments": {"allergy_info": "dị ứng hải sản"},
                "thought": "Khách hàng có đề cập đến tiền sử dị ứng thực phẩm. Tôi cần gọi tool check_allergy trước để đảm bảo an toàn tuyệt đối."
            }
        elif ("ăn tối" in prompt_lower or "tối nay" in prompt_lower or "18:30" in prompt_lower) and "check_voucher" not in prompt_lower:
            res = {
                "type": "tool_call",
                "tool_name": "check_voucher",
                "arguments": {"order_time": "18:30 tối"},
                "thought": "Khách hàng muốn ăn hoặc giao hàng vào buổi tối. Tôi sẽ kiểm tra mã ưu đãi giờ vàng bữa tối bằng tool check_voucher."
            }
        elif "đặt 2 suất" in prompt_lower or ("đặt" in prompt_lower and "chùa bộc" in prompt_lower):
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
        elif "set-vip-9999" in prompt_lower:
            res = {
                "type": "tool_call",
                "tool_name": "query_food_set",
                "arguments": {"set_code": "SET-VIP-9999"},
                "thought": "Khách hàng muốn tra cứu thông tin set ăn có mã SET-VIP-9999. Tôi sẽ gọi tool query_food_set."
            }
        elif "set-clean-01" in prompt_lower or "tra cứu thông tin chi tiết" in prompt_lower:
            res = {
                "type": "tool_call",
                "tool_name": "query_food_set",
                "arguments": {"set_code": "SET-CLEAN-01"},
                "thought": "Khách hàng muốn tra cứu thông tin dinh dưỡng set SET-CLEAN-01. Tôi sẽ gọi tool query_food_set."
            }
        elif "sv2026001" in prompt_lower and "đặt lịch" in prompt_lower:
            res = {
                "type": "tool_call",
                "tool_name": "schedule_appointment",
                "arguments": {"student_id": "SV2026001", "datetime_str": "14:00 15/09/2026", "advisor_name": "PGS.TS Nguyễn Văn A"},
                "thought": "Người dùng yêu cầu đặt lịch hẹn tư vấn cho sinh viên SV2026001. Tôi sẽ gọi tool schedule_appointment."
            }
        elif "sv2026001" in prompt_lower or "tra cứu thông tin học vụ" in prompt_lower:
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
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env! Đang sử dụng chế độ Mock."
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(model=self.model_name, contents=contents)
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"

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
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        self.base_url = base_url

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key in ["your_openai_api_key_here", "your_openrouter_api_key_here"]:
            return "[OpenAI/OpenRouter Error]: Chưa cấu hình API Key hợp lệ trong file .env! Đang sử dụng chế độ Mock."
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(model=self.model_name, messages=messages)
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[API Exception]: {str(e)}"

    def generate_with_tools(self, prompt: str, tools_schema: List[Dict[str, Any]], system_prompt: str = "") -> Dict[str, Any]:
        if not self.api_key or self.api_key in ["your_openai_api_key_here", "your_openrouter_api_key_here"]:
            print("ℹ️ [API Provider]: Chưa tìm thấy API Key hợp lệ. Tự động chuyển sang Mock Offline.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)

            tools = []
            for tool in tools_schema:
                if not tool.get("name"):
                    continue
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.get("name"),
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
                    "thought": f"Model quyết định gọi công cụ '{call.function.name}' với tham số: {json.dumps(args, ensure_ascii=False)}",
                    "usage": usage
                }
            else:
                return {
                    "type": "text",
                    "content": msg.content or "",
                    "thought": "Model phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
                    "usage": usage
                }
        except Exception as e:
            print(f"⚠️ [API Warning]: Không thể kết nối live API ({str(e)}). Tự động fallback về Mock.")
            return MockOfflineProvider().generate_with_tools(prompt, tools_schema, system_prompt)


class OpenRouterProvider(OpenAIProvider):
    """OpenRouter Provider (sử dụng OpenAI SDK với base_url='https://openrouter.ai/api/v1')"""
    def __init__(self, api_key: str = None, model: str = None):
        key = api_key or os.getenv("OPENROUTER_API_KEY")
        model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.0-flash-001"
        super().__init__(api_key=key, model=model_name, base_url="https://openrouter.ai/api/v1")


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
    elif provider_type == "openrouter":
        key = os.getenv("OPENROUTER_API_KEY")
        if key and key != "your_openrouter_api_key_here":
            return OpenRouterProvider()
        else:
            return MockOfflineProvider()
    elif provider_type == "mock":
        return MockOfflineProvider()
    else:
        return MockOfflineProvider()
