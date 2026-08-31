import asyncio
import gc
import json
import random
import logging
import psutil
from pathlib import Path
from playwright.async_api import async_playwright
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

print("=" * 60)
print("          🔥 ANKIT GOD SCRIPT (ULTIMATE EDITION) 🔥          ")
print("          Multi-Login & Advanced GC Routing Active            ")
print("=" * 60)

logging.basicConfig(format='%(asctime)s - [ANKIT_GOD] - %(levelname)s - %(message)s', level=logging.INFO)

PROFILES_DIR   = Path.cwd() / "ankit_aws_profiles"
ACCOUNTS_FILE  = Path.cwd() / "ankit_aws_accounts.json"
CONFIG_FILE    = Path.cwd() / "ankit_aws_config.json"
PRIMARY_SELECTOR = 'div[role="textbox"], [contenteditable="true"]'

AWS_ARGS = [
    "--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu",
    "--disable-extensions", "--disable-sync", "--mute-audio",
    "--disable-background-networking", "--disable-background-timer-throttling",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-blink-features=AutomationControlled",
    "--no-zygote",
    "--ignore-certificate-errors"
]

MOBILE_UAS = [
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
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
        return {"target": "ANKIT", "delay_min": 1.2, "delay_max": 2.8}

    def save(self):
        with open(CONFIG_FILE, 'w') as f: json.dump(self.config, f, indent=2)

config_mgr = BotConfigManager()

class AWSAccountManager:
    def __init__(self):
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        self.accounts = self._load()

    def _load(self):
        if ACCOUNTS_FILE.exists():
            try:
                with open(ACCOUNTS_FILE, 'r') as f: return json.load(f)
            except: return []
        return []

    def _save(self):
        with open(ACCOUNTS_FILE, 'w') as f: json.dump(self.accounts, f, indent=2)

    def add(self, username, password=None, sessionid=None, proxy=None):
        for acc in self.accounts:
            if acc['username'] == username:
                if password: acc['password'] = password
                if sessionid: acc['sessionid'] = sessionid
                if proxy: acc['proxy'] = proxy
                self._save()
                return True

        self.accounts.append({
            'username': username, 
            'password': password,
            'sessionid': sessionid,
            'profile_dir': str(PROFILES_DIR / f"acc_{username}"),
            'proxy': proxy,
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

class AWSAutoDiscoverySpammer:
    def __init__(self, accounts, target):
        self.accounts = accounts
        self.target = target
        self.running = True
        self.total_sent = 0
        self.errors_count = 0

    async def _worker(self, account_data):
        profile_dir = account_data['profile_dir']
        proxy_url = account_data.get('proxy')
        sessionid = account_data.get('sessionid')
        username = account_data['username']
        password = account_data.get('password')
        assigned_gcs = account_data.get('assigned_gcs', [])
        
        while self.running:
            async with async_playwright() as p:
                browser = None
                try:
                    proxy_config = {"server": proxy_url} if proxy_url else None
                    chosen_ua = random.choice(MOBILE_UAS)
                    
                    browser = await p.chromium.launch_persistent_context(
                        user_data_dir=profile_dir,
                        headless=True,
                        args=AWS_ARGS,
                        proxy=proxy_config,
                        user_agent=chosen_ua,
                        viewport={"width": 360, "height": 800},
                        is_mobile=True,
                        has_touch=True,
                        ignore_https_errors=True
                    )
                    
                    if sessionid:
                        await browser.add_cookies([{
                            "name": "sessionid",
                            "value": sessionid,
                            "domain": ".instagram.com",
                            "path": "/",
                            "httpOnly": True,
                            "secure": True
                        }])

                    await browser.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                        window.navigator.chrome = { runtime: {} };
                        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                    """)

                    page = await browser.new_page()
                    await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,mp4,webm,ogg,css,font,woff}", lambda route: route.abort())

                    # Auto login if password provided and session not active
                    if password and not sessionid:
                        try:
                            await page.goto("https://www.instagram.com/accounts/login/", timeout=30000)
                            await asyncio.sleep(3)
                            await page.fill('input[name="username"]', username)
                            await page.fill('input[name="password"]', password)
                            await page.click('button[type="submit"]')
                            await asyncio.sleep(5)
                        except:
                            pass

                    target_urls = assigned_gcs
                    if not target_urls:
                        try:
                            await page.goto("https://www.instagram.com/direct/inbox/", timeout=35000, wait_until='domcontentloaded')
                            await asyncio.sleep(4)
                            links = await page.evaluate("""
                                Array.from(document.querySelectorAll('a')).map(a => a.href).filter(h => h.includes('/direct/t/'))
                            """)
                            target_urls = list(set(links))[:20]
                        except:
                            target_urls = []

                    if not target_urls:
                        target_urls = ["https://www.instagram.com/direct/inbox/"]

                    pages = []
                    for url in target_urls:
                        if not self.running: break
                        p_tab = await browser.new_page()
                        await p_tab.route("**/*.{png,jpg,jpeg,gif,webp,svg,mp4,webm,ogg,css,font,woff}", lambda route: route.abort())
                        try:
                            # Support for Thread ID, Thread Number, or Direct Invite Link
                            if url.isdigit() or len(url) > 12 and "/" not in url:
                                target_link = f"https://www.instagram.com/direct/t/{url}/"
                            elif "instagram.com" in url or "ig.me" in url:
                                target_link = url.replace("http://", "https://")
                            else:
                                target_link = f"https://www.instagram.com/direct/t/{url}/"
                            
                            await p_tab.goto(target_link, timeout=30000, wait_until='domcontentloaded')
                            await p_tab.wait_for_selector(PRIMARY_SELECTOR, timeout=12000)
                            pages.append(p_tab)
                        except:
                            try: await p_tab.close()
                            except: pass

                    if not pages:
                        await asyncio.sleep(15)
                        continue

                    msg_counter = 0
                    while self.running:
                        for p_tab in pages:
                            if not self.running: break
                            
                            msg_counter += 1
                            if msg_counter >= 30:
                                msg_counter = 0
                                rest_time = random.uniform(15.0, 30.0)
                                await asyncio.sleep(rest_time)

                            emojis = ["💙", "❤️", "💚", "💛", "💜", "🖤", "🤍", "🤎", "🧡", "💖"]
                            currentEmoji = random.choice(emojis)
                            line = f"{self.target} 𝚃𝙼𝙺𝙲 {currentEmoji}"
                            payload = "\n".join([line for _ in range(4)])

                            try:
                                await p_tab.evaluate(f"""
                                    (data) => {{
                                        const el = document.querySelector('{PRIMARY_SELECTOR}');
                                        if (el) {{
                                            el.focus();
                                            document.execCommand('insertText', false, data);
                                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                        }}
                                    }}
                                """, payload)
                                
                                await asyncio.sleep(0.05)
                                await p_tab.keyboard.press("Enter")
                                self.total_sent += 1
                                print(f"[ANKIT GOD] Sent Message #{self.total_sent} via @{username}")
                            except Exception as ex:
                                self.errors_count += 1
                                print(f"[ANKIT GOD ERROR] Failed: {ex}")

                            d_min = config_mgr.config.get("delay_min", 1.2)
                            d_max = config_mgr.config.get("delay_max", 2.8)
                            await asyncio.sleep(random.uniform(d_min, d_max))
                        
                        gc.collect()

                except Exception as e:
                    self.errors_count += 1
                    print(f"[ANKIT GOD CRITICAL] Worker error: {e}")
                    await asyncio.sleep(20)
                finally:
                    if browser:
                        try: await browser.close()
                        except: pass

    async def run(self):
        tasks = [asyncio.create_task(self._worker(acc)) for acc in self.accounts]
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass

def get_main_menu():
    keyboard = [
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
        [InlineKeyboardButton("➕ Add Account (Password)", callback_data="acc_add_pwd"),
         InlineKeyboardButton("➕ Add Account (SessionID)", callback_data="acc_add_sid")],
        [InlineKeyboardButton("📋 List Accounts", callback_data="acc_list"),
         InlineKeyboardButton("🔗 Bind GCs", callback_data="acc_bind_gcs")],
        [InlineKeyboardButton("🗑️ Remove Account", callback_data="acc_remove_prompt")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_config_menu():
    current_target = config_mgr.config.get("target", "ANKIT")
    keyboard = [
        [InlineKeyboardButton(f"✏️ Target Name: [{current_target}]", callback_data="cfg_set_target")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_home")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔥 **ANKIT GOD SCRIPT CONTROL PANEL** 🔥\n\nChoose an option below:"
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
    elif data == "menu_accounts":
        user_states.pop(user_id, None)
        await query.edit_message_text("👤 **Account Hub:**", reply_markup=get_account_menu(), parse_mode="Markdown")
    elif data == "acc_add_pwd":
        user_states[user_id] = "waiting_for_username_pwd"
        await query.edit_message_text("➕ **Add Account via Password:**\n\nInstagram Username bhejein:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]), parse_mode="Markdown")
    elif data == "acc_add_sid":
        user_states[user_id] = "waiting_for_username_sid"
        await query.edit_message_text("➕ **Add Account via Session ID:**\n\nInstagram Username bhejein:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]), parse_mode="Markdown")
    elif data == "acc_list":
        accounts = mgr.get_all()
        text = "📊 **Account Status:**\n\n"
        for acc in accounts:
            login_type = "🔑 Pwd" if acc.get('password') else ("🍪 SessionID" if acc.get('sessionid') else "❌ None")
            text += f"• `@{acc['username']}` | Mode: {login_type} | GCs: {len(acc.get('assigned_gcs', []))}\n"
        if not accounts: text = "❌ Koi account added nahi hai!"
        await query.edit_message_text(text, reply_markup=get_account_menu(), parse_mode="Markdown")
    elif data == "acc_bind_gcs":
        user_states[user_id] = "waiting_bind_gcs"
        await query.edit_message_text("🔗 **Bind GCs:**\n\nFormat:\n`username | link_or_thread_id1, thread_id2`\n\n*(Support: Invite Link, Thread ID, ya Thread Number)*", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]), parse_mode="Markdown")
    elif data == "acc_remove_prompt":
        user_states[user_id] = "waiting_for_remove"
        await query.edit_message_text("🗑️ **Remove Account:**\n\nUsername bhejein:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]), parse_mode="Markdown")
    elif data == "menu_config":
        await query.edit_message_text("🎯 **Config Hub:**", reply_markup=get_config_menu(), parse_mode="Markdown")
    elif data == "cfg_set_target":
        user_states[user_id] = "waiting_for_target"
        await query.edit_message_text("✏️ **Change Target:**\n\nNaya target name bhejein:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_config")]]), parse_mode="Markdown")
    elif data == "atk_auto":
        accounts = mgr.get_all()
        target = config_mgr.config.get("target", "ANKIT")
        if not accounts:
            await query.edit_message_text("❌ Pehle accounts add karein!", reply_markup=get_main_menu())
            return
        await query.edit_message_text(f"🚀 **ANKIT GOD Attack Started!**\nTarget: `{target}` | Active IDs: {len(accounts)}", reply_markup=get_main_menu(), parse_mode="Markdown")
        active_spammer = AWSAutoDiscoverySpammer(accounts, target)
        asyncio.create_task(active_spammer.run())
    elif data == "menu_status":
        cpu, ram = psutil.cpu_percent(), psutil.virtual_memory().percent
        status_desc = f"🔥 **RUNNING**\n⚡ Sent: `{active_spammer.total_sent:,}`\n⚠️ Errors: `{active_spammer.errors_count}`" if (active_spammer and active_spammer.running) else "💤 **IDLE**"
        await query.edit_message_text(f"📊 **Diagnostics:**\n\n{status_desc}\n\nCPU: `{cpu}%` | RAM: `{ram}%` | Active IDs: `{len(mgr.get_all())}`", reply_markup=get_main_menu(), parse_mode="Markdown")
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

    if state == "waiting_for_username_pwd":
        temp_account_data[user_id] = {"username": text, "type": "pwd"}
        user_states[user_id] = "waiting_for_password"
        await update.message.reply_text("🔑 Ab Instagram ka **Password** bhejein:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]))

    elif state == "waiting_for_password":
        data_dict = temp_account_data.get(user_id, {})
        username = data_dict.get("username")
        password = text
        mgr.add(username, password=password)
        user_states.pop(user_id, None)
        temp_account_data.pop(user_id, None)
        await update.message.reply_text(f"✅ Account `@{username}` password ke sath add ho gaya!", reply_markup=get_main_menu(), parse_mode="Markdown")

    elif state == "waiting_for_username_sid":
        temp_account_data[user_id] = {"username": text, "type": "sid"}
        user_states[user_id] = "waiting_for_sessionid"
        await update.message.reply_text("🍪 Ab Instagram ka **sessionid cookie** bhejein:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="menu_accounts")]]))

    elif state == "waiting_for_sessionid":
        data_dict = temp_account_data.get(user_id, {})
        username = data_dict.get("username")
        sessionid = text
        mgr.add(username, sessionid=sessionid)
        user_states.pop(user_id, None)
        temp_account_data.pop(user_id, None)
        await update.message.reply_text(f"✅ Account `@{username}` session ID ke sath add ho gaya!", reply_markup=get_main_menu(), parse_mode="Markdown")

    elif state == "waiting_bind_gcs":
        user_states.pop(user_id, None)
        if "|" in text:
            acc_name, links_str = [x.strip() for x in text.split("|", 1)]
            links = [l.strip() 
