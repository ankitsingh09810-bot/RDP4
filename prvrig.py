#!/usr/init/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import threading
import gc
import platform
import psutil
from datetime import datetime
import telebot
from telebot import types
from instagrapi import Client
from instagrapi.exceptions import (
    RateLimitError,
    PleaseWaitFewMinutes,
    ChallengeRequired,
    ClientForbiddenError,
    LoginRequired,
)

# ======================== CONFIG ========================
BOT_TOKEN = "8684651458:AAFSGE0cgk_LZVj0SbNbIDPL62S3DWxumuY"
ADMIN_ID = 6837248644  # Aapki nayi wali Admin/Owner ID

ALLOWED_USERS = {ADMIN_ID}

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# 🔥 UNIFORM TEMPLATE 🔥
BASE_TEMPLATE = """<{TARGET}> Ρʏᴛʜ𝙤𝚗 𝚜є ᴛ𝘳ꪗ ʍꪖꪖ ᴄᴏ∂ʊ ʏᴀ ꫝᴜᴛᴏᴍᱟ 𝘴ᴇ: ̗̀⟼ ﴾⚡﴿





<{TARGET}> Ρʏᴛʜ𝙤𝚗 𝚜є ᴛ𝘳ꪗ ʍꪖꪖ ᴄᴏ∂ʊ ʏᴀ ꫝᴜᴛᴏᴍᱟ 𝘴ᴇ: ̗̀⟼ ﴾💎﴿





<{TARGET}> Ρʏᴛʜ𝙤𝚗 𝚜є ᴛ𝘳ꪗ ʍꪖꪖ ᴄᴏ∂ʊ ʏᴀ ꫝᴜᴛᴏᴍᱟ 𝘴ᴇ: ̗̀⟼ ﴾👑﴿






<{TARGET}> Ρʏᴛʜ𝙤𝚗 𝚜є ᴛ𝘳ꪗ ʍꪖꪖ ᴄᴏ∂ʊ ʏᴀ ꫝᴜᴛᴏᴍᱟ 𝘴ᴇ: ̗̀⟼ ﴾🌌﴿






<{TARGET}> Ρʏᴛʜ𝙤𝚗 𝚜є ᴛ𝘳ꪗ ʍꪖꪖ ᴄᴏ∂ʊ ʏᴀ ꫝᴜᴛᴏᴍᱟ 𝘴ᴇ: ̗̀⟼ ﴾🎯﴿






<{TARGET}> Ρʏᴛʜ𝙤𝚗 𝚜є ᴛ𝘳ꪗ ʍꪖꪖ ᴄᴏ∂ʊ ʏᴀ ꫝᴜᴛᴏᴍᱟ 𝘴ᴇ: ̗̀⟼ ﴾🌊﴿






<{TARGET}> Ρʏᴛʜ𝙤𝚗 𝚜є ᴛ𝘳ꪗ ʍꪖꪖ ᴄᴏ∂ʊ ʏᴀ ꫝᴜᴛᴏᴍᱟ 𝘴ᴇ: ̗̀⟼ ﴾🚀﴿






<{TARGET}> Ρʏᴛʜ𝙤𝚗 𝚜є ᴛ𝘳ꪗ ʍꪖꪖ ᴄᴏ∂ʊ ʏᴀ ꫝᴜᴛᴏᴍᱟ 𝘴ᴇ: ̗̀⟼ ﴾🌪️﴿






<{TARGET}> Ρʏᴛʜ𝙤𝚗 𝚜є ᴛ𝘳ꪗ ʍꪖꪖ ᴄᴏ∂ʊ ʏᴀ ꫝᴜᴛᴏᴍᱟ 𝘴ᴇ: ̗̀⟼ ﴾💫﴿






<{TARGET}> Ρʏᴛʜ𝙤𝚗 𝚜є ᴛ𝘳ꪗ ʍꪖꪖ ᴄᴏ∂ʊ ʏᴀ ꫝᴜᴛᴏᴍᱟ 𝘴ᴇ: ̗̀⟼ ﴾🔥﴿






<{TARGET}> Ρʏᴛʜ𝙤𝚗 𝚜є ᴛ𝘳ꪗ ʍꪖꪖ ᴄᴏ∂ʊ ʏᴀ ꫝᴜᴛᴏᴍᱟ 𝘴ᴇ: ̗̀⟼ ﴾✨﴿"""

