# -*- coding: utf-8 -*-
import os, time, re, threading, gc, sys, logging, random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- ⚙️ SUPREME TUNED SETTINGS ---
TOTAL_DURATION = 86400  

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

TELEGRAM_BOT_TOKEN = "8926218603:AAH9YcmIRJ6hwLuvGYC-a0bQoZIKw46aC94"

# Base Floral Emojis List (Target ID will be prefixed dynamically)
RAW_EMOJIS = [
    "<💐>", "<🌸>", "<💮>", "<🪷>", "<🏵️>", "<🌹>", "<🥀>", "<🌺>", 
    "<🌻>", "<🌼>", "<🌷>", "<🪻>", "<⚜️>", "<🍀>", "<☘️>", "<🌿>", 
    "<🍃>", "<🍂>", "<🍁>", "<🌱>", "<🌾>", "<🌵>", "<🌲>", "<🌳>", 
    "<🎋>", "<🎍>", "<🪴>"
]

active_tasks_config = []

stats = {
    "sent_count": 0,
    "last_error": "None ✅"
}

user_states = {}  
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

def send_emergency_alert(error_message):
    stats["last_error"] = error_message
    print(f"🚨 [CRITICAL ALERT] {error_message}")

def change_gc_name_if_needed(driver, new_gc_name):
    try:
        print(f"🔄 [Auto-Name] Checking / Updating GC Name to: '{new_gc_name}'...")
        time.sleep(2)
        
        details_btn = driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'Details') or contains(@aria-label, 'Conversation information')]")
        if details_btn:
            details_btn[0].click()
            time.sleep(2.5)
            
            name_input = driver.find_elements(By.XPATH, "//input[@type='text' and (contains(@value, '') or @placeholder)]")
            if name_input:
                current_val = name_input[0].get_attribute("value")
                if current_val != new_gc_name:
                    name_input[0].click()
                    for _ in range(len(current_val) + 5):
                        name_input[0].send_keys(Keys.BACK_SPACE)
                    time.sleep(0.5)
                    name_input[0].send_keys(new_gc_name)
                    time.sleep(1)
                    
                    save_btn = driver.find_elements(By.XPATH, "//div[text()='Save' or text()='Done']")
                    if save_btn:
                        save_btn[0].click()
                        print(f"✅ [Auto-Name] GC Name successfully updated to: '{new_gc_name}'")
                    time.sleep(1.5)
            
            close_btn = driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'Close') or contains(@aria-label, 'Back')]")
            if close_btn:
                close_btn[0].click()
                time.sleep(1)
    except Exception as e:
        print(f"⚠️ [Auto-Name Warning] Could not change GC name automatically: {e}")

