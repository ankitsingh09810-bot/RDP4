# -*- coding: utf-8 -*-
import os, time, re, threading, gc, sys, logging, random
from playwright.sync_api import sync_playwright
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import asyncio

# --- ⚙️ SUPREME AUTO-RECOVERY & ALERT SETTINGS ---
TOTAL_DURATION = 86400  
MAX_SESSION_LIFETIME = 20700  # ~5 hours 45 minutes (Auto-restart before GitHub 6-hr cutoff)

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

TELEGRAM_BOT_TOKEN = "8926218603:AAH9YcmIRJ6hwLuvGYC-a0bQoZIKw46aC94"

active_tasks_config = []

stats = {
    "sent_count": 0,
    "last_error": "None ✅"
}

user_states = {}  
is_running = False
active_threads = []
stop_event = threading.Event()
admin_chat_ids = set()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

def send_telegram_alert_sync(message):
    import urllib.request
    import urllib.parse
    stats["last_error"] = message
    print(f"🚨 [ALERT] {message}")
    if not admin_chat_ids:
        return
    for chat_id in admin_chat_ids:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = urllib.parse.urlencode({'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
            req = urllib.request.Request(url, data=data)
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            print(f"⚠️ Failed to send Telegram alert: {e}")

def run_stealth_playwright_agent(agent_id, session_cookie, target_name, target_ids, base_delay_sec):
    global is_running, stats
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION and not stop_event.is_set():
        cycle_start_time = time.time()
        with sync_playwright() as p:
            browser = None
            try:
                print(f"🛡️ [Stealth Agent {agent_id}] Initializing Auto-Recovery Browser Session...")
                chosen_ua = random.choice(USER_AGENTS)
                
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-infobars",
                        "--window-size=1280,800"
                    ]
                )
                
                context = browser.new_context(
                    user_agent=chosen_ua,
                    viewport={"width": 1280, "height": 800},
                    locale="en-US",
                    timezone_id="Asia/Kolkata"
                )
                
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                sid = re.search(r'sessionid=([^;]+)', session_cookie).group(1) if 'sessionid=' in session_cookie else session_cookie
                context.add_cookies([{
                    'name': 'sessionid',
                    'value': sid.strip(),
                    'domain': '.instagram.com',
                    'path': '/'
                }])

                page = context.new_page()
                page.goto("https://www.instagram.com/", timeout=45000)
                time.sleep(random.uniform(3.0, 5.0))

                if "accounts/login" in page.url or "challenge" in page.url:
                    send_telegram_alert_sync(
                        f"🚨 *INSTAGRAM ACCOUNT BAN / LOGOUT ALERT!*\n\n"
                        f"⚙️ *Task Controller:* `[T3{agent_id-1}69]`\n"
                        f"🎯 *Target Name:* `{target_name}`\n"
                        f"⚠️ *Reason:* Session Cookie Expired, Logged Out or Account Flagged/Banned!"
                    )
                    browser.close()
                    break

                pages = [page]
                for idx, tid in enumerate(target_ids):
                    if stop_event.is_set(): break
                    tid_clean = tid.strip()
                    if not tid_clean: continue
                    
                    if idx == 0:
                        page.goto(f"https://www.instagram.com/direct/t/{tid_clean}/", timeout=45000)
                    else:
                        new_page = context.new_page()
                        new_page.goto(f"https://www.instagram.com/direct/t/{tid_clean}/", timeout=45000)
                        pages.append(new_page)
                    time.sleep(random.uniform(1.8, 3.2))

                print(f"🔥 [Stealth Agent {agent_id}] Live & Spaming across {len(pages)} GCs...")

                while not stop_event.is_set():
                    if (time.time() - cycle_start_time) > MAX_SESSION_LIFETIME:
                        print(f"🔄 [Auto-Recovery] Agent #{agent_id} refreshing session proactively...")
                        break

                    try:
                        current_url = pages[0].url
                        if "accounts/login" in current_url or "challenge" in current_url:
                            send_telegram_alert_sync(
                                f"🚨 *INSTAGRAM BAN / LOGOUT DETECTED MID-RUN!*\n\n"
                                f"⚙️ *Task Controller:* `[T3{agent_id-1}69]`\n"
                                f"🎯 *Target Name:* `{target_name}`\n"
                                f"⚠️ *Status:* Account was logged out, restricted, or faced a checkpoint!"
                            )
                            break
                    except:
                        pass

                    for pg in pages:
                        if stop_event.is_set(): break
                        try:
                            pg.evaluate(f"""() => {{
                                const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                                if (box) {{
                                    box.focus();
                                    box.click();
                                    
                                    const emojis = [
                                        "😀","😃","😄","😁","😆","😅","🤣","😂","🙂","🙃","😉","😊","😇","🥰","😍","🤩","😘","😗","😚","😙",
                                        "😋","😛","😜","🤪","😝","🤑","🤗","🤭","🤫","🤔","🤐","🤨","😐","😑","😶","😏","😒","🙄","😬","🤥",
                                        "😌","😔","😪","🤤","😴","😷","🤒","🤕","🤢","🤮","🤧","🥵","🥶","🥴","😵","🤯","🤠","🥳","😎","🤓",
                                        "🧐","😕","😟","🙁","☹","😮","😯","😲","😳","🥺","😦","😧","😨","😰","😥","😢","😭","😱","😖","😣",
                                        "😞","😓","😩","😫","🥱","😤","😡","😠","🤬","😈","👿","💀","☠","💩","🤡","👹","👺","👻","👽","👾",
                                        "🤖","😺","😸","😹","😻","😼","😽","🙀","😿","😾","💋","👋","🤚","🖐","✋","🖖","👌","🤌","🤏","✌️",
                                        "🤞","🫰","🤟","🤘","🤙","👈","👉","👆","🖕","👇","☝️","👍","👎","✊","👊","🤛","🤜","👏","🙌","👐",
                                        "🤲","🤝","🙏","✍️","💅","🤳","💪","🦾","🦿","🦵","🦶","👂","🦻","👃","🧠","🫀","🫁","🦷","🦴","👀",
                                        "👁","👅","👄","👶","👧","🧒","👦","👩","🧑","👨","👱‍♀️","👱","👱‍♂️","🧔‍♀️","🧔","🧔‍♂️","👵","🧓","👴","👲",
                                        "🧕","👮‍♀️","👮","👮‍♂️","👷‍♀️","👷","👷‍♂️","💂‍♀️","💂","💂‍♂️","🕵️‍♀️","🕵️","🕵️‍♂️","👩‍⚕️","👨‍⚕️","👩‍🌾","👨‍🌾","👩‍🍳","👨‍🍳","👩‍🎓",
                                        "👨‍🎓","👩‍🎤","👨‍🎤","👩‍🏫","👨‍🏫","👩‍🏭","👨‍🏭","👩‍💻","👨‍💻","👩‍💼","👨‍💼","👩‍🔧","👨‍🔧","👩‍🔬","👨‍🔬","👩‍🎨","👨‍🎨","👩‍✈️","👨‍✈️","👩‍🚀",
                                        "👨‍🚀","👩‍🚒","👨‍🚒","👮","🚀","🛸","🛰","⚡","🔥","💥","✨","🌟","⭐","🌙","☀️","🌈","🌪️","🌀","🌊","💎","👑"
                                    ];
                                    
                                    let text = "";
                                    for(let i = 1; i <= 10; i++) {{
                                        const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
                                        text += "{target_name}" + " 𝐂ʜᴜᴘ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ -(" + randomEmoji + ")-\\n\\n";
                                    }}
                                    
                                    const now = new Date();
                                    const timeStr = "[" + String(now.getHours()).padStart(2, '0') + ":" + String(now.getMinutes()).padStart(2, '0') + ":" + String(now.getSeconds()).padStart(2, '0') + "]";
                                    text += timeStr;
                                    
                                    const dataTransfer = new DataTransfer();
                                    dataTransfer.setData('text/plain', text);
                                    const event = new ClipboardEvent('paste', {{
                                        clipboardData: dataTransfer,
                                        bubbles: true
                                    }});
                                    box.dispatchEvent(event);
                                    
                                    setTimeout(() => {{
                                        const enter = new KeyboardEvent('keydown', {{
                                            bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                                        }});
                                        box.dispatchEvent(enter);
                                    }}, {random.randint(700, 1500)});
                                }}
                            }}""")
                        except Exception as e:
                            pass

                    stats["sent_count"] += len(pages)
                    print(f"📤 [Stats] Agent #{agent_id} batch delivered! Total: {stats['sent_count']}")

                    dynamic_jitter = base_delay_sec + random.uniform(3.0, 9.5)
                    time.sleep(dynamic_jitter)

            except Exception as e:
                err_str = str(e)
                print(f"⚠️ [Stealth Agent {agent_id}] Exception: {err_str}")
            finally:
                if browser:
                    try:
                        browser.close()
                    except:
                        pass
                gc.collect()
                time.sleep(1.0)

