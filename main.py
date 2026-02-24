import asyncio
import schedule
import time
import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters, idle
from pyrogram.types import Message

# ────────────────────────────────────────────────
# Tere details (change mat karna)
API_ID = 34757634
API_HASH = "70057be15aa6ef11f83e4ca7d2c9bc1a"
SESSION_STRING = "BQISXAIAS2pMQyhBi-UMpNv8VWB9F19EmMwFuuPwkAV7xklsqE5Idxz0yI9FHLF1DM6QgdAzBes70y8_ns_FeXseyGtklumlZ20-QR6iD1_dagP3aNdCanxsuGLXCL3SRH3DvNrbahR1HrNo-2Cv3WzQgHRob-XBtIaIjTRtfb33TMx9HwZUmXMVTQQDoHgTQzQbUMlM-l4TOb9rWWCWmNzbvX1-uE9kHj5-YMgJnw_NVm89Bv03Gme5L8IxK6GDk5b2HZnawtCyd1kxiBg1DoAxtrRtA9yy94yraCa3OxyrY-4me0dnEVgU9KPkz8m9-tKtiktnvB9mytyLdO2YrqjcydUnOQAAAAH4Su13AA"

ADMIN_ID = 1804574038

# Variables (memory mein rahega, restart pe reset ho jayega)
groups = []                 # group chat IDs ya usernames
message_text = "Hello sabko! Yeh mera auto message hai 🔥"
timer_sec = 900             # 15 minutes default
sending = False

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# Commands (sirf tere private chat se)
@app.on_message(filters.private & filters.user(ADMIN_ID) & filters.command)
async def handle_commands(client, message: Message):
    global groups, message_text, timer_sec, sending
    cmd = message.command[0].lower()

    if cmd in ["start", "help"]:
        await message.reply(
            "**Userbot Commands**\n\n"
            "/add <chat_id / @username / link> → group add karo\n"
            "/setmessage <text> → message change karo\n"
            "/settime <number>m or <number>h → timer set (ex: 15m, 1h)\n"
            "/startsend → sending shuru\n"
            "/stop → band\n"
            "/list → groups list\n"
            "/status → current status"
        )

    elif cmd == "add":
        if len(message.command) < 2:
            await message.reply("Group daalo: /add -1001234567890 ya /add @groupname")
            return
        entity = message.command[1]
        if entity not in groups:
            groups.append(entity)
            await message.reply(f"Added: {entity} (Total: {len(groups)})")
        else:
            await message.reply("Already added")

    elif cmd == "list":
        if not groups:
            await message.reply("Koi group add nahi kiya")
        else:
            await message.reply("Groups:\n" + "\n".join(groups))

    elif cmd == "setmessage":
        if len(message.command) < 2:
            await message.reply("Text daalo: /setmessage Good morning sabko!")
            return
        message_text = " ".join(message.command[1:])
        await message.reply(f"Message set ho gaya:\n{message_text}")

    elif cmd == "settime":
        if len(message.command) < 2:
            await message.reply("Time daalo: /settime 15m ya /settime 1h")
            return
        val = message.command[1].lower()
        try:
            num = int(val[:-1])
            if val.endswith("m"):
                timer_sec = num * 60
            elif val.endswith("h"):
                timer_sec = num * 3600
            else:
                raise ValueError
            await message.reply(f"Timer set: har {num} {val[-1]}")
        except:
            await message.reply("Galat format! Sirf number + m/h")

    elif cmd == "startsend":
        if not message_text.strip() or not groups:
            await message.reply("Pehle message aur groups set karo!")
            return
        sending = True
        await message.reply("✅ Sending shuru ho gaya!")

    elif cmd == "stop":
        sending = False
        await message.reply("⛔ Sending band ho gaya")

    elif cmd == "status":
        await message.reply(
            f"**Status**\n"
            f"Sending: {'ON' if sending else 'OFF'}\n"
            f"Timer: {timer_sec} seconds\n"
            f"Message: {message_text}\n"
            f"Groups: {len(groups)}"
        )

# Auto send function
async def send_messages():
    if not sending:
        return
    for entity in groups:
        try:
            await app.send_message(entity, message_text)
            print(f"Sent to {entity}")
        except Exception as e:
            print(f"Error sending to {entity}: {e}")

# Scheduler background mein
def run_scheduler():
    schedule.every(timer_sec).seconds.do(lambda: asyncio.create_task(send_messages()))
    while True:
        schedule.run_pending()
        time.sleep(1)

# Dummy HTTP server (Render port issue fix ke liye)
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK - Userbot is running")

def start_dummy_server():
    PORT = int(os.getenv("PORT", 10000))  # Render $PORT use karega
    server = HTTPServer(("", PORT), HealthHandler)
    print(f"Dummy server started on port {PORT}")
    server.serve_forever()

# Main function
async def main():
    await app.start()
    print("Userbot logged in and running!")

    # Scheduler shuru
    threading.Thread(target=run_scheduler, daemon=True).start()

    # Dummy server shuru
    threading.Thread(target=start_dummy_server, daemon=True).start()

    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
