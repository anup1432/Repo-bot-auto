import asyncio
import schedule
import time
from pyrogram import Client, filters
from pyrogram.types import Message

# ────────────────────────────────────────────────
API_ID = 34757634
API_HASH = "70057be15aa6ef11f83e4ca7d2c9bc1a"
PHONE = "+919724450019"

ADMIN_ID = 1804574038

# Memory values (har restart pe reset, session se login rahega)
groups = []
message_text = "Default message 🔥"
timer_sec = 900  # 15 min
sending = False

app = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE)

@app.on_message(filters.private & filters.user(ADMIN_ID) & filters.command)
async def handle(client, message: Message):
    global groups, message_text, timer_sec, sending
    cmd = message.command[0].lower()

    if cmd in ["start", "help"]:
        await message.reply("Commands:\n/add <link>\n/setmessage <text>\n/settime 15m\n/startsend\n/stop\n/list\n/status")

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
            await message.reply(f"Set: {message_text}")

    elif cmd == "settime":
        if len(message.command) > 1:
            val = message.command[1]
            try:
                if val.endswith("m"):
                    timer_sec = int(val[:-1]) * 60
                elif val.endswith("h"):
                    timer_sec = int(val[:-1]) * 3600
                await message.reply(f"Timer: {val}")
            except:
                await message.reply("Invalid format")

    elif cmd == "startsend":
        sending = True
        await message.reply("Started")

    elif cmd == "stop":
        sending = False
        await message.reply("Stopped")

    elif cmd == "status":
        await message.reply(f"Sending: {sending}\nTimer: {timer_sec}s\nGroups: {len(groups)}")

async def send_task():
    if not sending:
        return
    for g in groups:
        try:
            await app.send_message(g, message_text)
        except Exception as e:
            print(f"Send error: {e}")

def scheduler():
    # Schedule ko loop ke andar schedule karo
    loop = asyncio.get_running_loop()
    def job():
        loop.call_soon_threadsafe(lambda: asyncio.create_task(send_task()))
    schedule.every(timer_sec).seconds.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)

async def main():
    await app.start()
    print("Userbot logged in and running")
    import threading
    threading.Thread(target=scheduler, daemon=True).start()
    await app.idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
