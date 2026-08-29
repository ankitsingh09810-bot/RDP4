# -*- coding: utf-8 -*-
import os, time, re, threading, gc, sys, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ SUPREME TUNED SETTINGS ---
THREADS = 1           
TABS_PER_THREAD = 1   
PULSE_DELAY = 8000    # 8 seconds interval
TOTAL_DURATION = 86400  

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Hardcoded Telegram Token
TELEGRAM_BOT_TOKEN = "8926218603:AAH9YcmIRJ6hwLuvGYC-a0bQoZIKw46aC94"

# Runtime Dynamic Storage & State Management for Interactive UI
config = {
    "cookie": "",
    "target_id": "",
    "target_name": "Target"
}

user_states = {}  # Tracks what input the user is currently typing (cookie, target_id, target_name)
is_running = False
active_threads = []
stop_event = threading.Event()

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.page_load_strategy = 'eager'
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPad Pro"})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stealth(driver, languages=["en-US"], vendor="Google Inc.", platform="Linux armv8l", fix_hairline=True)
    return driver

def run_agent(agent_id, cookie, target_id, target_name):
    global is_running
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION and not stop_event.is_set():
        driver = None
        try:
            print(f"🚀 [Agent {agent_id}] Initializing Browser & Bypass Matrix...")
            driver = get_driver()
            driver.set_page_load_timeout(30)
            
            try:
                driver.get("https://www.instagram.com/")
            except Exception as load_err:
                print(f"⚠️ Page load timeout/error caught: {load_err}, forcing continuation...")

            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            for _ in range(TABS_PER_THREAD):
                if stop_event.is_set(): break
                driver.execute_script("window.open('https://www.instagram.com/direct/t/{}/', '_blank');".format(target_id))
                time.sleep(2)

            for handle in driver.window_handles[1:]:
                if stop_event.is_set(): break
                driver.switch_to.window(handle)
                
                # JS CODE FOR LONG SPAM + 𝐂ʜᴜᴘ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ + EMOJI DESIGN + SPACING + TIMER AT END
                js_code = """
                const delay = arguments[0];
                const targetName = arguments[1];
                
                const styleEmojis = ["💬", "💿", "🌀", "☢️", "🌊", "🧜‍♂️", "🎃", "🌙", "🐶", "🔥", "⚡", "💎"];
                
                window.__spamInterval = setInterval(() => {
                    try {
                        const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                        if (box) {
                            const now = new Date();
                            const timeStr = "[" + String(now.getHours()).padStart(2, '0') + ":" + String(now.getMinutes()).padStart(2, '0') + ":" + String(now.getSeconds()).padStart(2, '0') + "]";
                            
                            const randomEmoji = styleEmojis[Math.floor(Math.random() * styleEmojis.length)];
                            const line = targetName + " 𝐂ʜᴜᴘ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ -(" + randomEmoji + ")-";
                            
                            let text = "";
                            for(let i = 0; i < 25; i++) { 
                                text += line + "\\n\\n\\n"; 
                            }
                            text += line + " " + timeStr;
                            
                            const dataTransfer = new DataTransfer();
                            dataTransfer.setData('text/plain', text);
                            const event = new ClipboardEvent('paste', {
                                clipboardData: dataTransfer,
                                bubbles: true
                            });
                            box.dispatchEvent(event);
                            
                            setTimeout(() => {
                                const enter = new KeyboardEvent('keydown', {
                                    bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                                });
                                box.dispatchEvent(enter);
                            }, 400);
                        }
                    } catch(err) {}
                }, delay);
                """
                driver.execute_script(js_code, PULSE_DELAY, target_name)

            print(f"🔥 [Agent {agent_id}] Supreme 8-Sec Pulse Active & Stable...")
            
            while not stop_event.is_set():
                time.sleep(1)

        except Exception as e:
            print(f"⚠️ [Agent {agent_id}] Minor Exception Handled: {e}. Auto-recovering...")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            gc.collect()
            time.sleep(3)

    is_running = False

