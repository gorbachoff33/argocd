import socketserver
import http.server
import socket
import urllib.parse
import time
import threading

SQUID_PORTS = list(range(3128, 3148))  # 20 портов
DELAY_SECONDS = 1.8
LOCK = threading.Lock()
last_used = {}

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        self.send_error(405, "CONNECT not supported in this proxy")
        return

    def do_GET(self):
        self.handle_http_proxy()

    def do_POST(self):
        self.handle_http_proxy()

    def handle_http_proxy(self):
        parser_id = self.headers.get("X-Parser-ID", "default")
        squid_port = self.select_port(parser_id)

        try:
            # Вместо подключения к Squid — просто выводим отладочную информацию
            print(f"[DEBUG] Would connect to Squid on port {squid_port} for parser '{parser_id}'")

            # Отправляем простой HTTP-ответ клиенту
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"Selected port: {squid_port}\n".encode())
            return

            # --- ОРИГИНАЛЬНЫЙ КОД: закомментирован ---
            # target = self.path
            # parsed = urllib.parse.urlsplit(target)
            # host = parsed.hostname
            # port = parsed.port or 80
            #
            # with socket.create_connection(("127.0.0.1", squid_port)) as proxy_sock:
            #     request_line = f"{self.command} {target} {self.request_version}\r\n"
            #     proxy_sock.sendall(request_line.encode())
            #
            #     for header, value in self.headers.items():
            #         proxy_sock.sendall(f"{header}: {value}\r\n".encode())
            #     proxy_sock.sendall(b"\r\n")
            #
            #     if "Content-Length" in self.headers:
            #         content_length = int(self.headers["Content-Length"])
            #         body = self.rfile.read(content_length)
            #         proxy_sock.sendall(body)
            #
            #     self.forward(self.connection, proxy_sock)
            # --- КОНЕЦ ОРИГИНАЛА ---

        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")


    def select_port(self, parser_id):
        base_index = abs(hash(parser_id)) % len(SQUID_PORTS)
        while True:
            now = time.time()
            for i in range(len(SQUID_PORTS)):
                port = SQUID_PORTS[(base_index + i) % len(SQUID_PORTS)]
                print(f"[{parser_id}] trying port {port}, last_used = {last_used.get((parser_id, port), 0):.2f}, now = {now:.2f}")
                if self.port_available(parser_id, port, now):
                    self.mark_port_used(parser_id, port, now)
                    return port

    def port_available(self, parser_id, port, now):
        key = (parser_id, port)
        with LOCK:
            last = last_used.get(key, 0)
            return now - last >= DELAY_SECONDS

    def mark_port_used(self, parser_id, port, now):
        with LOCK:
            last_used[(parser_id, port)] = now
        print(f"[{parser_id}] using port {port} at time {now:.2f}")

    def forward(self, client_sock, server_sock):
        def pipe(src, dst):
            try:
                while True:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.sendall(data)
            finally:
                try: dst.shutdown(socket.SHUT_RDWR)
                except: pass
                dst.close()

        threading.Thread(target=pipe, args=(client_sock, server_sock)).start()
        pipe(server_sock, client_sock)

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(("0.0.0.0", 8080), ProxyHandler)
    print("Proxy-router (HTTP, wait mode) started on port 8080")
    server.serve_forever()