"""
🚀 CORE AGENT APPLICATION (DAY 03: CHATBOT VS REACT AGENT)
Thực thi so sánh giữa Chatbot Baseline (Cấp 2) và ReAct Agent kết nối MCP Server (Cấp 3).
"""

import json
import os
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from mcp_server import MCPAcademicServer
from prompts import (
    CHATBOT_BASELINE_PROMPT,
    REACT_AGENT_SYSTEM_PROMPT,
    MAX_ITERATIONS
)
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Tải danh sách 5 test cases từ config/test_cases.json hoặc config/test_cases.example.json"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    if not os.path.exists(config_path):
        example_path = os.path.join(base_dir, "config", "test_cases.example.json")
        if os.path.exists(example_path):
            print("⚠️ [CONFIG NOTICE]: Chưa thấy file 'config/test_cases.json'. Đang dùng mẫu 'config/test_cases.example.json'.")
            print("👉 Hãy chạy: copy config/test_cases.example.json config/test_cases.json và viết test cases theo đề tài của bạn!\n")
            config_path = example_path
        else:
            config_path = "test_cases.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_waterfall_trace(trace_data: list):
    """Ghi vết log Waterfall Trace Log ra file docs/trace_waterfall.json"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    trace_path = os.path.join(docs_dir, "trace_waterfall.json")
    with open(trace_path, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, ensure_ascii=False, indent=2)
    print(f"📊 [OBSERVABILITY]: Đã lưu {len(trace_data)} sự kiện Waterfall Trace tại '{trace_path}'!")


def run_baseline_chatbot(user_query: str, provider):
    """Chạy Chatbot gốc (Cấp 2) không có công cụ gọi Tool"""
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot phản hồi:\n{response}")


def is_duplicate_call(trace_logs: list, tool_name: str, arguments: dict) -> bool:
    """Safeguard: Phát hiện xem cùng một tool với cùng tham số đã được gọi lặp lại hay chưa"""
    for log in trace_logs:
        if log.get("action_type") == "TOOL_EXECUTION":
            if log.get("tool_name") == tool_name and log.get("arguments") == arguments:
                return True
    return False


def run_react_agent(user_query: str, provider, mcp_server: MCPAcademicServer) -> list:
    """
    [REACT AGENT LOOP V2 - PRODUCTION GRADE]
    Thực thi vòng lặp Thought -> Action -> Observation với MCP Server và Safeguards
    Bám sát chuẩn giáo trình VinUniversity AI Course (Slide Day 3)
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    
    step = 0
    trace_logs = []
    tools_list = mcp_server.list_tools()
    
    # Trajectory Context tích lũy qua từng vòng lặp
    trajectory_context = f"Yêu cầu của khách hàng: {user_query}"
    
    while step < MAX_ITERATIONS:
        step += 1
        step_start_time = time.time()
        print(f"\n--- 🔄 Vòng lặp ReAct Loop (Step {step}/{MAX_ITERATIONS}) ---")
        
        # Gọi LLM với Native Tool Calling Specs và ngữ cảnh tích lũy
        llm_response = provider.generate_with_tools(
            trajectory_context,
            tools_list,
            system_prompt=REACT_AGENT_SYSTEM_PROMPT
        )
        latency_ms = round((time.time() - step_start_time) * 1000, 2)
        
        thought = llm_response.get("thought", "Đang suy luận bước tiếp theo...")
        print(f"🧠 [Thought]: {thought}")
        
        # TRƯỜNG HỢP 1: LLM quyết định đưa ra Final Answer hoàn chỉnh
        if llm_response.get("type") == "text":
            final_content = llm_response.get("content", "")
            print(f"🏁 [Final Answer]:\n{final_content}")
            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "FINAL_ANSWER",
                "thought": thought,
                "output": final_content,
                "latency_ms": latency_ms
            })
            break
            
        # TRƯỜNG HỢP 2: LLM đề xuất gọi Tool (Action)
        elif llm_response.get("type") == "tool_call":
            tool_name = llm_response.get("tool_name")
            arguments = llm_response.get("arguments", {})
            
            print(f"🛠️ [Action Proposed]: {tool_name}({json.dumps(arguments, ensure_ascii=False)})")
            
            # SAFEGUARD 1: Phát hiện Agent đi vòng (Duplicate Tool Call)
            if is_duplicate_call(trace_logs, tool_name, arguments):
                warning_msg = f"WARNING: Tool '{tool_name}' đã được gọi với tham số tương tự ở bước trước. Vui lòng không lặp lại và chuyển sang hành động khác hoặc trả lời khách."
                print(f"⚠️ [SAFEGUARD TRIGGERED]: {warning_msg}")
                obs_data = {"status": "DUPLICATE_CALL_WARNING", "message": warning_msg}
            else:
                # SAFEGUARD 2: Bắt lỗi Timeout & Exception khi gọi qua MCP Server
                try:
                    mcp_result = mcp_server.call_tool(tool_name, arguments)
                    obs_data = mcp_result.get("result", {})
                except TimeoutError:
                    obs_data = {"status": "TIMEOUT_ERROR", "error": f"Tool {tool_name} timed out after 5s"}
                except Exception as e:
                    obs_data = {"status": "EXECUTION_ERROR", "error": str(e)}
            
            obs_str = json.dumps(obs_data, ensure_ascii=False)
            print(f"👁️ [Observation từ MCP Server]: {obs_str}")
            
            trace_logs.append({
                "step": step,
                "query": user_query,
                "action_type": "TOOL_EXECUTION",
                "tool_name": tool_name,
                "arguments": arguments,
                "observation": obs_data,
                "latency_ms": latency_ms
            })
            
            # Nạp Observation ngược lại vào Trajectory Context để LLM suy nghĩ bước kế tiếp
            trajectory_context += f"\n\n[Step {step}]"
            trajectory_context += f"\n- Thought: {thought}"
            trajectory_context += f"\n- Action: {tool_name}({json.dumps(arguments, ensure_ascii=False)})"
            trajectory_context += f"\n- Kết quả công cụ (Observation): {obs_str}"
            
            # SAFEGUARD 3: Kiểm tra Circuit Breaker khi chạm ngưỡng số bước tối đa
            if step >= MAX_ITERATIONS:
                fallback_msg = (
                    f"Hệ thống đã thực hiện {step} bước suy luận tối đa (Max Iterations Circuit Breaker). "
                    "Đã ghi nhận các dữ liệu quan sát trên để hỗ trợ quý khách. Vui lòng liên hệ hotline 1900 6868 nếu cần trợ giúp thêm."
                )
                print(f"🛑 [CIRCUIT BREAKER]: {fallback_msg}")
                trace_logs.append({
                    "step": step + 1,
                    "query": user_query,
                    "action_type": "FINAL_ANSWER",
                    "thought": "Đạt giới hạn vòng lặp tối đa. Dừng lại an toàn và đưa ra phản hồi tổng kết.",
                    "output": fallback_msg,
                    "latency_ms": 5.0
                })
                break

    return trace_logs


