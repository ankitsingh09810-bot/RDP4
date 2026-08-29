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

def run_isolated_agent(agent_id, session_cookie, target_name, target_ids, pulse_delay_sec):
    global is_running, stats
    global_start = time.time()
    pulse_delay_ms = pulse_delay_sec * 1000
    
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

            for tab_index, handle in enumerate(handles):
                if stop_event.is_set() or tab_index >= len(target_ids): break
                driver.switch_to.window(handle)
                
                js_code = f"""
                const delay = arguments[0];
                const targetName = "{target_name}";
                
                window.__spamInterval = setInterval(() => {{
                    try {{
                        const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                        if (box) {{
                            const now = new Date();
                            const timeStr = "[" + String(now.getHours()).padStart(2, '0') + ":" + String(now.getMinutes()).padStart(2, '0') + ":" + String(now.getSeconds()).padStart(2, '0') + "]";
                            
                            // Exact required format matching screenshots
                            const line = targetName + " 𝐂ʜᴜᴘ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ -(🌙)- " + timeStr;
                            
                            let text = "";
                            for(let i = 0; i < 20; i++) {{ 
                                text += line + "\\n\\n\\n"; 
                            }}
                            text += line;
                            
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
                            }}, 400);
                        }}
                    }} catch(err) {{}}
                }}, delay);
                """
                driver.execute_script(js_code, pulse_delay_ms)

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
                    print(f"📤 [Stats] Agent #{agent_id} batch dispatched! Total sent: {stats['sent_count']}")

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

