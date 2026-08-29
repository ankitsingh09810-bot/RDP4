# -*- coding: utf-8 -*-
import os, time, re, threading, gc, sys, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- ⚙️ SUPREME TUNED SETTINGS ---
THREADS = 1           
TABS_PER_THREAD = 1   
PULSE_DELAY = 8000    # 8 seconds interval
TOTAL_DURATION = 86400  

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Hardcoded Telegram Token
TELEGRAM_BOT_TOKEN = "8926218603:AAH9YcmIRJ6hwLuvGYC-a0bQoZIKw46aC94"

# Runtime Dynamic Storage
config = {
    "cookie": "",
    "target_id": "",
    "target_name": "Target"
}

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
                
                # JS CODE WITH DYNAMIC TIMESTAMP ADDED AT THE END
                js_code = """
                const delay = arguments[0];
                const targetName = arguments[1];
                let iteration = 0;
                
                const messages = [
                    "〔💀〕 " + targetName + " Cʜɪꪀꫝʟ 〔💀〕",
                    "〔🔥〕 " + targetName + " ᴄʜꪊᴛꫝᴅ 〔🔥〕",
                    "〔🩸〕 " + targetName + " ʟꪊᴜɴᴅ ᥴʜᴜડ 〔🩸〕",
                    "〔👹〕 " + targetName + " ᴄʜꪊᴅ 〔👹〕",
                    "〔☣️〕 " + targetName + " ꪑꫝᴅꫝʀCʜꪮᴅ 〔☣️〕",
                    "〔⚔️〕 " + targetName + " ᴋꫝꪑᴊꪮʀ 〔⚔️〕",
                    "〔⛓️〕 " + targetName + " ꜱʟꪖᴠᴇ 〔⛓️〕",
                    "〔🎭〕 " + targetName + " ᴄʜʜꫝᴋᴇ 〔🎭〕",
                    "〔💸〕 " + targetName + " ɢꫝʀᴇᴇʙ 〔💸〕",
                    "〔🦴〕 " + targetName + " ᴄʜꫝᴍꫝꫝʀ 〔🦴〕",
                    "〔💥〕 " + targetName + " ʙʜꪮડᴅɪᴋꫝ 〔💥〕",
                    "〔👑〕 " + targetName + " ɢꫝ᭙ꫝʀ 〔👑〕",
                    "〔😈〕 " + targetName + " ᴊʜꫝᴛᴜ 〔😈〕",
                    "〔🦂〕 " + targetName + " 𝕜ꪊᴛɪꪗꫝ 〔🦂〕",
                    "〔🔗〕 " + targetName + " ɢꪊʟꫝꪑ 〔🔗〕",
                    "〔🚫〕 " + targetName + " ᴛꪑᴋᥴ 〔🚫〕",
                    "〔📛〕 " + targetName + " ᴅꫝʟɪᴛ 〔📛〕",
                    "〔🕷️〕 " + targetName + " ʀꪀᴅꪗᴋꫝ 〔🕷️〕",
                    "〔🪦〕 " + targetName + " ʙʜꫝꪀɢɪ 〔🪦〕"
                ];
                
                window.__spamInterval = setInterval(() => {
                    try {
                        const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                        if (box) {
                            const now = new Date();
                            const timeStr = "[" + String(now.getHours()).padStart(2, '0') + ":" + String(now.getMinutes()).padStart(2, '0') + ":" + String(now.getSeconds()).padStart(2, '0') + "]";
                            
                            const currentMsg = messages[iteration % messages.length] + " ⏳ " + timeStr;
                            let text = currentMsg + "\\n" + currentMsg + "\\n" + currentMsg;
                            
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
                            
                            iteration++;
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

# --- TELEGRAM INLINE KEYBOARD ---
def get_control_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🚀 Start Engine", callback_data="start_spam"),
            InlineKeyboardButton("🛑 Stop Engine", callback_data="stop_spam")
        ],
        [
            InlineKeyboardButton("📊 Check Status", callback_data="status_check"),
            InlineKeyboardButton("🔄 Refresh Panel", callback_data="refresh_panel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- TELEGRAM BOT HANDLERS ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    banner = """╭─────────────────────────╮
