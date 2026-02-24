import asyncio
import schedule
import time
import threading
from pyrogram import Client, filters, idle   # ← idle yahan se import
from pyrogram.types import Message

# ────────────────────────────────────────────────
API_ID = 34757634
API_HASH = "70057be15aa6ef11f83e4ca7d2c9bc1a"
SESSION_STRING = "BQISXAIAS2pMQyhBi-UMpNv8VWB9F19EmMwFuuPwkAV7xklsqE5Idxz0yI9FHLF1DM6QgdAzBes70y8_ns_FeXseyGtklumlZ20-QR6iD1_dagP3aNdCanxsuGLXCL3SRH3DvNrbahR1HrNo-2Cv3WzQgHRob-XBtIaIjTRtfb33TMx9HwZUmXMVTQQDoHgTQzQbUMlM-l4TOb9rWWCWmNzbvX1-uE9kHj5-YMgJnw_NVm89Bv03Gme5L8IxK6GDk5b2HZnawtCyd1kxiBg1DoAxtrRtA9yy94yraCa3OxyrY-4me0dnEVgU9KPkz8m9-tKtiktnvB9mytyLdO2YrqjcydUnOQAAAAH4Su13AA"

ADMIN_ID = 1804574038

groups = []
message_text = "Default message 🔥"
timer_sec = 900  # change kar sakta hai
sending = False

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
            "/add <link/@username/-100xxxx>\n"
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
            val = message.command[1].lower()
            try:
                num = int(val[:-1])
                if val.endswith("m"):
                    timer_sec = num * 60
                elif val.endswith("h"):
                    timer_sec = num * 3600
                await message.reply(f"Timer set to {val}")
            except:
                await message.reply("Invalid format! Use like 15m or 1h")

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

async def send_messages():
    if not sending:
        return
    for entity in groups:
        try:
            await app.send_message(entity, message_text)
            print(f"Sent to {entity}")
        except Exception as e:
            print(f"Error sending to {entity}: {e}")

def run_scheduler():
    # Yeh function background thread mein chalega
    # Har timer_sec seconds pe send_messages task schedule karega (main loop mein)
    def job():
        asyncio.create_task(send_messages())  # direct create_task (main loop context assume karta hai)

    schedule.every(timer_sec).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)

async def main():
    await app.start()
    print("Userbot logged in and running (session string se)")

    # Scheduler ko background mein shuru karo
    threading.Thread(target=run_scheduler, daemon=True).start()

    # Client ko alive rakhne ke liye global idle use karo
    await idle()

    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
