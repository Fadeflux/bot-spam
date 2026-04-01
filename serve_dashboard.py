"""
Serveur Web Simple pour le Dashboard
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys

class MyHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Ajoute les headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super().end_headers()

    def log_message(self, format, *args):
        # Format personnalisé des logs
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    
    print("\n" + "="*70)
    print("  [UI] DASHBOARD WEB SERVER")
    print("="*70)
    print("\n  URL: http://localhost:8000/dashboard.html")
    print("  API: http://localhost:5000")
    print("\n" + "="*70 + "\n")
    
    server = HTTPServer(("localhost", 8000), MyHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[OK] Serveur arrete.")
        sys.exit(0)