MAX_RETRIES = 3

user_setups = {}
active_tasks = {}
GLOBAL_MESSAGES_SENT = 0
BOT_START_TIME = datetime.now()

# ======================== HELPER FUNCTIONS ========================

def is_authorized(user_id):
    return user_id in ALLOWED_USERS

def delete_msg(chat_id, msg_id):
    try:
        bot.delete_message(chat_id, msg_id)
    except:
        pass

def get_system_uptime():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    return str(datetime.now() - boot_time).split('.')[0]

def make_bar(percent, length=10):
    filled = int(round(length * percent / 100))
    return '█' * filled + '░' * (length - filled)


# ======================== LIVE LOG EDITOR ========================

def update_task_log(task_id, event_text):
    task = active_tasks.get(task_id)
    if not task:
        return
    
    chat_id = task["chat_id"]
    target = task["target_name"]
    threads_count = len(task["thread_ids"])
    sent = task.get("msg_count", 0)
    log_msg_id = task.get("log_msg_id")
    
    status_icon = "🟢 RUNNING" if task["running"] else "🛑 STOPPED"
    
    dashboard = (
        f"⚡ <b>HIGH-SPEED TASK [<code>{task_id}</code>]</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Status:</b> {status_icon}\n"
        f"🎯 <b>Target:</b> {target}\n"
        f"🔗 <b>Active GCs:</b> <code>{threads_count} GCs</code>\n"
        f"📨 <b>Total Sent:</b> <code>{sent}</code>\n\n"
        "📝 <b>Live Log:</b>\n"
        f"<i>{event_text}</i>"
    )
    
    if task.get("last_dashboard_text") == dashboard:
        return
    task["last_dashboard_text"] = dashboard

    markup = types.InlineKeyboardMarkup()
    if task["running"]:
        markup.add(types.InlineKeyboardButton(f"🛑 Stop Task", callback_data=f"kill_{task_id}"))
    else:
        markup.add(types.InlineKeyboardButton(f"🗑️ Dismiss", callback_data=f"del_log_{task_id}"))

    try:
        if log_msg_id:
            bot.edit_message_text(dashboard, chat_id, log_msg_id, reply_markup=markup, parse_mode="HTML")
        else:
            msg = bot.send_message(chat_id, dashboard, reply_markup=markup, parse_mode="HTML")
            task["log_msg_id"] = msg.message_id
    except:
        pass


# ======================== INSTAGRAM WORKER ========================

def send_message_with_retry(client, thread_id, message, task_id):
    global GLOBAL_MESSAGES_SENT
    
    for attempt in range(1, MAX_RETRIES + 1):
        if not active_tasks.get(task_id, {}).get("running", False):
            return False

        try:
            client.direct_send(message, thread_ids=[thread_id])
            GLOBAL_MESSAGES_SENT += 1
            active_tasks[task_id]["msg_count"] += 1
            update_task_log(task_id, f"✅ Sent message to GC: <code>{thread_id}</code>")
            return True
        except RateLimitError:
            wait = 60 * attempt
            update_task_log(task_id, f"⚠️ Rate Limit: Resting {wait}s")
            time.sleep(wait)
        except PleaseWaitFewMinutes:
            time.sleep(150)
        except ChallengeRequired:
            update_task_log(task_id, "🔒 Challenge Required! Pausing...")
            time.sleep(1200)
        except (ClientForbiddenError, LoginRequired):
            active_tasks[task_id]["running"] = False
            update_task_log(task_id, "🔐 Session Expired!")
            return False
        except Exception as e:
            time.sleep(10)

    return False

