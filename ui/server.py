#!/usr/bin/env python3
"""
🌐 REACT AGENT OBSERVABILITY & INTERACTIVE UI SERVER
Day 03: VinUni AI Course - Chatbot vs ReAct Agent (MCP Enhanced)
Sinh viên: Phùng Đức Đăng (MSSV: 2A202602956)
"""

import json
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

# Thiết lập đường dẫn root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
UI_DIR = os.path.join(BASE_DIR, "ui")

sys.path.insert(0, SRC_DIR)

from mcp_server import MCPAcademicServer
from providers import get_llm_provider
from app import run_react_agent, run_baseline_chatbot, save_waterfall_trace, calculate_token_cost

# Khởi tạo singleton server & provider
print("🚀 Đang khởi tạo MCP Academic Server và LLM Provider...")
mcp_server = MCPAcademicServer()
provider = get_llm_provider()
print(f"✅ Đã kết nối Provider: {provider.__class__.__name__} ({provider.model_name})")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Multi-threaded HTTP Server để hỗ trợ gọi ReAct song song mà không block UI"""
    daemon_threads = True


class AgentUIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200, "text/plain")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # 1. Trả về giao diện chính
        if path in ["/", "/index.html"]:
            html_path = os.path.join(UI_DIR, "index.html")
            if os.path.exists(html_path):
                with open(html_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self._set_headers(200, "text/html")
                self.wfile.write(content.encode("utf-8"))
            else:
                self._set_headers(404, "text/plain")
                self.wfile.write(b"UI file not found. Please ensure ui/index.html exists.")
            return

        # 2. API: Lấy trạng thái hệ thống
        if path == "/api/status":
            menu_file = os.path.join(DATA_DIR, "menu.json")
            voucher_file = os.path.join(DATA_DIR, "vouchers.json")
            total_items = 0
            total_vouchers = 0
            if os.path.exists(menu_file):
                with open(menu_file, "r", encoding="utf-8") as f:
                    total_items = len(json.load(f).get("items", []))
            if os.path.exists(voucher_file):
                with open(voucher_file, "r", encoding="utf-8") as f:
                    total_vouchers = len(json.load(f).get("happy_hour_vouchers", []))

            data = {
                "status": "ONLINE",
                "student_name": "Phùng Đức Đăng",
                "student_id": "2A202602956",
                "course": "VinUni AI Course Day 03 (Lab 03)",
                "provider": provider.__class__.__name__,
                "model_name": provider.model_name,
                "total_menu_items": total_items,
                "total_vouchers": total_vouchers,
                "tools_available": [t["name"] for t in mcp_server.list_tools()]
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        # 3. API: Lấy danh sách thực đơn 21 món
        if path == "/api/menu":
            menu_file = os.path.join(DATA_DIR, "menu.json")
            if os.path.exists(menu_file):
                with open(menu_file, "r", encoding="utf-8") as f:
                    menu_data = json.load(f)
                self._set_headers(200)
                self.wfile.write(json.dumps(menu_data, ensure_ascii=False).encode("utf-8"))
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Menu file not found"}).encode("utf-8"))
            return

        # 4. API: Lấy danh sách vouchers
        if path == "/api/vouchers":
            voucher_file = os.path.join(DATA_DIR, "vouchers.json")
            if os.path.exists(voucher_file):
                with open(voucher_file, "r", encoding="utf-8") as f:
                    v_data = json.load(f)
                self._set_headers(200)
                self.wfile.write(json.dumps(v_data, ensure_ascii=False).encode("utf-8"))
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Vouchers file not found"}).encode("utf-8"))
            return

        # 5. API: Lấy danh sách Test Cases
        if path == "/api/test-cases":
            tc_file = os.path.join(CONFIG_DIR, "test_cases.json")
            if os.path.exists(tc_file):
                with open(tc_file, "r", encoding="utf-8") as f:
                    tc_data = json.load(f)
                self._set_headers(200)
                self.wfile.write(json.dumps(tc_data, ensure_ascii=False).encode("utf-8"))
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Test cases file not found"}).encode("utf-8"))
            return

        # 6. API: Lấy Trace Waterfall mới nhất
        if path == "/api/latest-trace":
            trace_file = os.path.join(DOCS_DIR, "trace_waterfall.json")
            if os.path.exists(trace_file):
                with open(trace_file, "r", encoding="utf-8") as f:
                    trace_data = json.load(f)
                self._set_headers(200)
                self.wfile.write(json.dumps(trace_data, ensure_ascii=False).encode("utf-8"))
            else:
                self._set_headers(200)
                self.wfile.write(json.dumps([], ensure_ascii=False).encode("utf-8"))
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                payload = json.loads(body) if body else {}
            except Exception:
                payload = {}

            query = payload.get("query", "").strip()
            mode = payload.get("mode", "react")  # 'react' hoặc 'baseline'
            max_iterations = int(payload.get("max_iterations", 7))

            if not query:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Vui lòng nhập câu hỏi query!"}).encode("utf-8"))
                return

            print(f"\n📨 [API /api/chat] Nhận query: '{query}' | Mode: {mode} | Max Iterations: {max_iterations}")

            if mode == "baseline":
                # Chạy Chatbot Baseline (Cấp 2)
                res = run_baseline_chatbot(query, provider)
                response_data = {
                    "mode": "baseline",
                    "query": query,
                    "final_answer": res.get("output", ""),
                    "latency_ms": res.get("latency_ms", 0),
                    "usage": res.get("usage", {}),
                    "cost": res.get("cost", {}),
                    "trace_logs": []
                }
            else:
                # Chạy ReAct Agent (Cấp 3) với MCP Server & Safeguards
                trace_logs = run_react_agent(query, provider, mcp_server, max_iterations=max_iterations)
                
                # Cập nhật tệp trace_waterfall.json
                save_waterfall_trace(trace_logs)

                # Tìm final answer
                final_answer = ""
                for log in reversed(trace_logs):
                    if log.get("action_type") == "FINAL_ANSWER":
                        final_answer = log.get("output", "")
                        break
                if not final_answer and trace_logs:
                    final_answer = "Hệ thống đã hoàn tất chuỗi hành động tra cứu và lưu vết quan sát."

                # Tính tổng chi phí và token
                total_prompt_tokens = sum(log.get("usage", {}).get("prompt_tokens", 0) for log in trace_logs)
                total_completion_tokens = sum(log.get("usage", {}).get("completion_tokens", 0) for log in trace_logs)
                total_tokens = total_prompt_tokens + total_completion_tokens
                total_usd = sum(log.get("cost", {}).get("usd", 0.0) for log in trace_logs)
                total_vnd = sum(log.get("cost", {}).get("vnd", 0.0) for log in trace_logs)
                total_latency = sum(log.get("latency_ms", 0.0) for log in trace_logs)

                response_data = {
                    "mode": "react",
                    "query": query,
                    "final_answer": final_answer,
                    "total_latency_ms": round(total_latency, 2),
                    "trace_logs": trace_logs,
                    "usage_summary": {
                        "prompt_tokens": total_prompt_tokens,
                        "completion_tokens": total_completion_tokens,
                        "total_tokens": total_tokens
                    },
                    "cost_summary": {
                        "usd": round(total_usd, 6),
                        "vnd": round(total_vnd, 2)
                    },
                    "max_iterations": max_iterations
                }

            self._set_headers(200)
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
            return

        self._set_headers(404, "text/plain")
        self.wfile.write(b"Endpoint Not Found")

    def log_message(self, format, *args):
        # Giảm bớt log mặc định để console sáng sủa
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {self.address_string()} - {args[0]}\n")


def run_server(port=5000):
    for p in range(port, port + 10):
        try:
            server_address = ("", p)
            httpd = ThreadedHTTPServer(server_address, AgentUIHandler)
            print("\n" + "="*70)
            print(f"🌟 REACT AGENT OBSERVABILITY DASHBOARD ĐANG CHẠY TẠI:")
            print(f"👉 http://localhost:{p}")
            print(f"👉 http://127.0.0.1:{p}")
            print("="*70 + "\n")
            httpd.serve_forever()
            break
        except OSError as e:
            if "Address already in use" in str(e):
                continue
            else:
                raise e


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    run_server(port)
