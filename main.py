# -*- coding: utf-8 -*-
import os, time, re, threading, gc, sys, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- ⚙️ TUNED SETTINGS (1 Tab, 8 Sec Interval) ---
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
    "target_name": "Target",  
    "custom_text": "Bᴏʟᴇ  𝐀 ɴ ᴋ ɪ ᴛ  पिताश्री  Mᴇʀɪ Mᴀ Cʜᴏᴅ Dᴏ"
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
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.page_load_strategy = 'eager'
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPad Pro"})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    stealth(driver, languages=["en-US"], vendor="Google Inc.", platform="Linux armv8l", fix_hairline=True)
    return driver

def run_agent(agent_id, cookie, target_id, target_name, custom_text):
    global is_running
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION and not stop_event.is_set():
        driver = None
        try:
            print(f"🚀 [Agent {agent_id}] Starting Cycle...")
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            for _ in range(TABS_PER_THREAD):
                if stop_event.is_set(): break
                driver.execute_script("window.open('https://www.instagram.com/direct/t/{}/', '_blank');".format(target_id))
                time.sleep(2)

            for handle in driver.window_handles[1:]:
                if stop_event.is_set(): break
                driver.switch_to.window(handle)
                
                js_code = """
                const delay = arguments[0];
                const targetName = arguments[1];
                const customText = arguments[2];
                let iteration = 0;
                const emojis = ["⟬𝔛𓊈🌀𓊉𝔛⟭", "⟬𝔛𓊈💎𓊉𝔛⟭", "⟬𝔛𓊈❄️𓊉𝔛⟭", "⟬𝔛𓊈🍫𓊉𝔛⟭", "⟬𝔛𓊈🎐𓊉𝔛⟭", "⟬𝔛𓊈🥎𓊉𝔛⟭", "⟬𝔛𓊈💥𓊉𝔛⟭", "⟬𝔛𓊈💢𓊉𝔛⟭", "⟬𝔛𓊈⚾𓊉𝔛⟭", "⟬𝔛𓊈💦𓊉𝔛⟭"];
                
                window.__spamInterval = setInterval(() => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        const currentEmoji = emojis[iteration % emojis.length];
                        const line = "[" + targetName + "]" + customText + currentEmoji;
                        
                        let text = "";
                        for(let i = 0; i < 3; i++) { text += line + "\\n"; }
                        
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
                        }, 500);
                        
                        iteration++;
                    }
                }, delay);
                """
                driver.execute_script(js_code, PULSE_DELAY, target_name, custom_text)

            print(f"🔥 [Agent {agent_id}] 8-Second Spam Pulse Active...")
            
            while not stop_event.is_set():
                time.sleep(1)

        except Exception as e:
            print(f"⚠️ [Agent {agent_id}] Error: {e}")
        finally:
            if driver: driver.quit()
            gc.collect()
            time.sleep(2)

    is_running = False

# --- TELEGRAM BOT HANDLERS ---

async def set_cookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **Usage:** `/setcookie <your_session_id>`")
        return
    config["cookie"] = " ".join(context.args)
    await update.message.reply_text("✅ **Instagram Cookie successfully updated!**")

async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **Usage:** `/settarget <thread_id>`")
        return
    config["target_id"] = context.args[0]
    await update.message.reply_text(f"✅ **Target Thread ID set to:** `{config['target_id']}`")

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **Usage:** `/setname <target_name>` (e.g. `/setname RAJESH`)")
        return
    config["target_name"] = " ".join(context.args)
    await update.message.reply_text(f"✅ **Target Name updated to:** `{config['target_name']}`")

async def set_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ **Usage:** `/settext <custom spam message>`")
        return
    config["custom_text"] = " ".join(context.args)
    await update.message.reply_text(f"✅ **Spam Text updated to:**\n`{config['custom_text']}`")

async def start_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, active_threads, stop_event
    
    if is_running:
        await update.message.reply_text("⚠️ Spam automation is already running!")
        return

    if not config["cookie"] or not config["target_id"]:
        await update.message.reply_text("❌ Missing configuration! Please set cookie using `/setcookie` and target using `/settarget` first.")
        return

    stop_event.clear()
    is_running = True
    active_threads.clear()

    for i in range(THREADS):
        t = threading.Thread(target=run_agent, args=(i+1, config["cookie"], config["target_id"], config["target_name"], config["custom_text"]))
        t.start()
        active_threads.append(t)

    await update.message.reply_text(f"🚀 **Instagram Spam Started!**\n🎯 Target Name: `{config['target_name']}`\n⏱️ Speed: Every 8 seconds")

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, stop_event
    
    if not is_running:
        await update.message.reply_text("⚠️ No spam process is currently active.")
        return

    stop_event.set()
    await update.message.reply_text("🛑 **Stopping Spam Automation...** Cleaning up browsers.")

async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running
    status_msg = (
        f"📊 **Bot Configuration & Status**\n\n"
        f"🟢 **Status:** {'Running (8s interval)' if is_running else 'Stopped'}\n"
        f"🍪 **Cookie Set:** {'Yes' if config['cookie'] else 'No'}\n"
        f"🎯 **Target ID:** `{config['target_id'] if config['target_id'] else 'Not Set'}`\n"
        f"👤 **Target Name:** `{config['target_name']}`\n"
        f"💬 **Current Text:** `{config['custom_text']}`"
    )
    await update.message.reply_text(status_msg)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("setcookie", set_cookie))
    app.add_handler(CommandHandler("settarget", set_target))
    app.add_handler(CommandHandler("setname", set_name))
    app.add_handler(CommandHandler("settext", set_text))
    app.add_handler(CommandHandler("startspam", start_spam))
    app.add_handler(CommandHandler("stopspam", stop_spam))
    app.add_handler(CommandHandler("status", status_check))

    print("🤖 Dynamic Bot Controller Initialized successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
