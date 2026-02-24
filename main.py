import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 34757634
API_HASH = "70057be15aa6ef11f83e4ca7d2c9bc1a"
SESSION_STRING = "BQISXAIAS2pMQyhBi-UMpNv8VWB9F19EmMwFuuPwkAV7xklsqE5Idxz0yI9FHLF1DM6QgdAzBes70y8_ns_FeXseyGtklumlZ20-QR6iD1_dagP3aNdCanxsuGLXCL3SRH3DvNrbahR1HrNo-2Cv3WzQgHRob-XBtIaIjTRtfb33TMx9HwZUmXMVTQQDoHgTQzQbUMlM-l4TOb9rWWCWmNzbvX1"

ADMIN_ID = 1804574038

groups = set()
message_text = "Default message 🔥"
timer_sec = 900
sending = False

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# ================= BUTTON PANEL =================

def main_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add This Group", callback_data="add")],
        [InlineKeyboardButton("▶ Start Sending", callback_data="start")],
        [InlineKeyboardButton("⛔ Stop Sending", callback_data="stop")],
        [InlineKeyboardButton("📊 Status", callback_data="status")]
    ])

@app.on_message(filters.private & filters.user(ADMIN_ID) & filters.command("start"))
async def start_panel(client, message):
    await message.reply(
        "🔥 Userbot Control Panel",
        reply_markup=main_buttons()
    )

# ================= CALLBACK =================

@app.on_callback_query(filters.user(ADMIN_ID))
async def callbacks(client, callback_query):
    global sending

    data = callback_query.data

    if data == "start":
        sending = True
        await callback_query.answer("Started ✅")

    elif data == "stop":
        sending = False
        await callback_query.answer("Stopped ⛔")

    elif data == "status":
        await callback_query.message.reply(
            f"Sending: {sending}\n"
            f"Groups: {len(groups)}\n"
            f"Timer: {timer_sec}s\n"
            f"Message: {message_text}"
        )

    await callback_query.answer()

# ================= AUTO GROUP TARGET =================

@app.on_message(filters.group & filters.command("startsend") & filters.user(ADMIN_ID))
async def auto_add_group(client, message):
    chat_id = message.chat.id
    groups.add(chat_id)
    await message.reply("✅ This group added to auto sending list")

# ================= SET MESSAGE =================

@app.on_message(filters.private & filters.command("setmessage") & filters.user(ADMIN_ID))
async def set_msg(client, message):
    global message_text
    message_text = " ".join(message.command[1:])
    await message.reply("Message updated ✅")

# ================= SCHEDULER LOOP =================

async def scheduler_loop():
    global sending
    while True:
        if sending:
            for chat_id in groups:
                try:
                    await app.send_message(chat_id, message_text)
                except Exception as e:
                    print(e)
        await asyncio.sleep(timer_sec)

# ================= MAIN =================

async def main():
    await app.start()
    print("OK - Userbot is running")
    asyncio.create_task(scheduler_loop())
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