# --- INTERACTIVE TELEGRAM INLINE KEYBOARDS ---
def get_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🍪 Set Cookie", callback_data="menu_set_cookie"),
            InlineKeyboardButton("🎯 Set Target ID", callback_data="menu_set_target")
        ],
        [
            InlineKeyboardButton("👤 Set Target Name", callback_data="menu_set_name"),
            InlineKeyboardButton("📊 Status & Info", callback_data="status_check")
        ],
        [
            InlineKeyboardButton("🚀 Start Engine", callback_data="start_spam"),
            InlineKeyboardButton("🛑 Stop Engine", callback_data="stop_spam")
        ],
        [
            InlineKeyboardButton("🔄 Refresh Panel", callback_data="refresh_panel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="refresh_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- TELEGRAM BOT HANDLERS ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    banner = (
        "╭─────────────────────────╮\n"
        "🌙 ＡＣＥ ✖ 𝙼𝙾𝙾𝙽 𝚥²¹ 🌙\n"
        "👁️ ᴀᴄᴇ ᴇᴄᴏꜱʏꜱᴛᴇᴍ 👁️\n"
        "╰─────────────────────────╯\n"
        "⚡ **Supreme Insta Controller Dashboard**\n\n"
        "Neeche diye gaye buttons ka use karke configuration set karein aur engine control karein:"
    )
    
    if update.message:
        await update.message.reply_text(banner, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_text(banner, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        except Exception:
            await update.callback_query.message.reply_text(banner, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

# --- COMMAND HANDLERS (Fallback via text) ---
async def set_cookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **Usage:** `/setcookie <your_session_id>`")
        return
    config["cookie"] = " ".join(context.args)
    await update.message.reply_text("✅ **Instagram Cookie successfully locked in!** 🍪", reply_markup=get_main_menu_keyboard())

async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **Usage:** `/settarget <thread_id>`")
        return
    config["target_id"] = context.args[0]
    await update.message.reply_text(f"✅ **Target Thread ID locked:** `{config['target_id']}` 🎯", reply_markup=get_main_menu_keyboard())

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **Usage:** `/setname <target_name>`")
        return
    config["target_name"] = " ".join(context.args)
    await update.message.reply_text(f"✅ **Target Name updated:** `{config['target_name']}` 👤", reply_markup=get_main_menu_keyboard())

async def start_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, active_threads, stop_event
    
    query = update.callback_query
    chat = query.message if query else update.message
    
    if is_running:
        msg = "⚠️ Engine is already blazing live!"
        if query:
            await query.answer(msg, show_alert=True)
        else:
            await chat.reply_text(msg)
        return

    if not config["cookie"] or not config["target_id"]:
        msg = "❌ Setup incomplete! Pehle Cookie aur Target ID set karein."
        if query:
            await query.answer(msg, show_alert=True)
        else:
            await chat.reply_text(msg)
        return

    stop_event.clear()
    is_running = True
    active_threads.clear()

    t = threading.Thread(target=run_agent, args=(1, config["cookie"], config["target_id"], config["target_name"]))
    t.start()
    active_threads.append(t)

    success_msg = f"🚀 **Phoenix Engine Blazing!**\n🎯 Target: `{config['target_name']}`\n⏱️ Mode: Long Spamed Block + End Timer 🔥"
    if query:
        await query.answer("Engine Started Successfully! 🔥")
        try:
            await query.message.edit_text(success_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        except Exception:
            await query.message.reply_text(success_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    else:
        await chat.reply_text(success_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, stop_event
    query = update.callback_query
    chat = query.message if query else update.message
    
    if not is_running:
        msg = "⚠️ No active engine running right now."
        if query:
            await query.answer(msg, show_alert=True)
        else:
            await chat.reply_text(msg)
        return

    stop_event.set()
    stop_msg = "🛑 **Terminating Engine & Cleaning Browsers...**"
    if query:
        await query.answer("Engine Stopped! 🛑")
        try:
            await query.message.edit_text(stop_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        except Exception:
            await query.message.reply_text(stop_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    else:
        await chat.reply_text(stop_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running
    query = update.callback_query
    chat = query.message if query else update.message
    
    cookie_display = "Loaded ✅" if config['cookie'] else "Not Set ❌"
    target_display = config['target_id'] if config['target_id'] else "Not Set ❌"
    
    status_msg = (
        f"📊 **Supreme Bot Status Hub**\n\n"
        f"🟢 **Engine State:** {'🔥 Blazing Active (8s)' if is_running else '💤 Idle / Stopped'}\n"
        f"🍪 **Cookie:** `{cookie_display}`\n"
        f"🎯 **Target ID:** `{target_display}`\n"
        f"👤 **Target Name:** `{config['target_name']}`\n"
        f"💬 **Matrix:** `Long Spamed + 𝐂ʜᴜᴘ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ + Timer ⚡`"
    )
    if query:
        await query.answer("Status Refreshed 🔄")
        try:
            await query.message.edit_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        except Exception:
            await query.message.reply_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    else:
        await chat.reply_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

# --- INTERACTIVE BUTTON & INPUT HANDLER ---
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
    elif data == "refresh_panel":
        if user_id in user_states:
            del user_states[user_id]
        await cmd_start(update, context)
    elif data == "menu_set_cookie":
        user_states[user_id] = "waiting_cookie"
        await query.message.edit_text(
            "🍪 **Enter Instagram Session Cookie:**\n\nKripya apna `sessionid` yahan direct message mein bhejo:",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )
    elif data == "menu_set_target":
        user_states[user_id] = "waiting_target"
        await query.message.edit_text(
            "🎯 **Enter Target Thread ID:**\n\nKripya target ka Instagram Direct Thread ID yahan text mein bhejo:",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )
    elif data == "menu_set_name":
        user_states[user_id] = "waiting_name"
        await query.message.edit_text(
            "👤 **Enter Target Name:**\n\nKripya target ka naam yahan type karke bhejo:",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

# Handle text inputs dynamically based on button prompts
async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    if user_id in user_states:
        state = user_states[user_id]
        
        if state == "waiting_cookie":
            config["cookie"] = text
            del user_states[user_id]
            await update.message.reply_text("✅ **Cookie Successfully Saved!** 🍪", reply_markup=get_main_menu_keyboard())
        
        elif state == "waiting_target":
            config["target_id"] = text
            del user_states[user_id]
            await update.message.reply_text(f"✅ **Target Thread ID Saved:** `{text}` 🎯", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        
        elif state == "waiting_name":
            config["target_name"] = text
            del user_states[user_id]
            await update.message.reply_text(f"✅ **Target Name Saved:** `{text}` 👤", parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    else:
        # Normal chat or unrelated text ignore/optional info
        pass

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("setcookie", set_cookie))
    app.add_handler(CommandHandler("settarget", set_target))
    app.add_handler(CommandHandler("setname", set_name))
    app.add_handler(CommandHandler("startspam", start_spam))
    app.add_handler(CommandHandler("stopspam", stop_spam))
    app.add_handler(CommandHandler("status", status_check))
    
    # Callback & Message Handlers for Interactive Menu UI
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    print("🤖 Supreme Controller Initialized with Interactive Menu UI...")
    app.run_polling()

if __name__ == "__main__":
    main()
            
