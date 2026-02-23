import asyncio
import schedule
import time
import threading
from pyrogram import Client, filters
from pyrogram.types import Message

# Tere credentials (sensitive mat share karna kahin)
API_ID = 34757634
API_HASH = "70057be15aa6ef11f83e4ca7d2c9bc1a"
PHONE = "+919724450019"

ADMIN_ID = 1804574038

# Memory mein store (restart pe reset ho jayega, Render pe har deploy pe fresh start hota hai)
groups = []  # groups ya persons ke entities
message_text = "Default auto message from userbot! 🚀"
timer_sec = 900  # 15 min default
sending = False

app = Client("userbot_session", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE)

@app.on_message(filters.private & filters.user(ADMIN_ID) & filters.command)
async def commands_handler(client, message: Message):
    global groups, message_text, timer_sec, sending

    cmd = message.command[0].lower()

    if cmd in ["start", "help"]:
        await message.reply(
            "**Userbot Commands (sirf private mein):**\n"
            "/add <group link / @username / chat ID> → add group/person\n"
            "/setmessage <text> → message set kar\n"
            "/settime <number>m / <number>h → timer set (ex: 10m, 1h)\n"
            "/startsend → sending ON\n"
            "/stop → sending OFF\n"
            "/list → groups list\n"
            "/status → current setup check\n"
            "/clear → sab groups remove"
        )

    elif cmd == "add":
        if len(message.command) < 2:
            await message.reply("Entity do: /add https://t.me/+abc OR /add @groupname")
            return
        entity = message.command[1]
        if entity not in groups:
            groups.append(entity)
            await message.reply(f"Added: {entity} | Total: {len(groups)}")
        else:
            await message.reply("Already added")

    elif cmd == "list":
        if not groups:
            await message.reply("No groups added yet")
        else:
            await message.reply("Groups:\n" + "\n".join(groups))

    elif cmd == "setmessage":
        if len(message.command) < 2:
            await message.reply("Text do: /setmessage Hello everyone!")
            return
        message_text = " ".join(message.command[1:])
        await message.reply(f"Message set:\n{message_text}")

    elif cmd == "settime":
        if len(message.command) < 2:
            await message.reply("Format: /settime 15m ya /settime 2h")
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
            await message.reply(f"Timer: every {num} {val[-1]} ({timer_sec}s)")
        except:
            await message.reply("Invalid! Sirf number + m/h")

    elif cmd == "startsend":
        if not message_text or not groups:
            await message.reply("Pehle message aur groups set kar!")
            return
        sending = True
        await message.reply("Sending STARTED ✅")

    elif cmd == "stop":
        sending = False
        await message.reply("Sending STOPPED ⛔")

    elif cmd == "status":
        await message.reply(
            f"Status:\n"
            f"Message: {message_text}\n"
            f"Timer: {timer_sec}s\n"
            f"Sending: {'ON' if sending else 'OFF'}\n"
            f"Groups: {len(groups)}"
        )

    elif cmd == "clear":
        groups = []
        await message.reply("All groups cleared!")

async def auto_send():
    if not sending:
        return
    for entity in groups[:]:  # copy to avoid modification issues
        try:
            await app.send_message(entity, message_text)
            print(f"Sent to {entity}")
        except Exception as e:
            print(f"Error to {entity}: {e}")
            # Optional: agar group invalid ho toh remove kar sakte ho groups.remove(entity)

def run_schedule():
    schedule.every(timer_sec).seconds.do(lambda: asyncio.run_coroutine_threadsafe(auto_send(), asyncio.get_event_loop()))
    while True:
        schedule.run_pending()
        time.sleep(1)

async def main():
    await app.start()
    print("Userbot started on Render!")
    threading.Thread(target=run_schedule, daemon=True).start()
    await app.idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