🌙 ＡＣＥ ✖ 𝙼𝙾𝙾𝙽 𝚥²¹ 🌙
👁️ ᴀᴄᴇ ᴇᴄᴏꜱʏꜱᴛᴇᴍ 👁️
╰─────────────────────────╯
⚡ **Supreme Insta Controller Bot**
Use commands or tap buttons below:
🔹 `/setcookie <session_id>`
🔹 `/settarget <thread_id>`
🔹 `/setname <target_name>`
═════════════════════"""
    
    if update.message:
        await update.message.reply_text(banner, parse_mode="Markdown", reply_markup=get_control_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(banner, parse_mode="Markdown", reply_markup=get_control_keyboard())

async def set_cookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **Usage:** `/setcookie <your_session_id>`")
        return
    config["cookie"] = " ".join(context.args)
    await update.message.reply_text("✅ **Instagram Cookie successfully locked in!** 🍪", reply_markup=get_control_keyboard())

async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **Usage:** `/settarget <thread_id>`")
        return
    config["target_id"] = context.args[0]
    await update.message.reply_text(f"✅ **Target Thread ID locked:** `{config['target_id']}` 🎯", reply_markup=get_control_keyboard())

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **Usage:** `/setname <target_name>`")
        return
    config["target_name"] = " ".join(context.args)
    await update.message.reply_text(f"✅ **Target Name updated:** `{config['target_name']}` 👤", reply_markup=get_control_keyboard())

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
        msg = "❌ Setup incomplete! Set cookie and target first."
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

    success_msg = f"🚀 **Phoenix Engine Blazing!**\n🎯 Target: `{config['target_name']}`\n⏱️ Interval: Every 8 Seconds (With Timestamp 🔥)"
    if query:
        await query.answer("Engine Started Successfully! 🔥")
        await query.message.reply_text(success_msg, parse_mode="Markdown", reply_markup=get_control_keyboard())
    else:
        await chat.reply_text(success_msg, parse_mode="Markdown", reply_markup=get_control_keyboard())

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
        await query.message.reply_text(stop_msg, parse_mode="Markdown", reply_markup=get_control_keyboard())
    else:
        await chat.reply_text(stop_msg, parse_mode="Markdown", reply_markup=get_control_keyboard())

async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running
    query = update.callback_query
    chat = query.message if query else update.message
    
    status_msg = (
        f"📊 **Supreme Bot Status Hub**\n\n"
        f"🟢 **Engine State:** {'🔥 Blazing Active (8s)' if is_running else '💤 Idle / Stopped'}\n"
        f"🍪 **Cookie Loaded:** {'Yes ✅' if config['cookie'] else 'No ❌'}\n"
        f"🎯 **Target ID:** `{config['target_id'] if config['target_id'] else 'Not Set'}`\n"
        f"👤 **Target Name:** `{config['target_name']}`\n"
        f"💬 **Spam Matrix:** `Dangerous List + Live Timestamps ⏳`"
    )
    if query:
        await query.answer("Status Refreshed 🔄")
        await query.message.edit_text(status_msg, parse_mode="Markdown", reply_markup=get_control_keyboard())
    else:
        await chat.reply_text(status_msg, parse_mode="Markdown", reply_markup=get_control_keyboard())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "start_spam":
        await start_spam(update, context)
    elif data == "stop_spam":
        await stop_spam(update, context)
    elif data == "status_check":
        await status_check(update, context)
    elif data == "refresh_panel":
        await cmd_start(update, context)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("setcookie", set_cookie))
    app.add_handler(CommandHandler("settarget", set_target))
    app.add_handler(CommandHandler("setname", set_name))
    app.add_handler(CommandHandler("startspam", start_spam))
    app.add_handler(CommandHandler("stopspam", stop_spam))
    app.add_handler(CommandHandler("status", status_check))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 Supreme Controller with Timestamp Matrix Initialized & Polling active...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
