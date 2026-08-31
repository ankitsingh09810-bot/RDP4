import asyncio
import json
import logging
import random
import psutil
from pathlib import Path
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

print("=" * 60)
print("     🔥 ANKIT GOD SCRIPT (ULTIMATE OPTIONS EDITION) 🔥     ")
print("=" * 60)

logging.basicConfig(format='%(asctime)s - [ANKIT_GOD] - %(levelname)s - %(message)s', level=logging.INFO)

ACCOUNTS_FILE  = Path.cwd() / "ankit_aws_accounts.json"
CONFIG_FILE    = Path.cwd() / "ankit_aws_config.json"

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
]

user_states = {}
temp_account_data = {}
active_spammer = None

class BotConfigManager:
    def __init__(self):
        self.config = self._load()

    def _load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f: return json.load(f)
            except: pass
        return {"target": "ANKIT", "delay_min": 2.0, "delay_max": 4.5, "mode": "multiple"}

    def save(self):
        with open(CONFIG_FILE, 'w') as f: json.dump(self.config, f, indent=2)

config_mgr = BotConfigManager()

class AWSAccountManager:
    def __init__(self):
        self.accounts = self._load()

    def _load(self):
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, 'r') as f: return json.load(f)
            except: return []
        return []

    def _save(self):
        with open(ACCOUNTS_FILE, 'w') as f: json.dump(self.accounts, f, indent=2)

    def add(self, username, password=None, sessionid=None):
        for acc in self.accounts:
            if acc['username'] == username:
                if password: acc['password'] = password
                if sessionid: acc['sessionid'] = sessionid
                self._save()
                return True

        self.accounts.append({
            'username': username, 
            'password': password,
            'sessionid': sessionid,
            'assigned_gcs': [],
            'link_type': 'invite' # invite, thread_id, thread_num
        })
        self._save()
        return True

    def remove(self, username):
        self.accounts = [a for a in self.accounts if a['username'] != username]
        self._save()

    def get_all(self):
        return self.accounts

mgr = AWSAccountManager()

class PureHTTPSSpammer:
    def __init__(self, accounts, target, mode):
        self.accounts = accounts
        self.target = target
        self.mode = mode
        self.running = True
        self.total_sent = 0
        self.errors_count = 0

    async def _resolve_target(self, client, item):
        link = item.get("val")
        ltype = item.get("type", "invite")
        try:
            if ltype == "invite" and ("ig.me" in link or "instagram.com" in link):
                resp = await client.get(link, follow_redirects=True, timeout=10)
                final_url = str(resp.url)
                if "/direct/t/" in final_url:
                    parts = final_url.split("/direct/t/")
                    if len(parts) > 1:
                        tid = parts[1].strip("/").split("/")[0]
                        if tid.isdigit() or len(tid) > 5:
                            return tid
            elif ltype == "thread_id" or ltype == "thread_num":
                if link.isdigit() or len(link) > 3:
                    return link
            elif link.isdigit() or len(link) > 5:
                return link
        except:
            pass
        return None

    async def _worker(self, account_data):
        username = account_data['username']
        sessionid = account_data.get('sessionid')
        password = account_data.get('password')
        assigned_gcs = account_data.get('assigned_gcs', [])

        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "X-IG-App-ID": "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/direct/inbox/"
        }

        cookies = {"sessionid": sessionid} if sessionid else {}

        async with httpx.AsyncClient(headers=headers, cookies=cookies, http2=True) as client:
            try:
                if password and not sessionid:
                    # Basic login handling if password used
                    await client.post("https://www.instagram.com/accounts/login/ajax/", data={"username": username, "password": password}, timeout=15)
                
                await client.get("https://www.instagram.com/api/v1/direct_v2/inbox/?visual_message_return_type=read", timeout=15)
                if "csrftoken" in client.cookies:
                    client.headers["X-CSRFToken"] = client.cookies["csrftoken"]
            except:
                pass

            resolved_tids = []
            for gco in assigned_gcs:
                tid = await self._resolve_target(client, gco)
                if tid:
                    resolved_tids.append(tid)

            while self.running:
                if not resolved_tids:
                    await asyncio.sleep(10)
                    continue

                if self.mode == "single":
                    active_targets = [resolved_tids[0]]
                else:
                    active_targets = resolved_tids

                for tid in active_targets:
                    if not self.running: break

                    emojis = ["💙", "❤️", "💚", "💛", "💜", "🖤", "🤍", "🤎", "🧡", "💖"]
                    line = f"{self.target} 𝚃𝙼𝙺𝙲 {random.choice(emojis)}"
                    payload_text = "\n".join([line for _ in range(3)])

                    url = "https://www.instagram.com/api/v1/direct_v2/threads/broadcast/text/"
                    data = {
                        "action": "send_item",
                        "text": payload_text,
                        "device_id": f"android-{random.randint(1000000000000, 9999999999999)}",
                        "client_context": str(random.randint(100000000, 999999999)),
                        "thread_ids": f"[\"{tid}\"]"
                    }

                    try:
                        response = await client.post(url, data=data, timeout=10)
                        if response.status_code == 200:
                            self.total_sent += 1
                        else:
                            self.errors_count += 1
                    except:
                        self.errors_count += 1

                    await asyncio.sleep(random.uniform(config_mgr.config.get("delay_min", 2.0), config_mgr.config.get("delay_max", 4.5)))

    async def run(self):
        tasks = [asyncio.create_task(self._worker(acc)) for acc in self.accounts]
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass

def get_main_menu():
    current_mode = config_mgr.config.get("mode", "multiple").upper()
    keyboard = [
        [InlineKeyboardButton(f"⚙️ Mode: [{current_mode} GC]", callback_data="toggle_mode")],
        [InlineKeyboardButton("🚀 Start ANKIT GOD Attack", callback_data="atk_auto")],
        [InlineKeyboardButton("👤 Manage Accounts & GCs", callback_data="menu_accounts"),
         InlineKeyboardButton("🎯 Target Config", callback_data="menu_config")],
        [InlineKeyboardButton("📊 Diagnostics", callback_data="menu_status"),
         InlineKeyboardButton("🛑 Stop Attack", callback_data="menu_stop")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="menu_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_account_menu():
    keyboard = [
        [InlineKeyboardButton("➕ Add (Username & Password)", callback_data="acc_add_pwd"),
         InlineKeyboardButton("➕ Add (Session ID)", callback_data="acc_add_sid")],
        [InlineKeyboardButton("📋 List Accounts", callback_data="acc_list"),
         InlineKeyboardButton("🔗 Bind GC (Choose Type)", callback_data="acc_bind_gcs")],
        [InlineKeyboardButton("🗑️ Remove Account", callback_data="acc_remove_prompt")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_bind_type_menu(username):
    keyboard = [
        [InlineKeyboardButton("🔗 Simple Invite Link", callback_data=f"bind_invite_{username}")],
        [InlineKeyboardButton("🔢 Thread ID", callback_data=f"bind_tid_{username}")],
        [InlineKeyboardButton("📌 Thread Number", callback_data=f"bind_tnum_{username}")],
        [InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔥 **ANKIT GOD SCRIPT (ULTIMATE OPTIONS PANEL)** 🔥\n\nChoose an option below:"
    if update.message:
        await update.message.reply_text(text, reply_markup=get_main_menu(), parse_mode="Markdown")
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=get_main_menu(), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_spammer
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if data == "menu_home":
        user_states.pop(user_id, None)
        await context.bot.send_message(chat_id=chat_id, text="🔥 **Main Menu:**", reply_markup=get_main_menu(), parse_mode="Markdown")
    elif data == "toggle_mode":
        current = config_mgr.config.get("mode", "multiple")
        config_mgr.config["mode"] = "single" if current == "multiple" else "multiple"
        config_mgr.save()
        await context.bot.send_message(chat_id=chat_id, text=f"🔄 Mode switched to: **{config_mgr.config['mode'].upper()} GC**", reply_markup=get_main_menu(), parse_mode="Markdown")
    elif data == "menu_accounts":
        user_states.pop(user_id, None)
        await context.bot.send_message(chat_id=chat_id, text="👤 **Account Hub:**", reply_markup=get_account_menu(), parse_mode="Markdown")
    elif data == "acc_add_pwd":
        user_states[user_id] = "waiting_username_pwd"
        await context.bot.send_message(chat_id=chat_id, text="➕ **Instagram Username bhejein (Password login ke liye):**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]))
    elif data == "acc_add_sid":
        user_states[user_id] = "waiting_username_sid"
        await context.bot.send_message(chat_id=chat_id, text="➕ **Instagram Username bhejein (Session ID login ke liye):**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]))
    elif data == "acc_list":
        accounts = mgr.get_all()
        text = "📊 **Registered Accounts:**\n\n"
        for acc in accounts:
            l_type = "🔑 Pwd" if acc.get('password') else "🍪 SessionID"
            text += f"• `{acc['username']}` | {l_type} | GCs: {len(acc.get('assigned_gcs', []))}\n"
        if not accounts: text = "❌ Koi account added nahi hai!"
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=get_account_menu(), parse_mode="Markdown")
    elif data == "acc_bind_gcs":
        user_states[user_id] = "waiting_bind_username"
        await context.bot.send_message(chat_id=chat_id, text="🔗 **GC Bind karne ke liye Account ka Username bhejein:** (Bina @ ke)", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]))
    elif data.startswith("bind_invite_") or data.startswith("bind_tid_") or data.startswith("bind_tnum_"):
        parts = data.split("_")
        btype = parts[1] # invite, tid, tnum
        username = parts[2]
        user_states[user_id] = {"state": f"waiting_bind_val_{btype}", "username": username}
        type_names = {"invite": "Simple Invite Link", "tid": "Thread ID", "tnum": "Thread Number"}
        await context.bot.send_message(chat_id=chat_id, text=f"📥 Ab `{username}` ke liye **{type_names[btype]}** bhejhein:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]))
    elif data == "acc_remove_prompt":
        user_states[user_id] = "waiting_for_remove"
        await context.bot.send_message(chat_id=chat_id, text="🗑️ **Remove Account:**\n\nUsername bhejein:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]))
    elif data == "menu_config":
        current_target = config_mgr.config.get("target", "ANKIT")
        await context.bot.send_message(chat_id=chat_id, text=f"🎯 **Config Hub:**\nCurrent Target: `{current_target}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✏️ Change Target Name", callback_data="cfg_set_target")], [InlineKeyboardButton("🔙 Back", callback_data="menu_home")]]))
    elif data == "cfg_set_target":
        user_states[user_id] = "waiting_for_target"
        await context.bot.send_message(chat_id=chat_id, text="✏️ **Naya Target/Hater Name bhejein:**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_config")]]))
    elif data == "atk_auto":
        accounts = mgr.get_all()
        target = config_mgr.config.get("target", "ANKIT")
        mode = config_mgr.config.get("mode", "multiple")
        if not accounts:
            await context.bot.send_message(chat_id=chat_id, text="❌ Pehle accounts add karein!", reply_markup=get_main_menu())
            return
        await context.bot.send_message(chat_id=chat_id, text=f"🚀 **Attack Started!**\nTarget: `{target}` | Mode: `{mode.upper()} GC` | IDs: {len(accounts)}", reply_markup=get_main_menu(), parse_mode="Markdown")
        active_spammer = PureHTTPSSpammer(accounts, target, mode)
        asyncio.create_task(active_spammer.run())
    elif data == "menu_status":
        cpu, ram = psutil.cpu_percent(), psutil.virtual_memory().percent
        status_desc = f"🔥 **RUNNING**\n⚡ Sent: `{active_spammer.total_sent:,}`\n⚠️ Errors: `{active_spammer.errors_count}`" if (active_spammer and active_spammer.running) else "💤 **IDLE**"
        await context.bot.send_message(chat_id=chat_id, text=f"📊 **Diagnostics:**\n\n{status_desc}\n\nCPU: `{cpu}%` | RAM: `{ram}%`", reply_markup=get_main_menu(), parse_mode="Markdown")
    elif data == "menu_stop":
        if active_spammer:
            active_spammer.running = False
            active_spammer = None
            await context.bot.send_message(chat_id=chat_id, text="🛑 **Stopped safely!**", reply_markup=get_main_menu(), parse_mode="Markdown")
        else:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ Koi attack active nahi hai.", reply_markup=get_main_menu(), parse_mode="Markdown")

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    state = user_states.get(user_id)
    text = update.message.text.strip()

    if not state: return

    if state == "waiting_username_pwd":
        temp_account_data[user_id] = {"username": text, "login_method": "pwd"}
        user_states[user_id] = "waiting_password"
        await context.bot.send_message(chat_id=chat_id, text="🔑 Ab account ka **Password** bhejein:")
    elif state == "waiting_password":
        acc_info = temp_account_data.get(user_id, {})
        username = acc_info.get("username")
        mgr.add(username, password=text)
        user_states.pop(user_id, None)
        temp_account_data.pop(user_id, None)
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Account `{username}` Password login ke sath add ho gaya!", reply_markup=get_main_menu(), parse_mode="Markdown")
    elif state == "waiting_username_sid":
        temp_account_data[user_id] = {"username": text, "login_method": "sid"}
        user_states[user_id] = "waiting_sessionid"
        await context.bot.send_message(chat_id=chat_id, text="🍪 Ab account ki **Session ID cookie** bhejein:")
    elif state == "waiting_sessionid":
        acc_info = temp_account_data.get(user_id, {})
        username = acc_info.get("username")
        mgr.add(username, sessionid=text)
        user_states.pop(user_id, None)
        temp_account_data.pop(user_id, None)
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Account `{username}` Session ID ke sath add ho gaya!", reply_markup=get_main_menu(), parse_mode="Markdown")
    elif state == "waiting_bind_username":
        found = any(acc['username'] == text for acc in mgr.accounts)
        if found:
            user_states.pop(user_id, None)
            await context.bot.send_message(chat_id=chat_id, text=f"🎯 Account `{text}` ke liye link type select karein:", reply_markup=get_bind_type_menu(text))
        else:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Account `{username if 'username' in locals() else text}` nahi mila! Sahi username bhejein (bina @ ke).")
    elif isinstance(state, dict) and state.get("state", "").startswith("waiting_bind_val_"):
        btype = state["state"].split("_")[-1] # invite, tid, tnum
        username = state["username"]
        user_states.pop(user_id, None)
        
        for acc in mgr.accounts:
            if acc['username'] == username:
                acc['assigned_gcs'] = [{"val": text, "type": btype}]
        mgr._save()
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Success! `{username}` ke sath GC successfully bind ho gaya.", reply_markup=get_main_menu(), parse_mode="Markdown")
    elif state == "waiting_for_remove":
        mgr.remove(text)
        user_states.pop(user_id, None)
        await context.bot.send_message(chat_id=chat_id, text=f"🗑️ Account `{text}` hata diya gaya.", reply_markup=get_main_menu(), parse_mode="Markdown")
    elif state == "waiting_for_target":
        config_mgr.config["target"] = text
        config_mgr.save()
        user_states.pop(user_id, None)
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Target / Hater name updated: `{text}`", reply_markup=get_main_menu(), parse_mode="Markdown")

def main():
    TOKEN = "8684651458:AAFSGE0cgk_LZVj0SbNbIDPL62S3DWxumuY"
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    print("[ANKIT GOD SCRIPT] Ultimate Options Panel Running...")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
    