# --- UI KEYBOARDS (TASK CONTROLLER STYLE) ---
def get_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🚀 Start Session", callback_data="start_spam"),
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
    keyboard = [
        [InlineKeyboardButton("⚡ Back to Main Menu", callback_data="refresh_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_delay_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("⚡ 3s", callback_data="delay_3"),
            InlineKeyboardButton("🔥 5s", callback_data="delay_5"),
            InlineKeyboardButton("⏱️ 8s", callback_data="delay_8")
        ],
        [
            InlineKeyboardButton("⏳ 10s", callback_data="delay_10"),
            InlineKeyboardButton("🐢 15s", callback_data="delay_15"),
            InlineKeyboardButton("🛑 20s", callback_data="delay_20")
        ],
        [InlineKeyboardButton("⚡ Back to Main Menu", callback_data="refresh_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- TELEGRAM BOT HANDLERS ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    banner = (
        "🤖 **MAIN MENU**\n"
        "Select an operation:"
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
        msg = "⚠️ Warning: Session is already running!"
        if query:
            await query.answer(msg, show_alert=True)
        else:
            await chat.reply_text(msg)
        return

    if not active_tasks_config:
        msg = "❌ Error: No tasks added yet! Click 'Add Task'."
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
            args=(idx + 1, task["cookie"], task["target_name"], task["targets"], task["delay"])
        )
        t.start()
        active_threads.append(t)

    # Render Task Controller Cards Style as shown in screenshots
    controller_cards = ""
    for idx, task in enumerate(active_tasks_config):
        threads_str = ", ".join(task["targets"][:5]) # Displaying target IDs neatly
        controller_cards += (
            f"⚙️ **TASK CONTROLLER [T3{idx}69]**\n"
            f"────────────────────────\n"
            f"📊 **Status:** 🟢 RUNNING\n"
            f"🎯 **Target:** `{task['target_name']}`\n"
            f"📋 **Threads/GCs:** `{threads_str}`...\n"
            f"✉️ **Total Sent:** `{stats['sent_count']}`\n"
            f"⏱️ **Live Log:** Cooldown Active ⚡\n\n"
        )

    success_msg = f"🚀 **SESSION STARTED SUCCESSFULLY!**\n\n{controller_cards}"
    
    keyboard = [
        [InlineKeyboardButton("🛑 Stop Task", callback_data="stop_spam")],
        [InlineKeyboardButton("⚡ Main Menu", callback_data="refresh_panel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.answer("Session Started! 🚀")
        try:
            await query.message.edit_text(success_msg, parse_mode="Markdown", reply_markup=reply_markup)
        except Exception:
            await query.message.reply_text(success_msg, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await chat.reply_text(success_msg, parse_mode="Markdown", reply_markup=reply_markup)

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, stop_event
    query = update.callback_query
    chat = query.message if query else update.message
    
    if not is_running:
        msg = "⚠️ Tasks are currently offline."
        if query:
            await query.answer(msg, show_alert=True)
        else:
            await chat.reply_text(msg)
        return

    stop_event.set()
    stop_msg = f"🛑 **Task Terminated!**\n📊 **Total Messages Delivered:** `{stats['sent_count']}`\n⚠️ **Last Status:** `{stats['last_error']}`"
    if query:
        await query.answer("Task Stopped! 🛑")
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
    
    controller_cards = ""
    if not active_tasks_config:
        controller_cards = "_No active task controllers found._\n"
    for idx, task in enumerate(active_tasks_config):
        controller_cards += (
            f"⚙️ **TASK CONTROLLER [T3{idx}69]**\n"
            f"────────────────────────\n"
            f"📊 **Status:** `{'🟢 RUNNING' if is_running else '💤 IDLE'}`\n"
            f"🎯 **Target:** `{task['target_name']}`\n"
            f"✉️ **Total Sent:** `{stats['sent_count']}`\n"
            f"🛡️ **Diagnostics:** `{stats['last_error']}`\n\n"
        )

    status_msg = f"📊 **SYSTEM STATUS & CONTROLLERS**\n\n{controller_cards}"
    
    if query:
        await query.answer("Status Refreshed 🔄")
        try:
            await query.message.edit_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        except Exception:
            await query.message.reply_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
    else:
        await chat.reply_text(status_msg, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def admin_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    info_text = (
        "⚙️ **ADMIN INFO**\n\n"
        "👑 **Bot Owner / Creator:** Ankit\n"
        "⚡ **System Core:** Selenium Stealth + Multi-threading\n"
        "🛡️ **Status:** Active & Ready"
    )
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
        if user_id in user_states:
            del user_states[user_id]
        await cmd_start(update, context)
    elif data == "menu_clear_tasks":
        active_tasks_config.clear()
        await query.answer("All tasks cleared!", show_alert=True)
        await cmd_start(update, context)
    elif data == "menu_view_tasks":
        if not active_tasks_config:
            txt = "📋 **No tasks configured yet.**"
        else:
            txt = f"📋 **Active Task Controllers ({len(active_tasks_config)}):**\n\n"
            for i, t in enumerate(active_tasks_config):
                txt += f"⚙️ **[T3{i}69] Target:** `{t['target_name']}` | GCs: `{len(t['targets'])}` | Delay: `{t['delay']}s`\n"
        await query.message.edit_text(txt, parse_mode="Markdown", reply_markup=get_back_keyboard())
    elif data == "menu_add_task":
        user_states[user_id] = {"step": "cookie", "cookie": "", "target_name": "", "targets": [], "delay": 8.0}
        await query.message.edit_text(
            "➕ **ADD TASK (Step 1/4)**\n\n_Send the Instagram session ID (`sessionid` cookie):_",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard()
        )
    elif data.startswith("delay_"):
        if user_id in user_states and user_states[user_id].get("step") == "delay":
            delay_val = float(data.split("_")[1])
            user_states[user_id]["delay"] = delay_val
            
            # Save task config
            active_tasks_config.append(user_states[user_id].copy())
            del user_states[user_id]
            
            success_txt = f"✅ **Task Controller Created Successfully!**\nTotal Active Tasks: `{len(active_tasks_config)}`"
            await query.message.edit_text(success_txt, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    if user_id in user_states and isinstance(user_states[user_id], dict):
        state_data = user_states[user_id]
        step = state_data.get("step")
        
        if step == "cookie":
            state_data["cookie"] = text
            state_data["step"] = "target_name"
            await update.message.reply_text(
                "🎯 **ADD TASK (Step 2/4)**\n\n_Enter Target Name (e.g. DHURV KINNER or TEST):_",
                parse_mode="Markdown"
            )
        elif step == "target_name":
            state_data["target_name"] = text
            state_data["step"] = "targets"
            await update.message.reply_text(
                "📋 **ADD TASK (Step 3/4)**\n\n_Send Target GC ID(s) (comma or newline separated):_",
                parse_mode="Markdown"
            )
        elif step == "targets":
            split_ids = re.split(r'[,\n]+', text)
            state_data["targets"] = [i.strip() for i in split_ids if i.strip()]
            state_data["step"] = "delay"
            await update.message.reply_text(
                "⏱️ **ADD TASK (Step 4/4)**\n\n_Select message delay speed using the buttons below:_",
                parse_mode="Markdown",
                reply_markup=get_delay_keyboard()
            )

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    print("╔═══════════════════════════════════════════╗")
    print("   ⚡ TASK CONTROLLER BOT ONLINE (Ankit) ⚡   ")
    print("╚═══════════════════════════════════════════╝")
    app.run_polling()

if __name__ == "__main__":
    main()
                
