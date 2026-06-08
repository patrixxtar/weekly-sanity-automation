import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
from pathlib import Path

from global_actions import GlobalNav
from checkout_devices import MobileCheckout, DEVICE_PROFILES

# --- 1. START VIRTUAL DISPLAY (In-Memory Framebuffer) ---
SELECTED_DEVICE = "tablet_mobile_ui"

device = DEVICE_PROFILES[SELECTED_DEVICE]
DISPLAY_SIZE = (device["display_size"])
display = Display(visible=0, size=DISPLAY_SIZE)
display.start()

# --- CONFIGURATION DATA ---
CONFIG = {
    "file_name": str(Path(__file__).parent / "tablet-views" / f"{Path(__file__).stem}({time.strftime('%m-%d')}).mp4"),
    "target_url": "https://www.virginplus.ca/",
    "device_name": "iPhone 17",
}

try:
    # --- 2. CONFIGURE CONTAINER-SAFE CHROME OPTIONS ---
    options = Options()
    
    # Standard Command-Line Arguments
    chrome_arguments = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        f"--app={CONFIG['target_url']}",
        f"--window-size={DISPLAY_SIZE[0]},{DISPLAY_SIZE[1]}",
        "--start-maximized",
        "--disable-features=WebPayments"
    ]
    for argument in chrome_arguments:
        options.add_argument(argument)

    # Browser Internal Preferences (Disables "Save Card" & Credit Card Popups)
    chrome_prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "autofill.credit_card_enabled": False,
        "autofill.profile_enabled": False
    }
    options.add_experimental_option("prefs", chrome_prefs)

    # Experimental Automation Settings
    experimental_settings = {
        "excludeSwitches": ["enable-automation"],
        "useAutomationExtension": False
    }
    for key, value in experimental_settings.items():
        options.add_experimental_option(key, value)

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    # --- 3. INITIALIZE NAV & RECORDING ---
    nav = GlobalNav(driver)
    # The class now internally verifies the workspace folders and provisions the background FFmpeg stream
    nav.start_recording(
        display_num=display.display, 
        display_size=DISPLAY_SIZE, 
        file_name=CONFIG["file_name"],
    )

    # --- STEP 1: LANDING & NAVIGATION ---
    driver.get(CONFIG["target_url"])

    print(f"Website: '{CONFIG['target_url']}'")
    
    nav.landing_popups()
    nav.stable_click((By.XPATH, "//a[contains(@class, 'accss-mobile-menu-button')]"))
    nav.stable_click((By.XPATH, "//div[@role='button' and contains(., 'Mobile')]"))
    nav.stable_click((By.XPATH, "//a[contains(@href, '/en/phones/phones-summary.html#!/A3112012,A3111990-0/phones')]"))

    print("Successfully navigated to Device page.")
    time.sleep(2)

    checkout = MobileCheckout(driver, CONFIG)
    checkout.virgin_new_device()

    print("Finalizing recording... pausing for 5 seconds.")
    time.sleep(5)

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    # --- 4. TEARDOWN LIFECYCLE NODE ABSTRACTION ---
    if 'nav' in locals(): 
        nav.stop_recording()
    if 'driver' in locals(): 
        driver.quit()
    display.stop()