def worker_thread(task_id):
    task = active_tasks[task_id]
    session_id = task["session_id"]
    thread_ids = task["thread_ids"]
    target_name = task["target_name"]
    
    update_task_log(task_id, "🔄 Connecting session for multiple GCs...")
    
    cl = Client()
    try:
        cl.login_by_sessionid(session_id)
        update_task_log(task_id, f"✅ Logged in successfully!")
    except Exception as e:
        task["running"] = False
        update_task_log(task_id, f"❌ Login Failed: {str(e)[:40]}")
        return

    msg_template = BASE_TEMPLATE.replace("{TARGET}", target_name)
    round_num = 0

    thread_msg_counts = {tid: 0 for tid in thread_ids}
    current_group_titles = {tid: target_name for tid in thread_ids}

    while task.get("running", False):
        try:
            round_num += 1
            update_task_log(task_id, f"🔄 Running Loop Round {round_num}...")

            for thread_id in thread_ids:
                if not task.get("running", False):
                    break

                # Footer with dynamic timer and signature
                current_time = datetime.now().strftime("%H:%M:%S")
                footer_signature = f"ꜱᴄʀɪᴩᴛ ᴍᴀᴅᴇ ʙʏ 𝐀ɴᴋɪᴛ अब्बू  [{current_time}]"
                
                full_msg = f"{msg_template}\n\n{footer_signature}"

                success = send_message_with_retry(cl, thread_id, full_msg, task_id)
                
                if success:
                    thread_msg_counts[thread_id] += 1

                # 🔥 EVERY 10 MESSAGES -> AUTO NC CHANGE WITH RANDOM EMOJI 🔥
                if thread_msg_counts[thread_id] >= 10:
                    try:
                        rand_emoji = random.choice(["🔥", "⚡", "💎", "👑", "🚀", "💀", "🌪️", "💫", "🎯", "🗿", "🧨", "🌀", "⭐", "🔥"])
                        new_nc = f"<{target_name}>𝖲ʟᴀꪜɛꜱ 𝖢ꪊ𝖣𝖗ꪖɪ {rand_emoji}"
                        
                        if new_nc != current_group_titles.get(thread_id):
                            cl.direct_thread_update_title(thread_id, new_nc)
                            current_group_titles[thread_id] = new_nc
                            update_task_log(task_id, f"🔄 NC Updated on GC <code>{thread_id}</code>")
                    except Exception as nc_err:
                        pass
                    
                    thread_msg_counts[thread_id] = 0

                delay = random.uniform(8, 14)
                time.sleep(delay)

            gc.collect()

        except Exception as e:
            time.sleep(30)

    update_task_log(task_id, "🛑 Task safely stopped.")
    gc.collect()


# ======================== INTERACTIVE UI ========================

def send_main_menu(chat_id, msg_to_edit=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🚀 Start High-Speed Task", callback_data="menu_start"),
        types.InlineKeyboardButton("📊 System RAM/CPU", callback_data="menu_status")
    )
    if chat_id == ADMIN_ID:
        markup.add(types.InlineKeyboardButton("⚙️ Admin Info", callback_data="menu_admin"))
        
    text = "👑 <b>ANKIT CONTROL PANEL</b>\nSelect an option below:"
    
    if msg_to_edit:
        bot.edit_message_text(text, chat_id, msg_to_edit, reply_markup=markup, parse_mode="HTML")
    else:
        msg = bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
        user_setups[chat_id] = {"menu_id": msg.message_id}

