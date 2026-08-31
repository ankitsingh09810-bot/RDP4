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
print("     🔥 ANKIT GOD SCRIPT (ULTIMATE ANTI-BAN EDITION) 🔥     ")
print("     Single/Multiple GC Routing & Zero-Ban Safety Engine    ")
print("=" * 60)

logging.basicConfig(format='%(asctime)s - [ANKIT_GOD] - %(levelname)s - %(message)s', level=logging.INFO)

ACCOUNTS_FILE  = Path.cwd() / "ankit_aws_accounts.json"
CONFIG_FILE    = Path.cwd() / "ankit_aws_config.json"

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
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

    def add(self, username, sessionid=None):
        for acc in self.accounts:
            if acc['username'] == username:
                if sessionid: acc['sessionid'] = sessionid
                self._save()
                return True

        self.accounts.append({
            'username': username, 
            'sessionid': sessionid,
            'assigned_gcs': []
        })
        self._save()
        print(f"[+] Account Added: @{username}")
        return True

    def remove(self, username):
        self.accounts = [a for a in self.accounts if a['username'] != username]
        self._save()
        print(f"[-] Account Removed: @{username}")

    def get_all(self):
        return self.accounts

mgr = AWSAccountManager()

class PureHTTPSSpammer:
    def __init__(self, accounts, target, mode):
        self.accounts = accounts
        self.target = target
        self.mode = mode # 'single' ya 'multiple'
        self.running = True
        self.total_sent = 0
        self.errors_count = 0

    async def _resolve_link(self, client, link):
        try:
            if "ig.me" in link or "instagram.com" in link:
                resp = await client.get(link, follow_redirects=True, timeout=10)
                final_url = str(resp.url)
                if "/direct/t/" in final_url:
                    parts = final_url.split("/direct/t/")
                    if len(parts) > 1:
                        tid = parts[1].strip("/").split("/")[0]
                        if tid.isdigit() or len(tid) > 5:
                            return tid
            elif link.isdigit() or len(link) > 5:
                return link
        except:
            pass
        return None

    async def _worker(self, account_data):
        username = account_data['username']
        sessionid = account_data.get('sessionid')
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
                await client.get("https://www.instagram.com/api/v1/direct_v2/inbox/?visual_message_return_type=read", timeout=15)
                if "csrftoken" in client.cookies:
                    client.headers["X-CSRFToken"] = client.cookies["csrftoken"]
            except:
                pass

            target_tids = []
            for gclink in assigned_gcs:
                tid = await self._resolve_link(client, gclink)
                if tid:
                    target_tids.append(tid)

            while self.running:
                if not target_tids:
                    await asyncio.sleep(10)
                    continue

                # Mode handling: Single GC vs Multiple GCs
                if self.mode == "single":
                    # Har account apne assigned list ka sirf pehla GC pick karega (Dedicated Single GC Spam)
                    active_targets = [target_tids[0]]
                else:
                    # Multiple mode me saare assigned GCs par rotate karega
                    active_targets = target_tids

                for tid in active_targets:
                    if not self.running: break

                    emojis = ["💙", "❤️", "💚", "💛", "💜", "🖤", "🤍", "🤎", "🧡", "💖"]
                    currentEmoji = random.choice(emojis)
                    line = f"{self.target} 𝚃𝙼𝙺𝙲 {currentEmoji}"
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
                            print(f"[SAFE SPAM] Sent #{self.total_sent} | @{username} -> GC: {tid}")
                        elif response.status_code == 401 or response.status_code =="checkpoint":
                            print(f"[SECURITY WARNING] Account @{username} session issue detected! Pause recommended.")
                            self.errors_count += 1
                            await asyncio.sleep(30)
                        else:
                            self.errors_count += 1
                    except Exception as ex:
                        self.errors_count += 1
                        print(f"[ERROR] @{username}: {ex}")

                    # Anti-Ban Safe Delays (Randomized to prevent spam filters)
                    d_min = config_mgr.config.get("delay_min", 2.0)
                    d_max = config_mgr.config.get("delay_max", 4.5)
                    await asyncio.sleep(random.uniform(d_min, d_max))

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
        [InlineKeyboardButton("➕ Add Account (SessionID)", callback_data="acc_add_sid")],
        [InlineKeyboardButton("📋 List Accounts", callback_data="acc_list"),
         InlineKeyboardButton("🔗 Bind GCs (Links/IDs)", callback_data="acc_bind_gcs")],
        [InlineKeyboardButton("🗑️ Remove Account", callback_data="acc_remove_prompt")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_config_menu():
    current_target = config_mgr.config.get("target", "ANKIT")
    d_min = config_mgr.config.get("delay_min", 2.0)
    d_max = config_mgr.config.get("delay_max", 4.5)
    keyboard = [
        [InlineKeyboardButton(f"✏️ Target Name: [{current_target}]", callback_data="cfg_set_target")],
        [InlineKeyboardButton(f"⏱️ Delay: [{d_min}s - {d_max}s (Anti-Ban)]", callback_data="cfg_set_delay")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔥 **ANKIT GOD SCRIPT (ANTI-BAN PANEL)** 🔥\n\nChoose your option safely:"
    if update.message:
        await update.message.reply_text(text, reply_markup=get_main_menu(), parse_mode="Markdown")
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=get_main_menu(), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_spammer
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "menu_home":
        user_states.pop(user_id, None)
        await query.edit_message_text("🔥 **Main Menu:**", reply_markup=get_main_menu(), parse_mode="Markdown")
    elif data == "toggle_mode":
        current = config_mgr.config.get("mode", "multiple")
        config_mgr.config["mode"] = "single" if current == "multiple" else "multiple"
        config_mgr.save()
        await query.edit_message_text(f"🔄 Mode switched to: **{config_mgr.config['mode'].upper()} GC**", reply_markup=get_main_menu(), parse_mode="Markdown")
    elif data == "menu_accounts":
        user_states.pop(user_id, None)
        await query.edit_message_text("👤 **Account Hub:**", reply_markup=get_account_menu(), parse_mode="Markdown")
    elif data == "acc_add_sid":
        user_states[user_id] = "waiting_for_username_sid"
        await query.edit_message_text("➕ **Add Account:**\n\nInstagram Username bhejein:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]), parse_mode="Markdown")
    elif data == "acc_list":
        accounts = mgr.get_all()
        text = "📊 **Account Status (Anti-Ban Safe):**\n\n"
        for acc in accounts:
            has_sid = "✅ Safe" if acc.get('sessionid') else "❌ Missing"
            text += f"• `@{acc['username']}` | Status: {has_sid} | GCs: {len(acc.get('assigned_gcs', []))}\n"
        if not accounts: text = "❌ Koi account added nahi hai!"
        await query.edit_message_text(text, reply_markup=get_account_menu(), parse_mode="Markdown")
    elif data == "acc_bind_gcs":
        user_states[user_id] = "waiting_bind_gcs"
        await query.edit_message_text("🔗 **Bind GCs / Links:**\n\nFormat:\n`username | link_or_thread1, link2`\n\n*(Single mode me pehla link use hoga, Multiple me saare)*", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]), parse_mode="Markdown")
    elif data == "acc_remove_prompt":
        user_states[user_id] = "waiting_for_remove"
        await query.edit_message_text("🗑️ **Remove Account:**\n\nUsername bhejein:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]), parse_mode="Markdown")
    elif data == "menu_config":
        await query.edit_message_text("🎯 **Config Hub:**", reply_markup=get_config_menu(), parse_mode="Markdown")
    elif data == "cfg_set_target":
        user_states[user_id] = "waiting_for_target"
        await query.edit_message_text("✏️ **Change Target:**\n\nNaya target name bhejein:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_config")]]), parse_mode="Markdown")
    elif data == "cfg_set_delay":
        user_states[user_id] = "waiting_for_delay"
        await query.edit_message_text("⏱️ **Set Anti-Ban Delay:**\n\nSeconds daalein (Jaise: `2.0` ya `3.5`):", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_config")]]), parse_mode="Markdown")
    elif data == "atk_auto":
        accounts = mgr.get_all()
        target = config_mgr.config.get("target", "ANKIT")
        mode = config_mgr.config.get("mode", "multiple")
        if not accounts:
            await query.edit_message_text("❌ Pehle accounts add karein!", reply_markup=get_main_menu())
            return
        await query.edit_message_text(f"🚀 **Attack Started!**\nTarget: `{target}` | Mode: `{mode.upper()} GC` | IDs: {len(accounts)}", reply_markup=get_main_menu(), parse_mode="Markdown")
        active_spammer = PureHTTPSSpammer(accounts, target, mode)
        asyncio.create_task(active_spammer.run())
    elif data == "menu_status":
        cpu, ram = psutil.cpu_percent(), psutil.virtual_memory().percent
        status_desc = f"🔥 **RUNNING**\n⚡ Sent: `{active_spammer.total_sent:,}`\n⚠️ Errors: `{active_spammer.errors_count}`" if (active_spammer and active_spammer.running) else "💤 **IDLE**"
        await query.edit_message_text(f"📊 **Diagnostics:**\n\n{status_desc}\n\nCPU: `{cpu}%` | RAM: `{ram}%` | Mode: `{config_mgr.config.get('mode').upper()}`", reply_markup=get_main_menu(), parse_mode="Markdown")
    elif data == "menu_stop":
        if active_spammer:
            active_spammer.running = False
            active_spammer = None
            await query.edit_message_text("🛑 **Stopped safely!**", reply_markup=get_main_menu(), parse_mode="Markdown")
        else:
            await query.edit_message_text("⚠️ Koi attack active nahi hai.", reply_markup=get_main_menu(), parse_mode="Markdown")

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_spammer
    user_id = update.message.from_user.id
    state = user_states.get(user_id)
    text = update.message.text.strip()

    if not state:
        return

    if state == "waiting_for_username_sid":
        temp_account_data[user_id] = {"username": text}
        user_states[user_id] = "waiting_for_sessionid"
        await update.message.reply_text("🍪 Ab Instagram ka **sessionid cookie** bhejein (ID safe rakhne ke liye session ID best hai):", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]))

    elif state == "waiting_for_sessionid":
        username = temp_account_data.get(user_id, {}).get("username")
        sessionid = text
        mgr.add(username, sessionid=sessionid)
        user_states.pop(user_id, None)
        temp_account_data.pop(user_id, None)
        await update.message.reply_text(f"✅ Account `@{username}` safely add ho gaya!", reply_markup=get_main_menu(), parse_mode="Markdown")

    elif state == "waiting_bind_gcs":
        user_states.pop(user_id, None)
        if "|" in text:
            acc_name, links_str = [x.strip() for x in text.split("|", 1)]
            links = [l.strip() for l in links_str.split(",") if l.strip()]
            found = False
            for acc in mgr.accounts:
                if acc['username'] == acc_name:
                    acc['assigned_gcs'] = links
                    found = True
            mgr._save()
            if found:
                await update.message.reply_text(f"✅ Account `@{acc_name}` ke sath GCs bind ho gaye!", reply_markup=get_main_menu(), parse_mode="Markdown")
            else:
                await update.message.reply_text(f"❌ Account `@{acc_name}` nahi mila!", reply_markup=get_main_menu(), parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Format galat hai! `username | link1,link2` use karein.", reply_markup=get_main_menu(), parse_mode="Markdown")

    elif state == "waiting_for_remove":
        mgr.remove(text)
        user_states.pop(user_id, None)
        await update.message.reply_text(f"🗑️ Account `@{text}` hata diya gaya.", reply_markup=get_main_menu(), parse_mode="Markdown")

    elif state == "waiting_for_target":
        config_mgr.config["target"] = text
        config_mgr.save()
        user_states.pop(user_id, None)
        await update.message.reply_text(f"✅ Target updated: `{text}`", reply_markup=get_main_menu(), parse_mode="Markdown")

    elif state == "waiting_for_delay":
        try:
            val = float(text)
            config_mgr.config["delay_min"] = val
            config_mgr.config["delay_max"] = val + 2.0
            config_mgr.save()
            user_states.pop(user_id, None)
            await update.message.reply_text(f"✅ Delay updated safely to range: `{val}s - {val+2.0}s`", reply_markup=get_config_menu(), parse_mode="Markdown")
        except:
            await update.message.reply_text("❌ Kripya valid number daalein (Jaise: `2.5`)")

def main():
    TOKEN = "8684651458:AAFSGE0cgk_LZVj0SbNbIDPL62S3DWxumuY"
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    print("[ANKIT GOD SCRIPT] Ultimate Panel Running Safely...")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
                    