if __name__ == "__main__":
    print("==========================================================")
    print("🏫 VINUNI AI COURSE - DAY 03 LAB: CHATBOT VS REACT AGENT")
    print("==========================================================")
    
    provider = get_llm_provider()
    mcp_server = MCPAcademicServer()
    
    print(f"🔌 LLM Provider: {provider.__class__.__name__}")
    print(f"🌐 MCP Server: {mcp_server.server_name}\n")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases thử nghiệm.\n")
    
    if "--interactive" in sys.argv:
        print("🎮 [INTERACTIVE MODE] Trò chuyện trực tiếp với ReAct Agent:")
        print("💡 Gợi ý câu hỏi thử nghiệm:")
        print("   - Câu hỏi chung: 'Quy chế học vụ VinUni yêu cầu bao nhiêu tín chỉ?'")
        print("   - Tra cứu học vụ: 'Hãy tra cứu thông tin học vụ của sinh viên SV2026001'")
        print("   - Đặt lịch hẹn: 'Đặt lịch hẹn tư vấn cho SV2026001 vào 14:00 ngày 15/09/2026'")
        print("   - Gõ 'exit' hoặc 'quit' để kết thúc phiên trò chuyện.\n")
        while True:
            try:
                user_input = input("👤 Sinh viên hỏi: ").strip()
                if not user_input or user_input.lower() in ["exit", "quit"]:
                    print("👋 Tạm biệt! Kết thúc phiên trò chuyện.")
                    break
                logs = run_react_agent(user_input, provider, mcp_server)
                save_waterfall_trace(logs)
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Đã thoát phiên tương tác.")
                break
    elif "--all" in sys.argv:
        print("🚀 [TEST SUITE MODE] Kiểm tra 5 Test Cases:")
        completed_count = 0
        todo_count = 0
        all_traces = []
        
        for tc in tests:
            print(f"\n==================================================")
            print(f"🧪 [{tc['id']}] Loại test: {tc['type']} (Độ phức tạp: {tc['complexity']})")
            print(f"📌 Kỳ vọng: {tc['expected_behavior']}")
            
            if tc["question"].strip().startswith("TODO"):
                print(f"⏸️ [CHƯA KÍCH HOẠT - ĐANG LÀ TODO]:")
                print(f"   {tc['question']}")
                print(f"   👉 Hãy mở file 'config/test_cases.json' để viết câu hỏi thực tế cho Test Case này!")
                todo_count += 1
            else:
                logs = run_react_agent(tc["question"], provider, mcp_server)
                all_traces.extend(logs)
                completed_count += 1
                
        print(f"\n==================================================")
        print(f"📊 [KẾT QUẢ TEST SUITE]: Đã thực thi {completed_count}/{len(tests)} Test Cases | {todo_count} Test Cases đang chờ điền câu hỏi (TODO)")
        if all_traces:
            save_waterfall_trace(all_traces)
        print(f"💡 Để trò chuyện trực tiếp từng câu: Chạy 'python src/app.py --interactive'")
    else:
        # Chế độ mặc định khi chỉ gõ 'python src/app.py'
        print("ℹ️ HƯỚNG DẪN SỬ DỤNG CHƯƠNG TRÌNH:")
        print("  1. Chat trực tiếp liên tục:   python src/app.py --interactive")
        print("  2. Chạy toàn bộ Test Cases:    python src/app.py --all\n")
        
        sample_query = tests[1]["question"]
        print(f"--- 🏁 DEMO CHẠY THỬ 1 TEST CASE MẪU (TC02: Tra cứu học vụ) ---")
        logs = run_react_agent(sample_query, provider, mcp_server)
        save_waterfall_trace(logs)
        print("\n💡 Hãy thử ngay lệnh: python src/app.py --interactive để chat trực tiếp!")