def run_isolated_agent(agent_id, session_cookie, target_ids, pulse_delay_sec):
    global is_running, stats
    global_start = time.time()
    pulse_delay_ms = pulse_delay_sec * 1000
    msg_batch_counter = 0
    name_index = 0
    
    while (time.time() - global_start) < TOTAL_DURATION and not stop_event.is_set():
        driver = None
        try:
            print(f"🚀 [Agent {agent_id}] Initializing Dedicated Browser for Session...")
            driver = get_driver()
            driver.set_page_load_timeout(40)
            
            try:
                driver.get("https://www.instagram.com/")
            except Exception as load_err:
                print(f"⚠️ Page load warning: {load_err}, continuing...")

            sid = re.search(r'sessionid=([^;]+)', session_cookie).group(1) if 'sessionid=' in session_cookie else session_cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            time.sleep(3)
            current_url = driver.current_url
            if "accounts/login" in current_url or "challenge" in current_url:
                send_emergency_alert(f"⚠️ [ANTI-BAN ALERT] Session #{agent_id} Expired or Flagged by Instagram!")
                break

            for idx, tid in enumerate(target_ids):
                if stop_event.is_set(): break
                tid_clean = tid.strip()
                if not tid_clean: continue
                
                if idx == 0:
                    driver.get(f"https://www.instagram.com/direct/t/{tid_clean}/")
                else:
                    driver.execute_script(f"window.open('https://www.instagram.com/direct/t/{tid_clean}/', '_blank');")
                time.sleep(1.5)

            handles = driver.window_handles
            
            # Generate dynamic names using the target ID/name
            first_target = target_ids[0].strip() if target_ids else "Target"
            current_target_name = f"{first_target} ꜱʟᴀᴠᴇ {RAW_EMOJIS[0]}"

            for tab_index, handle in enumerate(handles):
                if stop_event.is_set() or tab_index >= len(target_ids): break
                driver.switch_to.window(handle)
                
                js_code = """
                const delay = arguments[0];
                const targetName = arguments[1];
                
                const styleEmojis = ["💐", "🌸", "💮", "🪷", "🏵️", "🌹", "🥀", "🌺", "🌻", "🌼", "🌷", "🪻", "⚜️", "🍀", "☘️", "🌿", "🍃", "🍂", "🍁", "🌱", "🌾", "🌵", "🌲", "🌳", "🎋", "🎍", "🪴", "🔥", "⚡", "💎"];
                
                window.__spamInterval = setInterval(() => {
                    try {
                        const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                        if (box) {
                            const now = new Date();
                            const timeStr = "[" + String(now.getHours()).padStart(2, '0') + ":" + String(now.getMinutes()).padStart(2, '0') + ":" + String(now.getSeconds()).padStart(2, '0') + "]";
                            
                            const randomEmoji1 = styleEmojis[Math.floor(Math.random() * styleEmojis.length)];
                            const randomEmoji2 = styleEmojis[Math.floor(Math.random() * styleEmojis.length)];
                            
                            const line = targetName + " 𝐂ʜᴜᴘ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ " + timeStr + " " + randomEmoji1 + " " + randomEmoji2;
                            
                            let text = "";
                            for(let i = 0; i < 20; i++) { 
                                text += line + "\\n\\n\\n"; 
                            }
                            text += line;
                            
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
                driver.execute_script(js_code, pulse_delay_ms, current_target_name)

            print(f"🔥 [Agent {agent_id}] Blazing {len(target_ids)} GCs with interval {pulse_delay_sec}s...")
            
            while not stop_event.is_set():
                time.sleep(pulse_delay_sec)
                if not stop_event.is_set():
                    try:
                        cur_url = driver.current_url
                        if "accounts/login" in cur_url or "challenge" in cur_url or "consent" in cur_url:
                            send_emergency_alert(f"🚨 [SECURITY BAN DETECTED] Session #{agent_id} locked during execution!")
                            break
                    except:
                        pass

                    stats["sent_count"] += len(target_ids)
                    msg_batch_counter += 1
                    print(f"📤 [Stats] Agent #{agent_id} batch dispatched! Total sent: {stats['sent_count']}")

                    if msg_batch_counter >= 20 and len(RAW_EMOJIS) > 1:
                        msg_batch_counter = 0
                        name_index = (name_index + 1) % len(RAW_EMOJIS)
                        
                        # Dynamically use target ID/name in rotation
                        active_target_label = target_ids[0].strip() if target_ids else "Target"
                        next_name = f"{active_target_label} ꜱʟᴀᴠᴇ {RAW_EMOJIS[name_index]}"
                        
                        if len(driver.window_handles) > 0:
                            driver.switch_to.window(driver.window_handles[0])
                            change_gc_name_if_needed(driver, next_name)

        except Exception as e:
            err_str = str(e)
            print(f"⚠️ [Agent {agent_id}] Exception caught: {err_str}")
            send_emergency_alert(f"⚠️ [Agent {agent_id} Exception] {err_str[:80]}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            gc.collect()
            time.sleep(3)

# --- UI KEYBOARDS ---
def get_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Account Task", callback_data="menu_add_task"),
            InlineKeyboardButton("📋 View Tasks", callback_data="menu_view_tasks")
        ],
        [
            InlineKeyboardButton("📊 System Status", callback_data="status_check"),
            InlineKeyboardButton("🗑️ Clear All Tasks", callback_data="menu_clear_tasks")
        ],
        [
            InlineKeyboardButton("🚀 LAUNCH ALL THREADS ⚡", callback_data="start_spam"),
            InlineKeyboardButton("🛑 TERMINATE ALL 🛑", callback_data="stop_spam")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [
        [InlineKeyboardButton("⚡ Back to Dashboard", callback_data="refresh_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- TELEGRAM BOT HANDLERS ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    banner = (
        "╔═════════════════════════════╗\n"
        "   ⚡ 𝐀𝐂𝐄 ✖ 𝐌𝐎𝐎𝐍 𝚥²¹ ꜰʟᴏʀᴀʟ ɴᴇxᴜꜱ ⚡\n"
        "╚═════════════════════════════╝\n\n"
        "🔥 **Multi-Account Dynamic GC Spammer**\n"
        "_Made by Ankit_\n"
        "_GC Names Configured: [Target Name/ID] ꜱʟᴀᴠᴇ + Emojis_"
    )
    
    if update.message:
        await update.message.reply_text(banner, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_text(banner, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        except Exception:
            await update.callback_query.message.reply_text(banner, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def start_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, active_threads, stop_event, stats, active_tasks_config
    
    query = update.callback_query
    chat = query.message if query else update.message
    
    if is_running:
        msg = "⚠️ Warning: Engines are already blazing live!"
        if query:
            await query.answer(msg, show_alert=True)
        else:
            await chat.reply_text(msg)
        return

    if not active_tasks_config:
        msg = "❌ Error: No account tasks added yet! Click 'Add Account Task'."
        if query:
            await query.answer(msg, show_alert=True)
        else:
            await chat.reply_text(msg)
        return

    stop_event.clear()
    is_running = True
    active_threads.clear()

    for idx, task in enumerate(active_tasks_config):
        t = threading.Thread(
            target=run_isolated_agent, 
            args=(idx + 1, task["cookie"], task["targets"], task["delay"])
        )
        t.start()
        active_threads.append(t)

    success_msg = (
        f"🚀 **FLORAL SPAM ENGINES LAUNCHED!** ⚡\n\n"
        f"👥 **Active Account Threads:** `{len(active_tasks_config)} Accounts`\n"
        f"📊 **Messages Sent Counter:** `{stats['sent_count']}`\n"
        f"🔄 **Auto GC Name Rotation:** `ACTIVE (Target Name + Emojis)` 🔥"
    )
    if query:
        await query.answer("Engines Blazing Successfully! 🚀")
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
        msg = "⚠️ Engines are currently offline."
        if query:
            await query.answer(msg, show_alert=True)
        else:
            await chat.reply_text(msg)
        return

    stop_event.set()
    stop_msg = f"🛑 **All Engines Terminated!**\n📊 **Total Messages Delivered:** `{stats['sent_count']}`\n⚠️ **Last Status / Error:** `{stats['last_error']}`"
    if query:
        await query.answer("Engines Stopped! 🛑")
        try:
            await query.message.edit_text(stop_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        except Exception:
            await query.message.reply_text(stop_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    else:
        await chat.reply_text(stop_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, stats, active_tasks_config
    query = update.callback_query
    chat = query.message if query else update.message
    
    status_msg = (
        "╔═════════════════════════════╗\n"
        "     📊 ꜰʟᴏʀᴀʟ ᴅɪᴀɢɴᴏꜱᴛɪᴄꜱ 📊\n"
        "╚═════════════════════════════╝\n\n"
        f"🟢 **Engine Status:** `{'🔥 BLAZING LIVE' if is_running else '💤 IDLE / STANDBY'}`\n"
        f"📤 **Total Messages Sent:** `{stats['sent_count']} Blocks` 🚀\n"
        f"👥 **Configured Account Tasks:** `{len(active_tasks_config)} Tasks`\n"
        f"🔄 **Auto GC Name Rotation:** `Dynamic Target Name + Emojis`\n"
        f"🛡️ **Anti-Ban Diagnostics:** `{stats['last_error']}`\n"
        f"💎 **Core Matrix:** `Made by Ankit`"
    )
    if query:
        await query.answer("Diagnostics Refreshed 🔄")
        try:
            await query.message.edit_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        except Exception:
            await query.message.reply_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    else:
        await chat.reply_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

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
    elif data == "menu_clear_tasks":
        active_tasks_config.clear()
        await query.answer("All tasks cleared!", show_alert=True)
        await cmd_start(update, context)
    elif data == "menu_view_tasks":
        if not active_tasks_config:
            txt = "📋 **No tasks added yet.**"
        else:
            txt = f"📋 **Configured Tasks ({len(active_tasks_config)}):**\n\n"
            for i, t in enumerate(active_tasks_config):
                txt += f"**Task #{i+1}:** GCs: `{len(t['targets'])}` | Delay: `{t['delay']}s`\n"
        await query.message.edit_text(txt, parse_mode="Markdown", reply_markup=get_back_keyboard())
    elif data == "menu_add_task":
        user_states[user_id] = {"step": "cookie", "cookie": "", "targets": [], "delay": 8}
        await query.message.edit_text(
            "➕ **ADD ACCOUNT TASK (Step 1/2)**\n\n_Send the raw Instagram `sessionid` for this account:_",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    if user_id in user_states and isinstance(user_states[user_id], dict):
        state_data = user_states[user_id]
        step = state_data.get("step")
        
        if step == "cookie":
            state_data["cookie"] = text
            state_data["step"] = "targets"
            await update.message.reply_text(
                "🎯 **ADD ACCOUNT TASK (Step 2/2)**\n\n_Send Target GC ID(s) or Name(s) for this account (comma separated if multiple):_",
                parse_mode="Markdown"
            )
        elif step == "targets":
            split_ids = re.split(r'[,\n]+', text)
            state_data["targets"] = [i.strip() for i in split_ids if i.strip()]
            
            active_tasks_config.append(state_data.copy())
            del user_states[user_id]
            
            await update.message.reply_text(
                f"✅ **Account Task Saved Successfully!**\nTotal Tasks Saved: `{len(active_tasks_config)}`",
                parse_mode="Markdown",
                reply_markup=get_main_menu_keyboard()
            )

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    print("╔═══════════════════════════════════════════╗")
    print("   ⚡ FLORAL NEXUS ONLINE (Ankit) ⚡         ")
    print("╚═══════════════════════════════════════════╝")
    app.run_polling()

if __name__ == "__main__":
    main()
                
