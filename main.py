import asyncio
import schedule
import time
import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters, idle
from pyrogram.types import Message

# ────────────────────────────────────────────────
API_ID = 34757634
API_HASH = "70057be15aa6ef11f83e4ca7d2c9bc1a"
SESSION_STRING = "BQISXAIAS2pMQyhBi-UMpNv8VWB9F19EmMwFuuPwkAV7xklsqE5Idxz0yI9FHLF1DM6QgdAzBes70y8_ns_FeXseyGtklumlZ20-QR6iD1_dagP3aNdCanxsuGLXCL3SRH3DvNrbahR1HrNo-2Cv3WzQgHRob-XBtIaIjTRtfb33TMx9HwZUmXMVTQQDoHgTQzQbUMlM-l4TOb9rWWCWmNzbvX1-uE9kHj5-YMgJnw_NVm89Bv03Gme5L8IxK6GDk5b2HZnawtCyd1kxiBg1DoAxtrRtA9yy94yraCa3OxyrY-4me0dnEVgU9KPkz8m9-tKtiktnvB9mytyLdO2YrqjcydUnOQAAAAH4Su13AA"

ADMIN_ID = 1804574038

groups = []
message_text = "Default message 🔥"
timer_sec = 900
sending = False

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# Telegram commands (same as before)
@app.on_message(filters.private & filters.user(ADMIN_ID) & filters.command)
async def handle(client, message: Message):
    global groups, message_text, timer_sec, sending
    cmd = message.command[0].lower()

    if cmd in ["start", "help"]:
        await message.reply("Commands:\n/add <link or chat ID>\n/setmessage <text>\n/settime 15m\n/startsend\n/stop\n/list\n/status")

    elif cmd == "add":
        if len(message.command) > 1:
            entity = message.command[1]
            if entity not in groups:
                groups.append(entity)
                await message.reply(f"Added {entity}")
            else:
                await message.reply("Already added")

    elif cmd == "list":
        await message.reply("\n".join(groups) or "No groups")

    elif cmd == "setmessage":
        if len(message.command) > 1:
            message_text = " ".join(message.command[1:])
            await message.reply(f"Message set: {message_text}")

    elif cmd == "settime":
        if len(message.command) > 1:
            val = message.command[1].lower()
            try:
                num = int(val[:-1])
                if val.endswith("m"):
                    timer_sec = num * 60
                elif val.endswith("h"):
                    timer_sec = num * 3600
                await message.reply(f"Timer set to {val}")
            except:
                await message.reply("Invalid format")

    elif cmd == "startsend":
        if not message_text.strip() or not groups:
            await message.reply("Set message and groups first!")
            return
        sending = True
        await message.reply("Started ✅")

    elif cmd == "stop":
        sending = False
        await message.reply("Stopped ⛔")

    elif cmd == "status":
        await message.reply(f"Sending: {sending}\nTimer: {timer_sec}s\nMessage: {message_text}\nGroups: {len(groups)}")

async def send_messages():
    if not sending:
        return
    for entity in groups:
        try:
            await app.send_message(entity, message_text)
            print(f"Sent to {entity}")
        except Exception as e:
            print(f"Error: {e}")

def run_scheduler():
    schedule.every(timer_sec).seconds.do(lambda: asyncio.create_task(send_messages()))
    while True:
        schedule.run_pending()
        time.sleep(1)

# Dummy HTTP server to satisfy Render port check
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK - Userbot is alive")

def start_http():
    port = int(os.getenv("PORT", 10000))  # Render PORT env var use karega
    server = HTTPServer(("", port), HealthCheckHandler)
    print(f"Dummy server started on port {port}")
    server.serve_forever()

async def main():
    await app.start()
    print("Userbot logged in")

    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=start_http, daemon=True).start()

    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
