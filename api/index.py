from http.server import BaseHTTPRequestHandler
import os
import json
import requests

# Vercel Serverless Function
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Allow browser visits to check if the bot is running
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Portfolio Bot is running! Send a POST request with JSON data to trigger.".encode('utf-8'))

    def do_POST(self):
        # 1. Get Secrets from Environment
        BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
        CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

        # 2. Parse Incoming JSON
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            # Extract fields (matching your n8n logic)
            name = body.get("name", "Unbekannt")
            email = body.get("email", "Keine Email")
            subject = body.get("subject", "(kein Betreff)")
            message = body.get("message", "")

            # Validation
            if not message:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Message is required"}).encode('utf-8'))
                return

        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
            return

        # 3. Formulate Telegram Message
        text = f"""Sie haben eine Nachricht erhalten 😁😁😁
Email: {email}

Betreff: {subject}

Nachricht: 
{message}"""

        # 4. Send to Telegram
        if BOT_TOKEN and CHAT_ID:
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": text
            }
            try:
                r = requests.post(telegram_url, json=payload)
                r.raise_for_status()
                # Success
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
            except Exception as e:
                # Telegram Error
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Telegram Error: {str(e)}".encode('utf-8'))
        else:
             # Config Error
            self.send_response(500)
            self.end_headers()
            self.wfile.write("Server Configuration Error: Missing Secrets".encode('utf-8'))

    def do_OPTIONS(self):
        # CORS support for your website
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
