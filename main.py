# -*- coding: utf-8 -*-
import os, time, re, threading, gc, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth

# --- ⚙️ V100 TUNED SETTINGS ---
THREADS = 2             
PULSE_DELAY = 100       
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

def run_agent(agent_id, cookie, target_id, custom_msg):
    global_start = time.time()
    
    while (time.time() - global_start) < TOTAL_DURATION:
        driver = None
        try:
            print(f"🚀 [Agent {agent_id}] Starting cycle...")
            driver = get_driver()
            driver.get("https://www.instagram.com/")
            
            sid = re.search(r'sessionid=([^;]+)', cookie).group(1) if 'sessionid=' in cookie else cookie
            driver.add_cookie({'name': 'sessionid', 'value': sid.strip(), 'domain': '.instagram.com'})
            
            driver.get(f"https://www.instagram.com/direct/t/{target_id}/")
            time.sleep(5) 

            driver.execute_script("""
                const msg = arguments[0];
                const delay = arguments[1];
                
                setInterval(() => {
                    const box = document.querySelector('div[role="textbox"], [contenteditable="true"]');
                    if (box) {
                        box.focus();
                        document.execCommand('insertText', false, msg);
                        box.dispatchEvent(new Event('input', { bubbles: true }));

                        const enter = new KeyboardEvent('keydown', {
                            bubbles: true, cancelable: true, key: 'Enter', code: 'Enter', keyCode: 13
                        });
                        box.dispatchEvent(enter);
                    }
                }, delay);
            """, custom_msg, PULSE_DELAY)

            time.sleep(SESSION_MAX_SEC) 
        except Exception as e:
            print(f"⚠️ [Agent {agent_id}] Cycle Error: {e}")
        finally:
            if driver: driver.quit()
            gc.collect() 
            time.sleep(2)

def main():
    cookie = os.environ.get("INSTA_COOKIE")
    target_id = os.environ.get("TARGET_THREAD_ID")
    # This retrieves the multi-line text from your GitHub Secret
    custom_message = os.environ.get("CUSTOM_MESSAGE", "Default Text")

    if not cookie or not target_id:
        print("❌ Missing Secrets!")
        return

    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=run_agent, args=(i+1, cookie, target_id, custom_message))
        t.start()
        threads.append(t)
        time.sleep(10)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
