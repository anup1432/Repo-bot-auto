import asyncio
import schedule
import time
import threading
from pyrogram import Client, filters
from pyrogram.types import Message

# ────────────────────────────────────────────────
# Tere details + SESSION STRING (ab OTP nahi maangega)
API_ID = 34757634
API_HASH = "70057be15aa6ef11f83e4ca7d2c9bc1a"
SESSION_STRING = "BQISXAIAS2pMQyhBi-UMpNv8VWB9F19EmMwFuuPwkAV7xklsqE5Idxz0yI9FHLF1DM6QgdAzBes70y8_ns_FeXseyGtklumlZ20-QR6iD1_dagP3aNdCanxsuGLXCL3SRH3DvNrbahR1HrNo-2Cv3WzQgHRob-XBtIaIjTRtfb33TMx9HwZUmXMVTQQDoHgTQzQbUMlM-l4TOb9rWWCWmNzbvX1-uE9kHj5-YMgJnw_NVm89Bv03Gme5L8IxK6GDk5b2HZnawtCyd1kxiBg1DoAxtrRtA9yy94yraCa3OxyrY-4me0dnEVgU9KPkz8m9-tKtiktnvB9mytyLdO2YrqjcydUnOQAAAAH4Su13AA"

ADMIN_ID = 1804574038

# Memory values (restart pe reset ho jayenge)
groups = []
message_text = "Default message 🔥"
timer_sec = 900  # 15 min default
sending = False

# Client ab session string se login karega
app = Client(
    "my_userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

@app.on_message(filters.private & filters.user(ADMIN_ID) & filters.command)
async def handle(client, message: Message):
    global groups, message_text, timer_sec, sending
    cmd = message.command[0].lower()

    if cmd in ["start", "help"]:
        await message.reply(
            "Commands:\n"
            "/add <link or @username or -100xxxx>\n"
            "/setmessage <text>\n"
            "/settime 15m or 1h\n"
            "/startsend\n"
            "/stop\n"
            "/list\n"
            "/status"
        )

    elif cmd == "add":
        if len(message.command) > 1:
            entity = message.command[1]
            if entity not in groups:
                groups.append(entity)
                await message.reply(f"Added: {entity}")
            else:
                await message.reply("Already added")

    elif cmd == "list":
        await message.reply("\n".join(groups) or "No groups added")

    elif cmd == "setmessage":
        if len(message.command) > 1:
            message_text = " ".join(message.command[1:])
            await message.reply(f"Message set: {message_text}")

    elif cmd == "settime":
        if len(message.command) > 1:
            val = message.command[1]
            try:
                if val.endswith("m"):
                    timer_sec = int(val[:-1]) * 60
                elif val.endswith("h"):
                    timer_sec = int(val[:-1]) * 3600
                await message.reply(f"Timer set to {val}")
            except:
                await message.reply("Invalid format! Example: 15m or 1h")

    elif cmd == "startsend":
        if not message_text.strip() or not groups:
            await message.reply("Pehle message aur groups set karo!")
            return
        sending = True
        await message.reply("Started ✅")

    elif cmd == "stop":
        sending = False
        await message.reply("Stopped ⛔")

    elif cmd == "status":
        await message.reply(
            f"Sending: {sending}\n"
            f"Timer: {timer_sec} seconds\n"
            f"Message: {message_text}\n"
            f"Groups: {len(groups)}"
        )

async def send_task():
    if not sending:
        return
    for g in groups:
        try:
            await app.send_message(g, message_text)
            print(f"Sent to {g}")
        except Exception as e:
            print(f"Send error to {g}: {e}")

def scheduler():
    loop = asyncio.get_running_loop()
    def job():
        loop.call_soon_threadsafe(lambda: asyncio.create_task(send_task()))
    schedule.every(timer_sec).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

async def main():
    await app.start()
    print("Userbot logged in and running (session string se)")
    threading.Thread(target=scheduler, daemon=True).start()
    await app.idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
