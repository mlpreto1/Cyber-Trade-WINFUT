# agents_pixel_server.py
# Servidor HTTP para interface pixel dos agentes

import http.server
import socketserver
import threading
import logging
import os
from pathlib import Path

logger = logging.getLogger("pixel_server")

_BASE_DIR = Path(__file__).parent
HTML_PATH = str(_BASE_DIR / "agents.html")
PORT = 8765


def start_server(port: int = PORT):
    def generate_html() -> str:
        if not os.path.exists(HTML_PATH):
            return """<!DOCTYPE html>
<html><head><title>Cyber Trade</title></head>
<body style="background:#0a0a0a;color:#00ff00;font-family:monospace;text-align:center;padding:50px;">
<h1>⏳ AGUARDANDO DADOS...</h1>
<p>Agents.html sera gerado em breve</p>
</body></html>"""
        
        with open(HTML_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/' or self.path == '/agents':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Refresh', '3')
                self.end_headers()
                content = generate_html()
                self.wfile.write(content.encode('utf-8'))
            else:
                self.send_error(404)
        
        def log_message(self, format, *args):
            pass
    
    os.chdir(_BASE_DIR)
    
    with socketserver.TCPServer(("", port), Handler) as httpd:
        logger.info(f"🎮 Pixel Agents: http://localhost:{port}")
        httpd.serve_forever()


def start_in_thread(port: int = PORT):
    t = threading.Thread(target=start_server, args=(port,), daemon=True)
    t.start()
    logger.info(f"[PIXEL] Server started on port {port}")
    return t


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(f"🚀 Pixel Agents Server: http://localhost:{PORT}")
    start_server(PORT)