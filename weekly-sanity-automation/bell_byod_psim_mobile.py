import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
from pathlib import Path

from global_actions import GlobalNav
from checkout_devices import MobileCheckout, DEVICE_PROFILES

# --- 1. SETUP VIRTUAL DISPLAY ---
SELECTED_DEVICE = "iphone_15_pro_max" 

device = DEVICE_PROFILES[SELECTED_DEVICE]
DISPLAY_SIZE = device["display_size"]
display = Display(visible=0, size=DISPLAY_SIZE)
display.start()

# --- 2. CONFIGURATION ---
CONFIG = {
    "file_name": str(Path(__file__).parent / "mobile-views" / f"{Path(__file__).stem}({time.strftime('%m-%d')}).mp4"),
    "target_url": "https://www.bell.ca/",
    "plan_name": "Ultra",
    "esim_imei": "357498198275732",
    "first_name": "Bqat",
    "last_name": "Testing",
    "email": "test@yopmail.com",
    "phone": "4167020880",
    "address": "5115 creekbank",
    "card_number": "4111111111111111",
    "cvv": "625",
    "birthday": "01011991"
}

try:
    options = Options()
    
    # 1. Standard Command-Line Arguments
    chrome_arguments = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        f"--app={CONFIG['target_url']}",
        f"--window-size={DISPLAY_SIZE[0]},{DISPLAY_SIZE[1]}",
        "--disable-features=WebPayments"
    ]
    for argument in chrome_arguments:
        options.add_argument(argument)

    # 2. Browser Internal Preferences (Disables the Popups)
    chrome_prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "autofill.credit_card_enabled": False,
        "autofill.profile_enabled": False
    }
    options.add_experimental_option("prefs", chrome_prefs)

    # 3. Experimental Automation & Emulation Settings
    experimental_settings = {
        "mobileEmulation": {"deviceName": "iPhone 12 Pro"},
        "excludeSwitches": ["enable-automation"],
        "useAutomationExtension": False
    }
    for key, value in experimental_settings.items():
        options.add_experimental_option(key, value)

    driver = webdriver.Chrome(options=options)
    
    # --- 4. INITIALIZE NAV & RECORDING ---
    nav = GlobalNav(driver)
    # Corrected the syntax leak inside the filename parameter here
    nav.start_recording(
        display_num=display.display, 
        display_size=DISPLAY_SIZE, 
        file_name=CONFIG["file_name"]
    )

    print(f"🚀 Starting automated test run for {CONFIG['file_name']} ... \n --- STEP 1: LANDING & NAVIGATION ---")
    
    # --- STEP 1: LANDING & NAVIGATION ---
    driver.get(CONFIG["target_url"])
    print(f"Website: '{CONFIG['target_url']}'")

    nav.landing_popups()

    nav.stable_click((By.ID, "mobileBarNavBtnG"))
    time.sleep(1)
    nav.stable_click((By.XPATH, "//button[contains(., 'Mobility')]"))
    nav.stable_click((By.XPATH, "//a[contains(@href, '/Mobility/Bring-Your-Own-Phone')]"))

    print("Successfully navigated to BYOP.")
    time.sleep(3)

    # --- STEP 2: DYNAMIC PLAN SELECTION ---
    print(f"--- STEP 2: NAVIGATING TO PLAN '{CONFIG['plan_name']}' ---")

    plan_card_xpath = f"//h3[@class='g-card-plan__title' and contains(text(), '{CONFIG['plan_name']}')]/ancestor::div[contains(@class, 'card-plan')]"
    
    try:
        # 1. Find the card and the header
        plan_card = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, plan_card_xpath)))
        plan_header = plan_card.find_element(By.TAG_NAME, "h3")
        
        # 2. First Stage: Scroll the header into view to "anchor" the plan
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", plan_header)
        print("Scrolled to plan header.")
        time.sleep(1.5) 
        
        # 3. Locate the CTA button
        cta_button = plan_card.find_element(By.XPATH, ".//button[contains(text(), 'Bring your own phone')]")
        
        # 4. Second Stage: Scroll the CTA into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", cta_button)
        print("Scrolled to plan CTA.")
        time.sleep(1.0)
        
        # 5. Final Interaction
        nav.stable_click(cta_button, scroll=False)
        print("Successfully clicked the plan CTA button!")

    except Exception as e:
        raise Exception(f"Failed during staged scroll to plan '{CONFIG['plan_name']}': {e}")

    # --- STEP 2.5: HANDLING MODAL SCREENS ---
    print("--- STEP 2.5: HANDLING MODAL SCREENS ---")
    try:
        nav.stable_click((By.ID, "newCustomerButton"))
        print("Clicking New Customer CTA")
        nav.stable_click((By.ID, "btnMobilityOnly"))
        print("Clicking Mobility only CTA")
        
        try:
            WebDriverWait(driver, 20).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(text(), 'Loading')]"))
            )
            WebDriverWait(driver, 20).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(text(), 'Determining')]"))
            )
        except Exception as e:
            print(f"Warning: Loading screen did not disappear: {str(e)}")
    except Exception as e:
        print(f"Failed during modal selection: {str(e)}")

    # --- STEP 3: DYNAMIC SIM ASSIGNMENT ---
    print("--- STEP 3: DYNAMIC SIM ASSIGNMENT ---")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "imei-number")))
    time.sleep(2) 
    nav.start_popup_checker()

    try:
        edit_plan_cta = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "editBtnRatePlanSection_SBPage"))
        )
        nav.stable_click(edit_plan_cta, scroll=True)
        print("Clicked plan Edit link; container section expanded.")
        time.sleep(1.5)

        # 1. Target the Alternative Plan
        alt_plan_radio = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tabpanel-pills-data-allotment']//h3[not(contains(text(), 'Ultra'))]/ancestor::div[contains(@class, 'graphical_ctrl_container')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", alt_plan_radio)
        time.sleep(1) 
        nav.stable_click(alt_plan_radio, scroll=False)
        print("Temporarily switched plan selection to an alternative option.")
        time.sleep(2.0)

        # 2. Target the Original (Ultra) Plan
        ultra_plan_radio = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tabpanel-pills-data-allotment']//h3[contains(text(), 'Ultra')]/ancestor::div[contains(@class, 'graphical_ctrl_container')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ultra_plan_radio)
        time.sleep(1)
        nav.stable_click(ultra_plan_radio, scroll=False)
        print("Restored original selection back to 'Ultra' plan option.")
        time.sleep(1.5)

        # 3. Final Confirmation
        next_step_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "next-step-button-1"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_step_btn)
        time.sleep(1)
        nav.stable_click(next_step_btn, scroll=False)
        print("Clicked 'Next step' confirmation button.")
        
    except Exception as e:
        print(f"Warning: Failed path execution variations adjusting plan configurations: {e}")

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "imei-number")))
    time.sleep(2) 

    imei_input = driver.find_element(By.ID, "imei-number")

    try:
        find_imei_link = driver.find_element(By.ID, "whereToFindImeiInfo")
        if find_imei_link.is_displayed():
            driver.execute_script("arguments[0].click();", find_imei_link)
            time.sleep(1) 
            
            android_tab = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "android")))
            android_tab.click()
            time.sleep(1)
            
            ios_tab = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "iOS")))
            ios_tab.click()
            time.sleep(1)
            
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "closeIMEIModalButton"))).click()
    except Exception as e:
        print(f"Modal interaction failed: {e}")

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "imei-number")))
    time.sleep(2) 
    imei_input = driver.find_element(By.ID, "imei-number")

    psim = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//label[@for='multiSimCard']")))
    nav.stable_click(psim)

    print("Waiting for validation...")
    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'd-none')][.//input[@id='imei-number']]")))
    
    final_next_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "next-step-button-3")))
    driver.execute_script("arguments[0].click();", final_next_btn)

    # --- STEP 4: SUBSCRIPTION & LIGHTBOX HANDLING ---
    print("--- STEP 4: SUBSCRIPTION & LIGHTBOX HANDLING ---")
    try:
        nav.stable_click((By.XPATH, "//button[contains(text(), 'Continue to cart')]"))
    except Exception as e:
        print(f"Continue button failed: {e}")

    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "modal-addition-offers-title")))
        nav.stable_click((By.ID, "eligible_offers_lightbox"))
    except TimeoutException:
        print("No lightbox detected. Proceeding.")
        
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Order summary') or contains(text(), 'Cart')]"))
        )
        print("Successfully reached final Cart page.")
    except Exception as e:
        print(f"Could not confirm reach of final cart: {e}")

    nav.stop_popup_checker()

    # --- STEP 5: CART REVIEW & CHECKOUT START ---
    print("--- STEP 5: CART REVIEW & CHECKOUT START ---")
    try:
        WebDriverWait(driver, 20).until(EC.invisibility_of_element_located((By.ID, "brfLoadingIndicator")))
        checkout_btn = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "next-step-button-undefined")))
        time.sleep(2)

        try:
            footer = driver.find_element(By.XPATH, "//nav[@aria-label='Privacy, security and legal'] | //nav[contains(@class, 'legal-links')]")
            ActionChains(driver).scroll_to_element(footer).perform()
        except Exception:
            driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
        
        time.sleep(3.5)
        nav.stable_click((By.ID, "next-step-button-undefined"), timeout=20)
        print("Successfully proceeded to checkout.")
    except Exception as e:
        print(f"Checkout transition failed: {e}")
        
    try:
        print("--- STARTING INTEGRATED CHECKOUT FLOW ---")
        checkout = MobileCheckout(driver, CONFIG)
        checkout.psim_checkout_flow()
        print("--- CHECKOUT FLOW COMPLETED SUCCESSFULLY ---")
    except Exception as e:
        print(f"❌ Error in CheckoutFlow: {e}")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    # --- 5. CLEANUP HANDLERS ---
    if 'nav' in locals(): 
        nav.stop_recording()
    if 'driver' in locals(): 
        driver.quit()
    display.stop()