# -*- coding: utf-8 -*-
import os, time, re, threading, gc, sys, logging, random
from playwright.sync_api import sync_playwright
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import asyncio

# --- ⚙️ SUPREME AUTO-RECOVERY & ALERT SETTINGS ---
TOTAL_DURATION = 86400  
MAX_SESSION_LIFETIME = 20700  

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

TELEGRAM_BOT_TOKEN = "8926218603:AAH9YcmIRJ6hwLuvGYC-a0bQoZIKw46aC94"

active_tasks_config = []
stats = {"sent_count": 0, "last_error": "None ✅"}
user_states = {}  
is_running = False
active_threads = []
stop_event = threading.Event()
admin_chat_ids = set()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
]

def send_telegram_alert_sync(message):
    import urllib.request
    import urllib.parse
    stats["last_error"] = message
    print(f"🚨 [ALERT] {message}")
    if not admin_chat_ids: return
    for chat_id in admin_chat_ids:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = urllib.parse.urlencode({'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
            urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=5)
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
                print(f"🛡️ [Stealth Agent {agent_id}] Initializing Browser Session...")
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--disable-blink-features=AutomationControlled"]
                )
                context = browser.new_context(user_agent=random.choice(USER_AGENTS), viewport={"width": 1280, "height": 800})
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

                sid = re.search(r'sessionid=([^;]+)', session_cookie).group(1) if 'sessionid=' in session_cookie else session_cookie
                context.add_cookies([{'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com', 'path': '/'}])

                page = context.new_page()
                page.goto("https://www.instagram.com/", timeout=45000)
                time.sleep(3.0)

                if "accounts/login" in page.url or "challenge" in page.url:
                    send_telegram_alert_sync(f"🚨 *INSTAGRAM LOGOUT ALERT* for target `{target_name}`!")
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
                    time.sleep(2.0)

                while not stop_event.is_set():
                    if (time.time() - cycle_start_time) > MAX_SESSION_LIFETIME: break

                    for pg in pages:
                        if stop_event.is_set(): break
                        try:
                            pg.evaluate(f"""() => {{
                                const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                                if (box) {{
                                    box.focus();
                                    box.click();
                                    let text = "{target_name} 𝐂ʜᴜᴘ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ -\\n\\n";
                                    const dataTransfer = new DataTransfer();
                                    dataTransfer.setData('text/plain', text);
                                    box.dispatchEvent(new ClipboardEvent('paste', {{ clipboardData: dataTransfer, bubbles: true }}));
                                    setTimeout(() => {{
                                        box.dispatchEvent(new KeyboardEvent('keydown', {{ bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13 }}));
                                    }}, 1000);
                                }}
                            }}""")
                        except: pass

                    stats["sent_count"] += len(pages)
                    print(f"📤 [Stats] Batch delivered! Total: {stats['sent_count']}")
                    time.sleep(base_delay_sec + random.uniform(3.0, 6.0))
            except Exception as e:
                print(f"⚠️ Exception: {e}")
            finally:
                if browser:
                    try: browser.close()
                    except: pass
                gc.collect()

def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Start Session", callback_data="start_spam"), InlineKeyboardButton("📊 Status", callback_data="status_check")],
        [InlineKeyboardButton("➕ Add Task", callback_data="menu_add_task"), InlineKeyboardButton("📋 View Tasks", callback_data="menu_view_tasks")],
        [InlineKeyboardButton("🗑️ Clear Tasks", callback_data="menu_clear_tasks"), InlineKeyboardButton("🛑 Stop", callback_data="stop_spam")]
    ])

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    admin_chat_ids.add(chat_id)
    msg = "🤖 **BOT ONLINE**\nSelect an option:"
    if update.message: await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    elif update.callback_query: await update.callback_query.message.edit_text(msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def start_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, active_threads, stop_event, active_tasks_config
    query = update.callback_query
    if is_running:
        if query: await query.answer("Already running!", show_alert=True)
        return
    if not active_tasks_config:
        if query: await query.answer("No tasks added yet!", show_alert=True)
        return

    stop_event.clear()
    is_running = True
    active_threads.clear()

    for idx, task in enumerate(active_tasks_config):
        t = threading.Thread(target=run_stealth_playwright_agent, args=(idx + 1, task["cookie"], task["target_name"], task["targets"], task["delay"]))
        t.start()
        active_threads.append(t)

    if query:
        await query.answer("Started! 🚀")
        await query.message.edit_text("🚀 **SESSION STARTED SUCCESSFULLY!**", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, stop_event
    is_running = False
    stop_event.set()
    query = update.callback_query
    if query:
        await query.answer("Stopped!")
        await query.message.edit_text("🛑 **Tasks Stopped.**", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

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
        await query.message.edit_text(f"📊 Active Tasks: {len(active_tasks_config)} | Sent: {stats['sent_count']}", reply_markup=get_main_menu_keyboard())
    elif data == "menu_clear_tasks":
        active_tasks_config.clear()
        await query.message.edit_text("🗑️ Cleared all tasks.", reply_markup=get_main_menu_keyboard())
    elif data == "menu_view_tasks":
        if not active_tasks_config:
            await query.message.edit_text("📋 No tasks configured.", reply_markup=get_main_menu_keyboard())
        else:
            txt = f"📋 Active Tasks: {len(active_tasks_config)}"
            await query.message.edit_text(txt, reply_markup=get_main_menu_keyboard())
    elif data == "menu_add_task":
        user_states[user_id] = {"step": "cookie", "cookie": "", "target_name": "", "targets": [], "delay": 12.0}
        await query.message.edit_text("➕ **Step 1:** Send Instagram Session Cookie:", parse_mode="Markdown")
    elif data.startswith("delay_"):
        if user_id in user_states and user_states[user_id].get("step") == "delay":
            delay_val = float(data.split("_")[1])
            user_states[user_id]["delay"] = delay_val
            active_tasks_config.append(user_states[user_id].copy())
            del user_states[user_id]
            await query.message.edit_text("✅ Task Added!", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    if user_id in user_states:
        state = user_states[user_id]
        if state["step"] == "cookie":
            state["cookie"] = text
            state["step"] = "target_name"
            await update.message.reply_text("🎯 **Step 2:** Enter Target Name:")
        elif state["step"] == "target_name":
            state["target_name"] = text
            state["step"] = "targets"
            await update.message.reply_text("📋 **Step 3:** Send GC ID(s):")
        elif state["step"] == "targets":
            state["targets"] = [i.strip() for i in re.split(r'[,\n]+', text) if i.strip()]
            state["step"] = "delay"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("8s", callback_data="delay_8"), InlineKeyboardButton("12s", callback_data="delay_12"), InlineKeyboardButton("15s", callback_data="delay_15")]
            ])
            await update.message.reply_text("⏱️ **Step 4:** Select Delay:", reply_markup=keyboard)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    print("Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
                