@bot.message_handler(commands=["start", "menu"])
def cmd_menu(message):
    delete_msg(message.chat.id, message.message_id)
    if not is_authorized(message.from_user.id):
        return bot.send_message(message.chat.id, "⛔ <b>Access Denied.</b>")
    send_main_menu(message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if not is_authorized(call.from_user.id):
        return bot.answer_callback_query(call.id, "⛔ Access Denied.", show_alert=True)
        
    menu_id = call.message.message_id

    if call.data == "menu_start":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Cancel", callback_data="menu_back"))
        bot.edit_message_text("👋 <b>Setup Wizard:</b>\n\nPaste your Instagram <b>sessionid</b> cookie:", chat_id, menu_id, reply_markup=markup, parse_mode="HTML")
        user_setups[chat_id] = {"menu_id": menu_id, "step": "session"}
        bot.register_next_step_handler_by_chat_id(chat_id, setup_flow)
        
    elif call.data == "menu_status":
        cpu_usage = psutil.cpu_percent(interval=0.2)
        ram = psutil.virtual_memory()
        
        active_count = len([t for t in active_tasks.values() if t["running"]])
        
        dashboard = (
            "🖥️ <b>RDP PERFORMANCE MONITOR</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚙️ <b>CPU Usage:</b> {make_bar(cpu_usage)} {cpu_usage}%\n"
            f"🧠 <b>RAM Usage:</b> {make_bar(ram.percent)} {ram.percent}%\n"
            f"⚡ <b>Active Tasks:</b> <code>{active_count}</code>\n"
            f"📨 <b>Global Sent:</b> <code>{GLOBAL_MESSAGES_SENT}</code>"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="menu_back"))
        bot.edit_message_text(dashboard, chat_id, menu_id, reply_markup=markup, parse_mode="HTML")
        
    elif call.data == "menu_admin":
        text = f"⚙️ <b>Admin Config:</b>\n\nOwner ID: <code>{ADMIN_ID}</code>\nStatus: Online & Optimized."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="menu_back"))
        bot.edit_message_text(text, chat_id, menu_id, reply_markup=markup, parse_mode="HTML")

    elif call.data == "menu_back":
        bot.clear_step_handler_by_chat_id(chat_id)
        send_main_menu(chat_id, menu_id)
        
    elif call.data.startswith("kill_"):
        tid = call.data.split("_")[1]
        if tid in active_tasks:
            active_tasks[tid]["running"] = False
            update_task_log(tid, "🛑 Force stopping task...")
            bot.answer_callback_query(call.id, "Stopping Task...", show_alert=False)

    elif call.data.startswith("del_log_"):
        bot.delete_message(chat_id, call.message.message_id)


# ======================== SETUP FLOW ========================

def setup_flow(message):
    chat_id = message.chat.id
    delete_msg(chat_id, message.message_id)
    
    if chat_id not in user_setups:
        return
        
    step = user_setups[chat_id].get("step")
    menu_id = user_setups[chat_id].get("menu_id")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Cancel", callback_data="menu_back"))

    if message.text.startswith("/"):
        bot.clear_step_handler_by_chat_id(chat_id)
        send_main_menu(chat_id, menu_id)
        return

    if step == "session":
        user_setups[chat_id]["session_id"] = message.text.strip()
        bot.edit_message_text("📋 <b>Setup:</b>\n\nEnter <b>Thread ID(s)</b>:\n<i>(Comma separated)</i>", chat_id, menu_id, reply_markup=markup, parse_mode="HTML")
        user_setups[chat_id]["step"] = "threads"
        bot.register_next_step_handler_by_chat_id(chat_id, setup_flow)

    elif step == "threads":
        thread_ids = [int(t.strip()) for t in message.text.split(",") if t.strip().isdigit()]
        if not thread_ids:
            bot.edit_message_text("❌ <b>Error:</b> No valid numbers found. Enter Thread IDs:", chat_id, menu_id, reply_markup=markup, parse_mode="HTML")
            bot.register_next_step_handler_by_chat_id(chat_id, setup_flow)
            return

        user_setups[chat_id]["thread_ids"] = thread_ids
        bot.edit_message_text("🎯 <b>Setup:</b>\n\nEnter the <b>Target Name</b>:", chat_id, menu_id, reply_markup=markup, parse_mode="HTML")
        user_setups[chat_id]["step"] = "target"
        bot.register_next_step_handler_by_chat_id(chat_id, setup_flow)

    elif step == "target":
        target_name = message.text.strip()
        task_id = f"T{random.randint(1000, 9999)}"
        
        active_tasks[task_id] = {
            "chat_id": chat_id,
            "session_id": user_setups[chat_id]["session_id"],
            "thread_ids": user_setups[chat_id]["thread_ids"],
            "target_name": target_name,
            "running": True,
            "msg_count": 0,
            "log_msg_id": None
        }

        bot.clear_step_handler_by_chat_id(chat_id)
        send_main_menu(chat_id, menu_id)
        
        threading.Thread(target=worker_thread, args=(task_id,), daemon=True).start()


if __name__ == "__main__":
    print("[ANKIT BOT] Online with Updated Admin ID! 👑 (Owner: Ankit अब्बू)")
    try:
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n[!] Exited by user.")
        sys.exit(0)
    