# --- UI KEYBOARDS & HANDLERS ---
def get_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🚀 Start Auto-Recovery Session", callback_data="start_spam"),
            InlineKeyboardButton("📊 Status", callback_data="status_check")
        ],
        [
            InlineKeyboardButton("⚙️ Admin Info", callback_data="admin_info"),
            InlineKeyboardButton("➕ Add Task", callback_data="menu_add_task")
        ],
        [
            InlineKeyboardButton("📋 View Tasks", callback_data="menu_view_tasks"),
            InlineKeyboardButton("🗑️ Clear Tasks", callback_data="menu_clear_tasks")
        ],
        [
            InlineKeyboardButton("🛑 Stop Task / Terminate All", callback_data="stop_spam")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [[InlineKeyboardButton("⚡ Back to Main Menu", callback_data="refresh_panel")]]
    return InlineKeyboardMarkup(keyboard)

def get_delay_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("⚡ 8s", callback_data="delay_8"),
            InlineKeyboardButton("🔥 12s (Safe Jitter)", callback_data="delay_12"),
            InlineKeyboardButton("⏱️ 15s (Ultra AI-Safe)", callback_data="delay_15")
        ],
        [InlineKeyboardButton("⚡ Back to Main Menu", callback_data="refresh_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    admin_chat_ids.add(chat_id)
    
    banner = "🤖 **SINGLE TIMER BOT ONLINE**\nSelect an option:"
    if update.message:
        await update.message.reply_text(banner, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_text(banner, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        except:
            await update.callback_query.message.reply_text(banner, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def start_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, active_threads, stop_event, stats, active_tasks_config
    query = update.callback_query
    chat = query.message if query else update.message
    chat_id = update.effective_chat.id
    admin_chat_ids.add(chat_id)
    
    if is_running:
        msg = "⚠️ Warning: Session is already running!"
        if query: await query.answer(msg, show_alert=True)
        else: await chat.reply_text(msg)
        return

    if not active_tasks_config:
        msg = "❌ Error: No tasks added yet! Click 'Add Task'."
        if query: await query.answer(msg, show_alert=True)
        else: await chat.reply_text(msg)
        return

    stop_event.clear()
    is_running = True
    active_threads.clear()

    for idx, task in enumerate(active_tasks_config):
        t = threading.Thread(
            target=run_stealth_playwright_agent, 
            args=(idx + 1, task["cookie"], task["target_name"], task["targets"], task["delay"])
        )
        t.start()
        active_threads.append(t)

    controller_cards = ""
    for idx, task in enumerate(active_tasks_config):
        threads_str = ", ".join(task["targets"][:5])
        controller_cards += (
            f"⚙️ **ALERT CONTROLLER [T3{idx}69]**\n"
            f"────────────────────────\n"
            f"📊 **Status:** 🟢 RUNNING (Single Timer at End)\n"
            f"🎯 **Target:** `{task['target_name']}`\n"
            f"📋 **GCs:** `{threads_str}`...\n"
            f"✉️ **Total Sent:** `{stats['sent_count']}`\n\n"
        )

    success_msg = f"🚀 **SESSION STARTED!**\n\n{controller_cards}"
    keyboard = [
        [InlineKeyboardButton("🛑 Stop Task", callback_data="stop_spam")],
        [InlineKeyboardButton("⚡ Main Menu", callback_data="refresh_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.answer("Started Successfully! 🚀")
        try: await query.message.edit_text(success_msg, parse_mode="Markdown", reply_markup=reply_markup)
        except: await query.message.reply_text(success_msg, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await chat.reply_text(success_msg, parse_mode="Markdown", reply_markup=reply_markup)

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, stop_event
    query = update.callback_query
    chat = query.message if query else update.message
    
    if not is_running:
        msg = "⚠️ Tasks are offline."
        if query: await query.answer(msg, show_alert=True)
        else: await chat.reply_text(msg)
        return

    stop_event.set()
    stop_msg = f"🛑 **Task Terminated!**\n📊 **Total Delivered:** `{stats['sent_count']}`"
    if query:
        await query.answer("Stopped! 🛑")
        try: await query.message.edit_text(stop_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        except: await query.message.reply_text(stop_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    else:
        await chat.reply_text(stop_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, stats, active_tasks_config
    query = update.callback_query
    chat = query.message if query else update.message
    
    controller_cards = ""
    if not active_tasks_config:
        controller_cards = "_No active task controllers found._\n"
    for idx, task in enumerate(active_tasks_config):
        controller_cards += (
            f"⚙️ **CONTROLLER [T3{idx}69]**\n"
            f"────────────────────────\n"
            f"📊 **Status:** `{'🟢 RUNNING' if is_running else '💤 IDLE'}`\n"
            f"🎯 **Target:** `{task['target_name']}`\n"
            f"✉️ **Total Sent:** `{stats['sent_count']}`\n\n"
        )

    status_msg = f"📊 **SYSTEM STATUS**\n\n{controller_cards}"
    if query:
        await query.answer("Refreshed 🔄")
        try: await query.message.edit_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        except: await query.message.reply_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    else:
        await chat.reply_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def admin_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    info_text = "⚙️ **ADMIN INFO**\n\n👑 **Owner:** Ankit\n⚡ **Engine:** Playwright + Single End Timer"
    if query:
        await query.answer()
        await query.message.edit_text(info_text, parse_mode="Markdown", reply_markup=get_back_keyboard())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if data == "start_spam":
        await start_spam(update, context)
    elif data == "stop_spam":
        await stop_spam(update, context)
    elif data == "status_check":
        await status_check(update, context)
    elif data == "admin_info":
        await admin_info(update, context)
    elif data == "refresh_panel":
        if user_id in user_states: del user_states[user_id]
        await cmd_start(update, context)
    elif data == "menu_clear_tasks":
        active_tasks_config.clear()
        await query.answer("Cleared!", show_alert=True)
        await cmd_start(update, context)
    elif data == "menu_view_tasks":
        if not active_tasks_config:
            txt = "📋 **No tasks configured.**"
        else:
            txt = f"📋 **Active Tasks ({len(active_tasks_config)}):**\n\n"
            for i, t in enumerate(active_tasks_config):
                txt += f"⚙️ **[T3{i}69] Target:** `{t['target_name']}` | GCs: `{len(t['targets'])}` | Delay: `{t['delay']}s`\n"
        await query.message.edit_text(txt, parse_mode="Markdown", reply_markup=get_back_keyboard())
    elif data == "menu_add_task":
        user_states[user_id] = {"step": "cookie", "cookie": "", "target_name": "", "targets": [], "delay": 12.0}
        await query.message.edit_text("➕ **ADD TASK (Step 1/4)**\n\n_Send Instagram session ID cookie:_", parse_mode="Markdown", reply_markup=get_back_keyboard())
    elif data.startswith("delay_"):
        if user_id in user_states and user_states[user_id].get("step") == "delay":
            delay_val = float(data.split("_")[1])
            user_states[user_id]["delay"] = delay_val
            active_tasks_config.append(user_states[user_id].copy())
            del user_states[user_id]
            success_txt = "✅ **Task Created Successfu
