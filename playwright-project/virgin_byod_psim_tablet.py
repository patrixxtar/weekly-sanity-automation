import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import stealth_page
from global_actions import GlobalNav
from checkout_devices import MobileCheckout, DEVICE_PROFILES

SELECTED_DEVICE = "tablet_mobile_ui"
device_config = DEVICE_PROFILES[SELECTED_DEVICE]

# Ensure output storage directory structure is present locally
VIDEO_DIR = Path(__file__).parent / "tablet-views"
os.makedirs(VIDEO_DIR, exist_ok=True)

CONFIG = {
    "video_dir": str(VIDEO_DIR),
    "final_video_name": f"{Path(__file__).stem}({time.strftime('%m-%d')}).mp4",
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

def run():
    with sync_playwright() as p:
        print(f"🚀 Starting automated test run context...")
        
        # Launch Chromium with explicit arguments
        browser = p.chromium.launch(
        headless=True,  # Toggle to False to step inside visually
        channel="chrome",
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-features=WebPayments"]
        )
        
        # Leverage Playwright's native emulation and video recording
        context = browser.new_context(
            viewport=device_config["viewport"],
            user_agent=device_config["user_agent"],
            is_mobile=device_config["is_mobile"],
            has_touch=device_config["has_touch"],
            record_video_dir=CONFIG["video_dir"]
        )
        
        page = context.new_page()
        stealth_sync(page)
        nav = GlobalNav(page)
        
        try:
            print("--- STEP 1: LANDING & NAVIGATION ---")
            page.goto(CONFIG["target_url"])
            print(f"Website: '{CONFIG['target_url']}'")
            
            nav.landing_popups()

            nav.stable_click("//a[contains(@class, 'accss-mobile-menu-button')]")
            nav.stable_click("//div[@role='button' and contains(., 'Mobile')]")
            nav.stable_click("//a[contains(@href, '/en/hot-offers/byop.html')]")
            print("Successfully navigated to BYOP.")
            page.wait_for_timeout(2000)

            nav.stable_click(page.locator("//a[text()='Select a plan' or text()='Activate now']").first)
            page.wait_for_timeout(3000)

            # --- STEP 2: DYNAMIC PLAN SELECTION ---
            print(f"--- STEP 2: FINDING AND SELECTING PLAN '{CONFIG['plan_name']}' ---")

            plan_card_xpath = f"//div[contains(@class, 'planHeading') and contains(., '{CONFIG['plan_name']}')]/ancestor::plan-container"
            plan_card = page.locator(plan_card_xpath).first

            try:
                plan_card.wait_for(state="attached", timeout=10000)
                plan_card.scroll_into_view_if_needed()
                print("Scrolled vertically to the carousel section.")
                page.wait_for_timeout(1500)
            except Exception:
                print("Warning: Could not do initial scroll to carousel. Proceeding anyway...")

            if plan_card.is_visible():
                print(f"Found plan '{CONFIG['plan_name']}' and it is visible!")
            else:
                raise Exception(f"Failed to find and navigate to plan: {CONFIG['plan_name']}")

            # Dynamic structural extraction of relative index mapping positions
            try:
                all_plans = page.locator("plan-container")
                initial_plan_index = 0
                for i in range(all_plans.count()):
                    if all_plans.nth(i).locator(f"//div[contains(@class, 'planHeading') and contains(., '{CONFIG['plan_name']}')]").count() > 0:
                        initial_plan_index = i
                        break
                print(f"Dynamically captured target plan index position: {initial_plan_index}")
            except Exception as e:
                initial_plan_index = 1
                print(f"Warning: Could not dynamically extract index position, defaulting to 1. Error: {e}")

            cta_button = plan_card.locator("//a[@role='button' and contains(., 'Select plan')]")
            nav.stable_click(cta_button)
            print("Successfully clicked the plan CTA button!")
            
            # --- STEP 2.5: HANDLING MODAL SCREENS ---
            print("--- STEP 2.5: HANDLING MODAL SCREENS ---")
            try:
                page.locator("#addaline-newline-heading-link2").wait_for(state="visible", timeout=15000)
                nav.stable_click("#addaline-newline-heading-link2")
                print("Clicking New Customer CTA")
                
                # Dynamic detachment mapping logic handling overlays
                page.locator("//div[contains(text(), 'Determining')]").wait_for(state="detached", timeout=20000)
                page.locator("//div[contains(text(), 'Loading')]").wait_for(state="detached", timeout=20000)
            except Exception as e:
                print(f"Failed during modal selection: {str(e)}")

            # --- STEP 3: DYNAMIC SIM ASSIGNMENT ---
            print("--- STEP 3: DYNAMIC SIM ASSIGNMENT ---")
            page.locator("#next-step-button-1").wait_for(state="visible", timeout=30000)
            page.wait_for_timeout(2000)

            nav.stable_click("#next-step-button-1")
            page.locator("#esim-number-input").wait_for(state="attached", timeout=30000)
            page.wait_for_timeout(2000)

            try:
                nav.stable_click("#edit-rateplan-link")
                print("Clicked plan Edit link; container section expanded.")
                page.wait_for_timeout(1500)

                page.locator("#tab-0").wait_for(state="visible", timeout=10000)
                page.wait_for_timeout(1500)

                # --- CAROUSEL SCROLLING LOGIC ---
                print("Simulating carousel browsing...")
                dot_selectors = page.locator("#radioCard-carousel-1-pagination button")
                dots_count = dot_selectors.count()
                
                for idx in range(dots_count):
                    if idx > 0:
                        nav.stable_click(dot_selectors.nth(idx))
                        print(f"Scrolled to carousel slide {idx + 1}")
                        page.wait_for_timeout(1200)

                if dots_count > 0:
                    nav.stable_click(dot_selectors.nth(0))
                    page.wait_for_timeout(1000)
                # --------------------------------

                radio_xpath = "//input[@type='radio' and @name='rate-plan']"
                page.locator(radio_xpath).first.wait_for(state="attached", timeout=10000)
                plan_radios = page.locator(radio_xpath)

                alt_index_pos = 0 if initial_plan_index != 0 else 1
                nav.stable_click(plan_radios.nth(alt_index_pos))
                print("Temporarily switched plan selection to an alternative option.")
                page.wait_for_timeout(2000)

                nav.stable_click(plan_radios.nth(int(initial_plan_index)))
                print("Restored original selection back.")
                page.wait_for_timeout(2000)

                nav.stable_click("#next-step-button-1")
                print("Clicked 'Next step' confirmation button pipeline layout node.")
                
            except Exception as e:
                print(f"Warning: Failed path execution variations adjusting plan configurations: {e}")

            page.locator("#esim-number-input").wait_for(state="attached", timeout=30000)
            page.wait_for_timeout(2000)

            try:
                print("Waiting for activation options loading overlay to disappear...")
                page.locator("//*[@aria-busy='true' and @role='alert']").wait_for(state="hidden", timeout=20000)
                print("Loader has disappeared. Proceeding to IMEI steps.")
            except Exception as e:
                print(f"Warning: Loader didn't clear or wasn't found, attempting to proceed: {e}")
            
            nav.stable_click("#order-selection-radio")
            page.locator("#esim-number-input").wait_for(state="hidden", timeout=30000)

            nav.stable_click("#add-to-cart-button-1")

            # --- STEP 4: CART REVIEW & CHECKOUT START ---
            print("--- STEP 4: CART REVIEW & CHECKOUT START ---")
            try:
                page.locator("#brfLoadingIndicator").wait_for(state="detached", timeout=20000)
                page.locator("//*[contains(@class, 'vrui-animate-icons-flipper')] | //*[contains(text(), 'Loading shopping cart.')]").wait_for(state="detached", timeout=20000)
                page.wait_for_timeout(2000)

                # Smooth scroll execution mimicking native viewport layouts
                page.evaluate("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
                page.wait_for_timeout(3500)
                
                nav.stable_click("#proceed-to-checkout-button", timeout=20000)
                print("Successfully proceeded to checkout.")
            except Exception as e:
                print(f"Checkout transition failed: {e}")
                
            try:
                print("--- STARTING INTEGRATED CHECKOUT FLOW ---")
                checkout = MobileCheckout(page, CONFIG)
                checkout.esim_checkout_flow()
                print("--- CHECKOUT FLOW COMPLETED SUCCESSFULLY ---")
            except Exception as e:
                print(f"❌ Error in CheckoutFlow: {e}")

        except Exception as e:
            print(f"❌ Error: {e}")

        finally:
            # Native context termination extracts and stops video recordings gracefully
            raw_video_path = page.video.path() if page.video else None
            context.close()
            browser.close()
            
            # Post-execution formatting renaming system-assigned UUID video file targets
            if raw_video_path and os.path.exists(raw_video_path):
                final_destination = os.path.join(CONFIG["video_dir"], CONFIG["final_video_name"])
                os.rename(raw_video_path, final_destination)
                print(f"🎥 Video verification trace finalized: {final_destination}")

if __name__ == "__main__":
    run()