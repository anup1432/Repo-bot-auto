import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ────────────────────────────────────────────────
API_ID = 34757634
API_HASH = "70057be15aa6ef11f83e4ca7d2c9bc1a"
SESSION_STRING = "BQISXAIAS2pMQyhBi-UMpNv8VWB9F19EmMwFuuPwkAV7xklsqE5Idxz0yI9FHLF1DM6QgdAzBes70y8_ns_FeXseyGtklumlZ20-QR6iD1_dagP3aNdCanxsuGLXCL3SRH3DvNrbahR1HrNo-2Cv3WzQgHRob-XBtIaIjTRtfb33TMx9HwZUmXMVTQQDoHgTQzQbUMlM-l4TOb9rWWCWmNzbvX1-uE9kHj5-YMgJnw_NVm89Bv03Gme5L8IxK6GDk5b2HZnawtCyd1kxiBg1DoAxtrRtA9yy94yraCa3OxyrY-4me0dnEVgU9KPkz8m9-tKtiktnvB9mytyLdO2YrqjcydUnOQAAAAH4Su13AA"

ADMIN_ID = 1804574038

groups = []               # list of chat IDs (groups)
message_text = "Default message 🔥"
timer_sec = 900           # 15 minutes
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
        [InlineKeyboardButton("➕ Add This Group", callback_data="add_current")],
        [InlineKeyboardButton("▶ Start Sending", callback_data="start")],
        [InlineKeyboardButton("⛔ Stop Sending", callback_data="stop")],
        [InlineKeyboardButton("📊 Status", callback_data="status")]
    ])

@app.on_message(filters.private & filters.user(ADMIN_ID) & filters.command("start"))
async def start_panel(client, message):
    await message.reply(
        "**🔥 Userbot Control Panel**\n\nUse buttons below to control:",
        reply_markup=main_buttons()
    )

# ================= CALLBACK QUERIES =================
@app.on_callback_query(filters.user(ADMIN_ID))
async def callbacks(client, callback_query):
    global sending

    data = callback_query.data

    if data == "start":
        if not groups:
            await callback_query.answer("No groups added yet!", show_alert=True)
            return
        sending = True
        await callback_query.answer("Sending started ✅")

    elif data == "stop":
        sending = False
        await callback_query.answer("Sending stopped ⛔")

    elif data == "status":
        status_text = (
            f"**Status**\n"
            f"Sending: {'ON' if sending else 'OFF'}\n"
            f"Timer interval: {timer_sec // 60} minutes\n"
            f"Message: {message_text}\n"
            f"Groups count: {len(groups)}"
        )
        await callback_query.message.reply(status_text)

    elif data == "add_current":
        # Yeh button sirf private mein hai, current group add nahi kar sakta
        await callback_query.answer("Use /add <chat_id> or add in group", show_alert=True)

    await callback_query.answer()

# ================= AUTO ADD GROUP (group mein command se) =================
@app.on_message(filters.group & filters.command("addme") & filters.user(ADMIN_ID))
async def add_group(client, message):
    chat_id = message.chat.id
    if chat_id not in groups:
        groups.append(chat_id)
        await message.reply("✅ This group added to auto-sending list")
    else:
        await message.reply("Already added")

# ================= SET MESSAGE =================
@app.on_message(filters.private & filters.command("setmessage") & filters.user(ADMIN_ID))
async def set_msg(client, message):
    global message_text
    if len(message.command) < 2:
        await message.reply("Usage: /setmessage Your message here")
        return
    message_text = " ".join(message.command[1:])
    await message.reply(f"Message updated:\n{message_text}")

# ================= SET TIMER =================
@app.on_message(filters.private & filters.command("settime") & filters.user(ADMIN_ID))
async def set_time(client, message):
    global timer_sec
    if len(message.command) < 2:
        await message.reply("Usage: /settime 15m or /settime 1h")
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
        await message.reply(f"Timer set to {num} {val[-1]}")
    except:
        await message.reply("Invalid format. Use 15m or 1h etc.")

# ================= SCHEDULER LOOP =================
async def scheduler_loop():
    global sending
    while True:
        if sending and groups:
            for chat_id in groups:
                try:
                    await app.send_message(chat_id, message_text)
                    print(f"Sent to {chat_id}")
                except Exception as e:
                    print(f"Error sending to {chat_id}: {e}")
                    # Optional: groups.remove(chat_id) agar invalid chat ho
        await asyncio.sleep(timer_sec)

# ================= MAIN =================
async def main():
    await app.start()
    print("OK - Userbot is running")
    asyncio.create_task(scheduler_loop())
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
