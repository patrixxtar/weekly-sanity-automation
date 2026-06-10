import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys # REQUIRED

# Add this to your imports at the top of the file
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

from global_actions import GlobalNav

class CheckoutFlow:
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(self.driver, 15)
        self.nav = GlobalNav(driver)

        
    def esim_checkout_flow(self):
        self.fill_personal_info()
        self.setup_number()
        self.process_credit_check()
        self.review_page()

    def psim_checkout_flow(self):
        self.fill_personal_info()
        self.setup_number()
        self.shipping()
        self.process_credit_check()
        self.review_page()



    def fill_personal_info(self):
        # --- CHECKOUT STEP 1: PERSONAL INFORMATION ---
        print("--- CHECKOUT STEP 1: PERSONAL INFORMATION ---")

        self._user_info()
        self._address()
        self._continue_click()
        
    def _user_info(self):
        def fill_field(field_id, value):
            element = self.wait.until(EC.visibility_of_element_located((By.ID, field_id)))
            element.clear()
            element.send_keys(value)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur'));", element)
            time.sleep(0.5)

        fill_field("PersonalInformation_CustomerInformationViewModel_FirstName", self.config["first_name"])
        fill_field("PersonalInformation_CustomerInformationViewModel_LastName", self.config["last_name"])
        fill_field("PersonalInformation_CustomerInformationViewModel_EmailAddress", self.config["email"])
        fill_field("PersonalInformation_CustomerInformationViewModel_ConfirmEmailAddress", self.config["email"])
        fill_field("PersonalInformation_BillingInformationViewModel_PhoneNumber", self.config["phone"])

    def _address(self):
        # --- ADDRESS HANDLING ---
        print("Entering address...")
        address_input = self.driver.find_element(By.ID, "PersonalInformation_BillingInformationViewModel_StreetAddress")
        address_input.clear()
        address_input.send_keys(self.config["address"])
        

        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".pca.pcalist .pcaitem")))# Send ENTER to trigger the address selection/validation
        time.sleep(1) # Brief pause before pressing Enter
        address_input.send_keys(Keys.ENTER)
        print("Address entered and ENTER key sent.")
        time.sleep(2)

    def _continue_click(self):
        # --- SCROLL AND CLICK CONTINUE ---
        print("Scrolling to and clicking 'Continue to Number setup'...")
        try:
            self.nav.stable_click((By.ID, "id_SHIPPINGBILLING_CUSTOMERINFO_NEXT_LABEL"))
            print("Successfully clicked 'Continue to Number setup'.")
        except Exception as e:
            print(f"Could not click 'Continue to Number setup': {e}")

        # --- STEP 6.5: HANDLING CONFIRMATION MODAL ---
        print("Checking for confirmation modal...")
        try:
            # Wait for the modal title to be visible to ensure the modal is active
            modal_title_xpath = "//*[@id='modal-confirm-information-title'] | //h2[contains(text(), 'Confirm information')]"
            self.wait.until(
                EC.visibility_of_element_located((By.XPATH, modal_title_xpath))
            )

            confirm_btn_xpath = (
                "//button[@data-dtname='Confirm information button on Checkout Personal Info step'] | "
                "//button[@id='confirm-billing-info-button']"
            )
            
            # Locate the 'Confirm' button using the data-dtname attribute
            self.nav.stable_click((By.XPATH, confirm_btn_xpath))
            print("Confirmed information modal.")
            
            # Wait for the modal to disappear
            self.wait.until(
                EC.invisibility_of_element_located((By.XPATH, modal_title_xpath))
            )
            
        except Exception as e:
            print("No confirmation modal appeared, or it was handled already.")

    def setup_number(self):
        # --- CHECKOUT STEP 2: NUMBER SETUP ---
        print("--- CHECKOUT STEP 2: NUMBER SETUP ---")

        # 1. Select 'Select a new number'
        new_number_label = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Select a new number')]"))
        )
        self.nav.stable_click(new_number_label)
        print("Clicked label: 'Select a new number'")
        
        # Wait for the phone number list to appear and become clickable
        # Using a slightly longer timeout for the AJAX load
        print("Waiting for numbers to populate...")
        time.sleep(2) 

        # 2. Select the first available phone number by clicking its label
        # The label associated with "current-option2-0"
        phone_label = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//label[@for='current-option2-0'] | //label[@for='phoneNumber-1']"))
        )
        self.nav.stable_click(phone_label)
        print("Selected the first available phone number.")


        current_url = self.driver.current_url.lower()
        if "virgin" in current_url or "virginplus" in current_url:
            print("Detected Virgin Plus environment.")
            try:
                # Giving a brief pause for the DOM/animation to settle before looking for the 2nd CTA
                time.sleep(1.5)
                first_continue = self.wait.until(EC.element_to_be_clickable((By.ID, "new-number-continue-button")))
                print("Assigning Virgin Continue ID")
            except Exception as e:
                print(f"Failed to assign {e}")
        elif "bell" in current_url:
            print("Detected Bell environment.")
            try:
                time.sleep(1.5)
                first_continue = self.wait.until(EC.element_to_be_clickable((By.XPATH, 
                "//*[@id='ContinueToPaymentInfo'] | //*[@id='linkToContinue']")))
                print("Assigning Bell Continue ID")
            except Exception as e:
                print(f"Failed to assign {e}")

        # 3. Continue button
        self.nav.stable_click(first_continue)
        continue_btn = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, 
                "//*[@id='ContinueToPaymentInfo'] | //*[@id='linkToContinue']"
            ))
        )
        self.nav.stable_click(continue_btn)
        print("Clicked 'Continue' to move to Payment.")


    def shipping(self):
        print("--- CHECKOUT STEP: SHIPPING ---")
        self.wait.until((EC.presence_of_element_located((By.ID, "standardShipping-shipping-container"))))
        
        # 1. Search for any button that has 'Continue' in the data-dtname attribute
        # We use contains() to be safer against slight naming changes
        # 2. Wait for the button to appear in the DOM
        try:
            btn = self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@data-dtname, 'Continue button')]")))
            
            # 3. If found, scroll it into view and click
            self.nav.stable_click(btn)        
            print("Successfully found and clicked the Continue button.")
            
        except Exception as e:
            print(f"❌ Shipping failure: {e}")


    def process_credit_check(self):
        # --- CHECKOUT STEP 3: CREDIT CHECK & ID IDENTIFICATION ---
        print("--- CHECKOUT STEP 3: CREDIT CHECK & ID IDENTIFICATION ---")
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='paymentInfo'] | //*[@id='paymentDetails']"))
        )
        time.sleep(3)

        window_width = self.driver.execute_script("return window.innerWidth;")

        if type(self).__name__ == "MobileCheckout" and window_width < 768:
            print("Mobile context detected: Attempting summary and accordion steps.")
            # Check if the mobile summary accordion flow exists

            current_url = self.driver.current_url.lower()
            self.nav.stable_click((By.CSS_SELECTOR, 'a[data-target="#summary-view-details"], button#view-details-button'))

            if "bell" in current_url:
                try:
                    self.nav.stable_click((By.ID, "price-summary-accordion-button-1"))
                    self.nav.stable_click((By.ID, "purchase-accordion-button-2"))
                    print("Successfully navigated mobile summary accordions.")
                    
                    # Check for the optional mobile 'Why Purchase Online' popup inside the flow
                    try:
                        self.nav.stable_click((By.ID, "whyPurchaseOnlineBtnMobile"))
                        print("Clicked mobile 'Why Purchase Online'.")
                    except Exception:
                        print("Mobile 'Why Purchase Online' button not found. Skipping popup.")
                except Exception as e:
                    print(f"Mobile accordions not found or failed to click: {e}. Skipping section.")
            
            self.nav.stable_click((By.CSS_SELECTOR, '#closeBtn-why-purchase-online-mobile, button#modal-title1-close-button'))

        else:
            print("Desktop context detected: Attempting 'Why Purchase Online' check.")
            # Check if desktop 'Why Purchase Online' exists before clicking
            try:
                self.nav.stable_click((By.ID, "whyPurchaseOnlineBtn"))
                self.nav.stable_click((By.ID, "closeBtn-why-purchase-online"))
                print("Clicked desktop 'Why Purchase Online' and closed it.")
            except Exception:
                print("Desktop 'Why Purchase Online' button not found/not visible. Skipping.")
        
        
        self.nav.stable_click((By.ID, "cardNumberWhyModalTrigger"))
        self.nav.stable_click((By.XPATH, "//*[@id='whyCreditCardClose'] | //button[contains(@id, '-close-button')]"))
        self.nav.stable_click((By.XPATH, '//*[@aria-label="tooltip security code info"] | //a[@id="securityCodeModalTrigger"] | //a[contains(@aria-label, "What is a card security code?")]'))
        self.nav.stable_click((By.XPATH, "//*[@id='security-code-closeCTA'] | //*[@id='security-code-modal-close-button']"))
        

        # 1. Input Card Number (Matching your ID: CreditCard_CardNumber)
        card_input = self.wait.until(EC.element_to_be_clickable((By.ID, "CreditCard_CardNumber")))
        card_input.clear()
        card_input.send_keys(self.config["card_number"])
        time.sleep(2)

        # --- MONTH DROPDOWN ---
        month_element = self.driver.find_element(By.ID, "CreditCard_ExpirationDataMM")
        if month_element.tag_name == "select":
            month_select = Select(month_element)
            month_select.select_by_index(len(month_select.options) - 1)
        else:
            # Action 1: Physically move to and click the Month Dropdown to open it
            actions = ActionChains(self.driver)
            actions.move_to_element(month_element).click().perform()
            time.sleep(1) # Wait for animation expansion
            
            # Action 2: Locate December item and physically click it with the mouse cursor
            target_month = self.wait.until(
                EC.presence_of_element_located((By.ID, "CreditCard_ExpirationDataMM-12"))
            )

            try:
                actions.reset_actions()
                actions.move_to_element(target_month).click().perform()
                print("Month selected via ActionChains manual mouse emulation.")
            except Exception as e:
                print(f"ActionChains failed/timed out ({type(e).__name__}). Applying tablet JS fallback...")
                self.driver.execute_script("""
                arguments[0].scrollIntoView({block: 'center'});
                arguments[0].click();
                """, target_month)
                print("Month selected via JS fallback execution.")


        time.sleep(1.5) # Clean transition gap before processing next menu

        # --- YEAR DROPDOWN ---
        year_element = self.driver.find_element(By.ID, "CreditCard_ExpirationDateYY")
        if year_element.tag_name == "select":
            year_select = Select(year_element)
            year_select.select_by_index(len(year_select.options) - 1)
        else:
            # Action 1: Physically move to and click the Year Dropdown to open it
            actions = ActionChains(self.driver)
            actions.move_to_element(year_element).click().perform()
            time.sleep(1)
            
            # Action 2: Locate 2035 item and physically click it with the mouse cursor
            target_year = self.wait.until(
                EC.visibility_of_element_located((By.ID, "CreditCard_ExpirationDateYY-2035"))
            )
            actions.reset_actions()
            actions.move_to_element(target_year).click().perform()
            print("Year selected via ActionChains manual mouse emulation.")
                
        time.sleep(2)

        # 3. Security Code (Matching your ID: CreditCard_SecurityCode)
        self.driver.find_element(By.ID, "CreditCard_SecurityCode").send_keys(self.config["cvv"])
        
        # 4. DOB (Matching your ID: PersonalInformation_CreditInformationViewModel_DateOfBirth)
        self.driver.find_element(By.XPATH, "//*[@id='PersonalInformation_CreditInformationViewModel_DateOfBirth'] | //input[@placeholder='MM/DD/YYYY']").send_keys(self.config["birthday"])
        time.sleep(3)

        # 5. Handle 'Continue' clicks
        self.nav.stable_click((By.ID, "idhdnSHIPPINGBILLING_CUSTOMERINFO_NEXT_LABEL"))

        print("--- CHECKOUT STEP 3: VALIDATING CREDIT CHECK ---")
        
        # 2. WAIT FOR THE ERROR BANNER
        # We target the class 'form-validation-errors' which appears in your HTML
        try:
            error_banner = self.wait.until(
                EC.any_of(
                    EC.visibility_of_element_located((By.XPATH, "//div[@role='alert'][contains(., 'The card you are trying to use is not supported')]")),
                    EC.visibility_of_element_located((By.XPATH, "//div[@role='alert'][contains(., 'There is an issue with the credit card information provided')]")),
                    EC.visibility_of_element_located((By.CLASS_NAME, "form-validation-errors")),
                    EC.visibility_of_element_located((By.CLASS_NAME, "vrui-bg-pink"))
                )
            )
            print("✅ Success: Validation error detected as expected.")
            
            # Optional: Print the errors found to the console for verification
            errors = error_banner.find_elements(By.TAG_NAME, "li")
            for err in errors:
                print(f"Found error: {err.text}")
                
        except Exception as e:
            print(f"⚠️ Warning: Credit check did not trigger the expected error banner: {e}")


    def review_page(self):
    # --- CHECKOUT STEP 4: FINAL ORDER SUMMARY REVIEW ---
        print("--- CHECKOUT STEP 4: FINAL ORDER SUMMARY REVIEW ---")

        current_url = self.driver.current_url.lower()
        if "bell" in current_url:
             self.driver.get("https://bell.ca/Order/Index#/OrderReview")

        elif "virgin" in current_url:
            self.driver.get("https://myaccount.virginplus.ca/Eshop/Checkout#/OrderReview")
        
        else:
            print("Review page doesn't exist for this webpage")
            return
           
        self.wait.until(
            EC.url_contains("OrderReview")
        )

        # Wait for the page to load
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(10) # Give the final review elements a moment to populate

        submit_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='LinkToPlaceOrder'] | //*[@id='place-order-button']")))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", submit_btn)
        time.sleep(4) # Allow scroll animation to finish

        self.nav.stable_click(submit_btn)
        print("✅ Order submitted successfully!")

        print("Finalizing recording... pausing for 5 seconds.")
        time.sleep(5)


    def virgin_new_device(self):
        """
        Executes intermediate checkout steps: Device selection, SweetPay selection,
        modal handling, downpayment slider adjustments, and item addition to cart.
        """
        driver = self.driver
        nav = self.nav
        actions = ActionChains(driver)
        device_target = self.config['device_name']

        # --- STEP 2: DYNAMIC DEVICE SELECTION ---
        print(f"--- STEP 2: FINDING AND SELECTING PLAN '{device_target}'")

        device_model_xpath = f"//div[contains(@class, 'item phone') and .//span[@class='phoneDescription' and text()='{device_target}']]"

        try:
            device_card = self.wait.until(
                EC.presence_of_element_located((By.XPATH, device_model_xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", device_card)
            print("Scrolled vertically to the device tile.")
            time.sleep(1.5) 

            nav.stable_click(device_card)
            print("Successfully clicked the device!")

        except Exception as e:
            print("Warning: Could not do scroll to device. Proceeding anyway...")

        self.wait.until(EC.visibility_of_element_located((By.ID, "phoneInfo")))
        time.sleep(2)

        sweetpay_lite_card = self.wait.until(EC.visibility_of_element_located((By.ID, "FO9")))
        nav.stable_click(sweetpay_lite_card)
        self.wait.until(EC.text_to_be_present_in_element_attribute((By.ID, "FO9"), "class", "selected"))
        time.sleep(1.5)

        sweetpay_regular_card = self.wait.until(EC.visibility_of_element_located((By.ID, "FO7")))
        nav.stable_click(sweetpay_regular_card)
        self.wait.until(EC.text_to_be_present_in_element_attribute((By.ID, "FO7"), "class", "selected"))
        time.sleep(1.5)

        continue_cta = self.wait.until(EC.visibility_of_element_located((By.ID, "accss-step1-btn")))
        nav.stable_click(continue_cta)
        time.sleep(1.5)
        
        # --- STEP 2.5: HANDLING MODAL SCREENS ---
        print("--- STEP 2.5: HANDLING MODAL SCREENS ---")
        try:
            get_started_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "addaline-newline-heading-link1"))
            )

            nav.stable_click((By.ID, "addaline-newline-heading-link1"))
            print("Clicking New Customer CTA")
            
            try:
                self.wait.until(
                    EC.invisibility_of_element_located((By.XPATH, "//div[contains(text(), 'Determining')]"))
                )
                self.wait.until(
                    EC.invisibility_of_element_located((By.XPATH, "//div[contains(text(), 'Loading')]"))
                )
            except Exception as e:
                print(f"Warning: Loading screen did not disappear: {str(e)}")
        except Exception as e:
            print(f"Failed during modal selection: {str(e)}")

        # --- STEP 3: INTERACTING WITH THE SLIDER ---
        print("--- STEP 3: INITIALIZING SLIDER MANIPULATION ---")
        try:
            slider_pointer = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.rz-pointer-min"))
            )
            print("Slider handle successfully located.")

            target_downpayment = 240

            # --- PRIMARY STRATEGY: JavaScript Injection ---
            try:
                print("Attempting to set slider via AngularJS Scope Injection...")
                js_script = f"""
                    var element = document.querySelector('.rzslider');
                    var scope = angular.element(element).scope();
                    scope.$apply(function() {{
                        scope.term.sliderValue = {target_downpayment};
                    }});
                """
                driver.execute_script(js_script)
                print(f"Primary strategy successful: Slider set directly to ${target_downpayment}!")
                time.sleep(2)

            # --- FALLBACK STRATEGY: ActionChains Drag and Drop ---
            except Exception as js_error:
                print(f"JavaScript injection failed ({str(js_error)}). Launching ActionChains fallback...")
                
                slider_pointer = self.wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "span.rz-pointer-min"))
                )
                
                actions.click_and_hold(slider_pointer).move_by_offset(150, 0).release().perform()
                print("Fallback strategy completed: Slider dragged via ActionChains simulation.")
                time.sleep(2)

        except Exception as e:
            print(f"❌ Error during Slider processing: {str(e)}")
        
        nav.stable_click((By.XPATH, "//a[contains(@class, 'nextStep') and @data-ng-click='showstep(3)']"))
        time.sleep(1.5)
        print("Continue to rate plan step...")

        nav.stable_click((By.XPATH, "//fieldset//plan-container[1]"))
        time.sleep(1.5)
        print("Plan selected...")

        nav.stable_click((By.XPATH, "//a[contains(@class, 'nextStep') and contains(., 'Continue to Step 4')]"))
        time.sleep(1.5)
        print("Continue to Smartcare step...")

        nav.stable_click((By.XPATH, "//div[contains(@class, 'smartcareBox')][1]"))
        time.sleep(1.5)
        print("Smartcare selected...")

        nav.stable_click((By.XPATH, "//a[@data-ng-click='addtobasket()']"))
        time.sleep(1.5)
        print("Adding to cart...")

        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'postpaid-order-init.do') and contains(text(), 'Checkout')]"))
        )
        time.sleep(2)

        monthly_charges_section = driver.find_element(
            By.XPATH, "//div[contains(@class, 'box')][.//h2[text()='Monthly charges']]"
        )

        actions.move_to_element(monthly_charges_section).perform()

        checkout_btn = driver.find_element(By.XPATH, "//a[@href='../activation/postpaid-order-init.do']")
        actions.move_to_element(checkout_btn).perform()

        nav.stable_click((By.XPATH, "//a[text()='Checkout']"))
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "innerVerificationcontainer")))

        time.sleep(2)


