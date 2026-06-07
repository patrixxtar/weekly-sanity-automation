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
from checkout_devices import MobileCheckout, DEVICE_PROFILES

# --- 1. START VIRTUAL DISPLAY (In-Memory Framebuffer) ---
SELECTED_DEVICE = "tablet_desktop_ui"

device = DEVICE_PROFILES[SELECTED_DEVICE]
DISPLAY_SIZE = device["display_size"]
display = Display(visible=0, size=DISPLAY_SIZE)
display.start()

# --- CONFIGURATION DATA ---
CONFIG = {
    "file_name": str(Path(__file__).parent / "tablet-views" / f"{Path(__file__).stem}({time.strftime('%m-%d')}).mp4"),
    "target_url": "https://www.virginplus.ca/",
    "plan_name": "60GB data, talk & text",
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
        f"--app={CONFIG['target_url']}",
        f"--window-size={DISPLAY_SIZE[0]},{DISPLAY_SIZE[1]}",
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
        "mobileEmulation": device["mobile_emulation"],
        "excludeSwitches": ["enable-automation"],
        "useAutomationExtension": False
    }
    for key, value in experimental_settings.items():
        options.add_experimental_option(key, value)

    driver = webdriver.Chrome(options=options)

    # --- 3. INITIALIZE NAV & RECORDING ---
    nav = GlobalNav(driver)
    # The class now internally verifies the workspace folders and provisions the background FFmpeg stream
    nav.start_recording(
        display_num=display.display, 
        display_size=DISPLAY_SIZE, 
        file_name=CONFIG["file_name"],
    )

    print(f"🚀 Starting automated test run for {CONFIG['file_name']} ... \n --- STEP 1: LANDING & NAVIGATION ---")
    
    # --- STEP 1: LANDING & NAVIGATION ---
    driver.get(CONFIG["target_url"])
    print(f"Website: '{CONFIG['target_url']}'")
    
    nav.landing_popups()

    nav.stable_click((By.XPATH, "//div[@role='button' and contains(., 'Mobile')]"))
    nav.stable_click((By.XPATH, "//a[contains(@href, '/en/hot-offers/byop.html')]"))

    print("Successfully navigated to BYOP.")
    time.sleep(2)

    nav.stable_click((By.XPATH, "//a[text()='Select a plan' or text()='Activate now']"))
    time.sleep(3)

    # --- STEP 2: DYNAMIC PLAN SELECTION ---
    print(f"--- STEP 2: FINDING AND SELECTING PLAN '{CONFIG['plan_name']}' ---")

    # Fixed: Closed out the dangling string wrapper to correctly compile the XPath rule
    plan_card_xpath = f"//div[contains(@class, 'planHeading') and contains(., '{CONFIG['plan_name']}')]/ancestor::plan-container"

    try:
        initial_next_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, plan_card_xpath))
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
            plan_card = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, plan_card_xpath))
            )
            if plan_card.is_displayed():
                print(f"Found plan '{CONFIG['plan_name']}' and it is visible!")
                card_found = True
                break
        except:
            print(f"Plan not visible yet. Checking again (Attempt {attempt + 1}/{max_scroll_attempts})...")

        try:
            # Since there is no carousel button to press, we try to force another view refresh scroll if not visible
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", plan_card)
            time.sleep(2)
        except Exception as e:
            print("Could not re-scroll to plan container.")
            break

    if not card_found:
        raise Exception(f"Failed to find and navigate to plan: {CONFIG['plan_name']}")

    time.sleep(1)

    try:
        # Find all plan containers on the page to figure out which position our plan card occupies
        all_plans = driver.find_elements(By.XPATH, "//plan-container")
        
        # Determine the 1-based index (e.g., 1, 2, 3...) of our selected plan_card
        initial_plan_index = [i for i, el in enumerate(all_plans, 1) if el == plan_card][0]
        print(f"Dynamically captured target plan index position: {initial_plan_index}")
    except Exception as e:
        initial_plan_index = 1  # Fallback default safety net
        print(f"Warning: Could not dynamically extract index position, defaulting to 1. Error: {e}")

    cta_button = plan_card.find_element(By.XPATH, ".//a[@role='button' and contains(., 'Select plan')]")
    nav.stable_click(cta_button)
    print("Successfully clicked the plan CTA button!")
    
    # --- STEP 2.5: HANDLING MODAL SCREENS ---
    print("--- STEP 2.5: HANDLING MODAL SCREENS ---")
    try:
        get_started_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "addaline-newline-heading-link2"))
        )

        nav.stable_click((By.ID, "addaline-newline-heading-link2"))
        print(f"Clicking New Customer CTA")
        
        try:
            WebDriverWait(driver, 20).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(text(), 'Determining')]"))
            )

            WebDriverWait(driver, 20).until(
                EC.invisibility_of_element_located((By.XPATH, "//div[contains(text(), 'Loading')]"))
            )

        except Exception as e:
            print(f"Warning: Loading screen did not disappear: {str(e)}")
    except Exception as e:
        print(f"Failed during modal selection: {str(e)}")

    # --- STEP 3: DYNAMIC SIM ASSIGNMENT ---
    print("--- STEP 3: DYNAMIC SIM ASSIGNMENT ---")
    plan_next_step = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "next-step-button-1")))
    time.sleep(2) 

    nav.stable_click(plan_next_step)

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "esim-number-input")))
    time.sleep(2)

    try:
        edit_plan_cta = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "edit-rateplan-link"))
        )
        nav.stable_click(edit_plan_cta)
        print("Clicked plan Edit link; container section expanded.")
        time.sleep(1.5)

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "tab-0"))
        )
        time.sleep(1.5)

        # --- CAROUSEL SCROLLING LOGIC ---
        print("Simulating carousel browsing...")
        
        # 1. Get the total count of dots first without storing the elements
        dot_xpath = "//ul[@id='radioCard-carousel-1-pagination']//button"
        dots_count = len(driver.find_elements(By.XPATH, dot_xpath))
        
        for idx in range(dots_count):
            # Skip the first dot since it's active by default
            if idx > 0:
                # 2. Re-fetch the specific dot on every iteration to avoid stale elements
                current_dot = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"({dot_xpath})[{idx + 1}]"))
                )
                nav.stable_click(current_dot)
                print(f"Scrolled to carousel slide {idx + 1}")
                time.sleep(1.2) # Brief pause to view the slide text/contents

        # Re-center the carousel back to the first view page before making changes
        if dots_count > 0:
            first_dot = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"({dot_xpath})[1]"))
            )
            nav.stable_click(first_dot)
            time.sleep(1.0)
        # --------------------------------

        radio_xpath = "//input[@type='radio' and @name='rate-plan']"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, radio_xpath)))
        plan_radios = driver.find_elements(By.XPATH, radio_xpath)

        alt_index_pos = 0 if initial_plan_index != 0 and initial_plan_index != '0' else 1
        alt_plan_radio = plan_radios[alt_index_pos]

        nav.stable_click(alt_plan_radio)
        print("Temporarily switched plan selection to an alternative option.")
        time.sleep(2.0)

        plan_radios = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, radio_xpath))
        )
        original_plan_radio = plan_radios[int(initial_plan_index)]
        
        nav.stable_click(original_plan_radio)
        print("Restored original selection back.")
        time.sleep(2.0)

        next_step_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "next-step-button-1"))
        )
        nav.stable_click(next_step_btn)
        print("Clicked 'Next step' confirmation button pipeline layout node.")
        
    except Exception as e:
        print(f"Warning: Failed path execution variations adjusting plan configurations: {e}")

    
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "esim-number-input")))
    time.sleep(2) 

    try:
        print("Waiting for activation options loading overlay to disappear...")
        loader_xpath = "//*[@aria-busy='true' and @role='alert']"
        WebDriverWait(driver, 20).until(
            EC.invisibility_of_element_located((By.XPATH, loader_xpath))
        )
        print("Loader has disappeared. Proceeding to IMEI steps.")
    except Exception as e:
        print(f"Warning: Loader didn't clear or wasn't found, attempting to proceed: {e}")


    try:
        find_imei_link = driver.find_element(By.ID, "find-esim-num-link")
        if find_imei_link.is_displayed():
            nav.stable_click(find_imei_link)
            time.sleep(1)

            try:
                android_tab = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "tab-Android-IMEI")))
                nav.stable_click(android_tab)
                time.sleep(1)

                ios_tab = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "tab-iOS-IMEI")))
                nav.stable_click(ios_tab)
                time.sleep(1)
            except TimeoutException:
                print("Android or iOS tab did not appear within timeout. Skipping tab clicks.")

            print("Closing the modal...")    
            nav.stable_click((By.ID, "modal-IMEI-Header-close-button"))

    except Exception as e:
        print(f"Modal interaction failed: {e}")
    
    WebDriverWait(driver, 30).until(EC.invisibility_of_element((By.ID, "modal-IMEI-Header-close-button")))
    imei_input = driver.find_element(By.ID, "esim-number-input")

    try:
        print(f"Entering IMEI: '{CONFIG['esim_imei']}' ...")
        imei_input.clear()
        imei_input.send_keys(CONFIG["esim_imei"])
        driver.execute_script("arguments[0].dispatchEvent(new Event('blur'));", imei_input)
    except Exception as e:
        print(f"Failed to enter IMEI: {e}")

    time.sleep(1.5)
    
    final_next_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "add-to-cart-button-1")))
    nav.stable_click(final_next_btn)

    # --- STEP 4: CART REVIEW & CHECKOUT START ---
    print("--- STEP 4: CART REVIEW & CHECKOUT START ---")
    try:
        WebDriverWait(driver, 20).until(
            EC.any_of(
                EC.invisibility_of_element_located((By.ID, "brfLoadingIndicator")),
                EC.invisibility_of_element_located((By.XPATH, "//*[contains(@class, 'vrui-animate-icons-flipper')] | //*[contains(text(), 'Loading shopping cart.')]"))
            )
        )
        checkout_btn = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "proceed-to-checkout-button")))
        time.sleep(2)

        try:
            footer = driver.find_element(By.XPATH, "//nav[@aria-label='Privacy, security and legal'] | //nav[contains(@class, 'legal-links')]")
            ActionChains(driver).scroll_to_element(footer).perform()
        except Exception:
            driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
        
        time.sleep(3.5)
        nav.stable_click((By.ID, "proceed-to-checkout-button"), timeout=20)
        print("Successfully proceeded to checkout.")
    except Exception as e:
        print(f"Checkout transition failed: {e}")
        
    try:
        print("--- STARTING INTEGRATED CHECKOUT FLOW ---")
        checkout = MobileCheckout(driver, CONFIG)
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