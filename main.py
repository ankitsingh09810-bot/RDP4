# -*- coding: utf-8 -*-
import os, time, re, threading, gc, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# --- ⚙️ V100 TUNED SETTINGS ---
THREADS = 2           
TABS_PER_THREAD = 2   
PULSE_DELAY = 2000    
SESSION_MAX_SEC = 120   
TOTAL_DURATION = 25000  

sys.stdout.reconfigure(encoding='utf-8')

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

def run_agent(agent_id, cookie, target_id):
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        try:
            print(f"🚀 [Agent {agent_id}] Starting Cycle...")
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            for _ in range(TABS_PER_THREAD):
                driver.execute_script("window.open('https://www.instagram.com/direct/t/{}/', '_blank');".format(target_id))
                time.sleep(2)

            for handle in driver.window_handles[1:]:
                driver.switch_to.window(handle)
                # Heart-rotation logic integrated into JS
                js_code = """
                const delay = arguments[0];
                let iteration = 0;
                const emojis = ["⟬𝔛𓊈🌀𓊉𝔛⟭", "⟬𝔛𓊈💎𓊉𝔛⟭", "⟬𝔛𓊈❄️𓊉𝔛⟭", "⟬𝔛𓊈🍫𓊉𝔛⟭", "⟬𝔛𓊈🎐𓊉𝔛⟭", "⟬𝔛𓊈🥎𓊉𝔛⟭", "⟬𝔛𓊈💥𓊉𝔛⟭", "⟬𝔛𓊈💢𓊉𝔛⟭", "⟬𝔛𓊈⚾𓊉𝔛⟭", "⟬𝔛𓊈💦𓊉𝔛⟭"];
                
                setInterval(() => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        const currentEmoji = emojis[iteration % emojis.length];
                        const line = "[ᴘʀᴀᴛɪᴋ-ᴠᴇᴇʀ-ꜱᴜʀᴀᴊ-ɴᴇᴍᴇꜱɪꜱ]Bᴏʟᴇ  𝐀 ɴ ᴋ ɪ ᴛ  पिताश्री  Mᴇʀɪ Mᴀ Cʜᴏᴅ Dᴏ" + currentEmoji;
                        
                        let text = "";
                        for(let i = 0; i < 10; i++) { text += line + "\\n\\n\\n\\n"; }
                        
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
                driver.execute_script(js_code, PULSE_DELAY)

            print(f"🔥 [Agent {agent_id}] Heart-Rotation Active...")
            time.sleep(SESSION_MAX_SEC) 

        except Exception as e:
            print(f"⚠️ [Agent {agent_id}] Error: {e}")
        finally:
            if driver: driver.quit()
            gc.collect()
            time.sleep(2)

def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")

    if not cookie or not target_id:
        print("❌ Missing Secrets!")
        return

    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=run_agent, args=(i+1, cookie, target_id))
        t.start()
        threads.append(t)
        time.sleep(10)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
