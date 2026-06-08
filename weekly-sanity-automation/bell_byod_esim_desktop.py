import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display
from pathlib import Path

from global_actions import GlobalNav
from checkout_devices import DesktopCheckout

# --- 1. START VIRTUAL DISPLAY (In-Memory Framebuffer) ---
DISPLAY_SIZE = (2560, 1440)
display = Display(visible=0, size=DISPLAY_SIZE)
display.start()

# --- CONFIGURATION DATA ---
CONFIG = {
    "file_name": str(Path(__file__).parent / "desktop-views" / f"{Path(__file__).stem}({time.strftime('%m-%d')}).mp4"),
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
    # --- 2. CONFIGURE CONTAINER-SAFE CHROME OPTIONS ---
    options = Options()
    
    # Standard Command-Line Arguments
    chrome_arguments = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
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
        file_name=CONFIG["file_name"]
    )
    
    # --- STEP 1: LANDING & NAVIGATION ---
    driver.get(CONFIG["target_url"])
    print(f"Website: '{CONFIG['target_url']}'")
    
    nav.landing_popups()
    nav.stable_click((By.XPATH, "//button[contains(., 'Mobility')]"))
    nav.stable_click((By.XPATH, "//a[contains(@href, '/Mobility/Bring-Your-Own-Phone')]"))

    print("Successfully navigated to BYOP.")
    time.sleep(3)

    # --- STEP 2: DYNAMIC PLAN SELECTION ---
    print(f"--- STEP 2: FINDING AND SELECTING PLAN '{CONFIG['plan_name']}' ---")

    plan_card_xpath = f"//h3[@class='g-card-plan__title' and contains(text(), '{CONFIG['plan_name']}')]/ancestor::div[contains(@class, 'card-plan')]"
    carousel_next_xpath = "//button[contains(@class, 'slick-next')]" 

    try:
        initial_next_btn = wait.until(
            EC.presence_of_element_located((By.XPATH, carousel_next_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", initial_next_btn)
        print("Scrolled vertically to the carousel section.")
        time.sleep(1.5) 
    except Exception as e:
        print("Warning: Could not do initial scroll to carousel. Proceeding anyway...")

    max_scroll_attempts = 6
    card_found = False

    for attempt in range(max_scroll_attempts):
        try:
            plan_card = wait.until(
                EC.presence_of_element_located((By.XPATH, plan_card_xpath))
            )
            if plan_card.is_displayed():
                print(f"Found plan '{CONFIG['plan_name']}' and it is visible!")
                card_found = True
                break
        except:
            print(f"Plan not visible yet. Advancing carousel (Attempt {attempt + 1}/{max_scroll_attempts})...")

        try:
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, carousel_next_xpath))
            )
            if next_button.get_attribute("aria-disabled") == "true":
                print("Reached the end of the carousel. 'Next' button is disabled.")
                break
                
            nav.stable_click(next_button)
            time.sleep(2)
        except Exception as e:
            print("Could not click carousel next button.")
            break

    if not card_found:
        raise Exception(f"Failed to find and navigate to plan: {CONFIG['plan_name']}")

    time.sleep(1)
    cta_button = plan_card.find_element(By.XPATH, ".//button[contains(text(), 'Bring your own phone')]")
    nav.stable_click(cta_button)
    print("Successfully clicked the plan CTA button!")
    
    # --- STEP 2.5: HANDLING MODAL SCREENS ---
    print("--- STEP 2.5: HANDLING MODAL SCREENS ---")
    try:
        nav.stable_click((By.ID, "newCustomerButton"))
        print("Clicking New Customer CTA")
        nav.stable_click((By.ID, "btnMobilityOnly"))
        print("Clicking Mobility only CTA")
        
        try:
            wait.until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(text(), 'Loading')]"))
            )
            wait.until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(text(), 'Determining')]"))
            )
        except Exception as e:
            print(f"Warning: Loading screen did not disappear: {str(e)}")
    except Exception as e:
        print(f"Failed during modal selection: {str(e)}")

    # --- STEP 3: DYNAMIC SIM ASSIGNMENT ---
    print("--- STEP 3: DYNAMIC SIM ASSIGNMENT ---")
    wait.until(EC.presence_of_element_located((By.ID, "imei-number")))
    time.sleep(2) 
    nav.start_popup_checker()

    try:
        edit_plan_cta = wait.until(
            EC.element_to_be_clickable((By.ID, "editBtnRatePlanSection_SBPage"))
        )
        nav.stable_click(edit_plan_cta)
        print("Clicked plan Edit link; container section expanded.")
        time.sleep(1.5)

        wait.until(
            EC.visibility_of_element_located((By.ID, "tabpanel-pills-data-allotment"))
        )
        time.sleep(1.5)

        alt_plan_radio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tabpanel-pills-data-allotment']//h3[not(contains(text(), 'Ultra'))]/ancestor::div[contains(@class, 'graphical_ctrl_container')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", alt_plan_radio)
        time.sleep(0.5)
        nav.stable_click(alt_plan_radio)
        print("Temporarily switched plan selection to an alternative option.")
        time.sleep(2.0)

        ultra_plan_radio = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tabpanel-pills-data-allotment']//h3[contains(text(), 'Ultra')]/ancestor::div[contains(@class, 'graphical_ctrl_container')]"))
        )
        nav.stable_click(ultra_plan_radio)
        print("Restored original selection back to 'Ultra' plan option.")
        time.sleep(2.0)

        next_step_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "next-step-button-1"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_step_btn)
        time.sleep(0.5)
        nav.stable_click(next_step_btn)
        print("Clicked 'Next step' confirmation button pipeline layout node.")
        
    except Exception as e:
        print(f"Warning: Failed path execution variations adjusting plan configurations: {e}")

    wait.until(EC.presence_of_element_located((By.ID, "imei-number")))
    time.sleep(2) 

    try:
        find_imei_link = driver.find_element(By.ID, "whereToFindImeiInfo")
        if find_imei_link.is_displayed():
            nav.stable_click(find_imei_link)
            time.sleep(1)
            close_btn = wait.until(EC.element_to_be_clickable((By.ID, "closeIMEIModalButton")))
            nav.stable_click(close_btn)
    except:
        pass
    
    wait.until(EC.invisibility_of_element((By.ID, "closeIMEIModalButton")))
    imei_input = driver.find_element(By.ID, "imei-number")

    try:
        print(f"Entering IMEI: '{CONFIG['esim_imei']}' ...")
        imei_input.clear()
        imei_input.send_keys(CONFIG["esim_imei"])
        driver.execute_script("arguments[0].dispatchEvent(new Event('blur'));", imei_input)
    except Exception as e:
        print(f"Failed to enter IMEI: {e}")

    print("Waiting for validation...")
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "icon-checkmark")))
    
    final_next_btn = wait.until(EC.element_to_be_clickable((By.ID, "addToCartCTA")))
    driver.execute_script("arguments[0].click();", final_next_btn)

    # --- STEP 4: SUBSCRIPTION & LIGHTBOX HANDLING ---
    print("--- STEP 4: SUBSCRIPTION & LIGHTBOX HANDLING ---")
    try:
        nav.stable_click((By.XPATH, "//button[contains(text(), 'Continue to cart')]"))
    except Exception as e:
        print(f"Continue button failed: {e}")

    try:
        wait.until(EC.visibility_of_element_located((By.ID, "modal-addition-offers-title")))
        nav.stable_click((By.ID, "eligible_offers_lightbox"))
    except TimeoutException:
        print("No lightbox detected. Proceeding.")
        
    try:
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Order summary') or contains(text(), 'Cart')]"))
        )
        print("Successfully reached final Cart page.")
    except Exception as e:
        print(f"Could not confirm reach of final cart: {e}")

    nav.stop_popup_checker()

    # --- STEP 5: CART REVIEW & CHECKOUT START ---
    print("--- STEP 5: CART REVIEW & CHECKOUT START ---")
    try:
        wait.until(EC.invisibility_of_element_located((By.ID, "brfLoadingIndicator")))
        checkout_btn = wait.until(EC.element_to_be_clickable((By.ID, "next-step-button-undefined")))

        try:
            footer = driver.find_element(By.XPATH, "//nav[@aria-label='Privacy, security and legal'] | //nav[contains(@class, 'legal-links')]")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", footer)
        except Exception:
            driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
        
        time.sleep(3.5)
        nav.stable_click((By.ID, "next-step-button-undefined"), timeout=20)
        print("Successfully proceeded to checkout.")
    except Exception as e:
        print(f"Checkout transition failed: {e}")
        
    try:
        print("--- STARTING INTEGRATED CHECKOUT FLOW ---")
        checkout = DesktopCheckout(driver, CONFIG)
        checkout.esim_checkout_flow()
        print("--- CHECKOUT FLOW COMPLETED SUCCESSFULLY ---")
    except Exception as e:
        print(f"❌ Error in CheckoutFlow: {e}")

except Exception as e:
    print(f"❌ Error: {e}")

finally:
    # --- 4. TEARDOWN LIFECYCLE NODE ABSTRACTION ---
    if 'nav' in locals(): 
        nav.stop_recording()
    if 'driver' in locals(): 
        driver.quit()
    display.stop()