import os
import requests
import zipfile
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIG ---
GITHUB_USER = "positronacademy2008" 
PRIVATE_REPO = "positron-storage"
BRANCH = "main" 
PARTS = ["whatsapp_session_2.zip.001", "whatsapp_session_2.zip.002", "whatsapp_session_2.zip.003", "whatsapp_session_2.zip.004"]

def download_and_combine_session():
    token = os.environ.get("MY_GITHUB_TOKEN")
    print("🛡️ Downloading session data...")
    try:
        with open("full_session.zip", "wb") as combined_file:
            for part in PARTS:
                url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{PRIVATE_REPO}/{BRANCH}/{part}"
                headers = {'Authorization': f'token {token}'}
                res = requests.get(url, headers=headers)
                if res.status_code == 200:
                    combined_file.write(res.content)
                    print(f"✅ {part} joined.")
                else: return False
        with zipfile.ZipFile("full_session.zip", 'r') as zip_ref:
            zip_ref.extractall("session_data")
        return True
    except: return False

def setup_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    session_path = os.path.join(os.getcwd(), "session_data", "whatsapp_session")
    options.add_argument(f"--user-data-dir={session_path}")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def send_bulk_messages(driver):
    print("⏳ Loading WhatsApp Web...")
    driver.get("https://web.whatsapp.com")
    time.sleep(50) 

    csv_path = "whatsapp/contacts.csv"
    with open(csv_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            phone = "".join(filter(str.isdigit, row['phone']))
            name = row['name']
            msg = f"Namaste {name}, Positron Academy Bhilwara mein naya batch shuru ho raha hai! Admission Open. 8104894648"
            
            print(f"📩 Sending to {name} ({phone})...")
            # Step 1: Direct Link par jaana
            driver.get(f"https://web.whatsapp.com/send?phone={phone}")
            time.sleep(35) 

            try:
                # Step 2: Message Box dhoondhna aur click karna
                print("⌨️ Typing message manually...")
                actions = webdriver.ActionChains(driver)
                actions.send_keys(msg) # Manual typing simulation
                time.sleep(2)
                actions.send_keys(Keys.ENTER) # Final Enter
                actions.perform()
                
                print(f"✅ Message sent to {name}!")
                time.sleep(10)
            except Exception as e:
                driver.save_screenshot(f"error_{phone}.png") # Debugging ke liye photo
                print(f"⚠️ Error with {name}: {e}")

if __name__ == "__main__":
    if download_and_combine_session():
        browser = setup_browser()
        try:
            send_bulk_messages(browser)
        finally:
            browser.quit()
            print("🏁 Finished.")
