import os
from playwright.sync_api import Page, expect
from global_actions import GlobalNav

class CheckoutFlow:
    def __init__(self, page: Page, config: dict):
        self.page = page
        self.config = config
        self.nav = GlobalNav(page)
        
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
        print("--- CHECKOUT STEP 1: PERSONAL INFORMATION ---")
        self._user_info()
        self._address()
        self._continue_click()
        
    def _user_info(self):
        def fill_field(selector, value):
            locator = self.page.locator(f"#{selector}")
            locator.wait_for(state="visible", timeout=10000)
            locator.fill(value)
            # Emulates native blur event
            locator.evaluate("el => el.dispatchEvent(new Event('blur'))")

        fill_field("PersonalInformation_CustomerInformationViewModel_FirstName", self.config["first_name"])
        fill_field("PersonalInformation_CustomerInformationViewModel_LastName", self.config["last_name"])
        fill_field("PersonalInformation_CustomerInformationViewModel_EmailAddress", self.config["email"])
        fill_field("PersonalInformation_CustomerInformationViewModel_ConfirmEmailAddress", self.config["email"])
        fill_field("PersonalInformation_BillingInformationViewModel_PhoneNumber", self.config["phone"])

    def _address(self):
        print("Entering address...")
        address_input = self.page.locator("#PersonalInformation_BillingInformationViewModel_StreetAddress")
        address_input.fill(self.config["address"])
        
        # Address validation dropdown monitoring
        dropdown_item = self.page.locator(".pca.pcalist .pcaitem")
        dropdown_item.first.wait_for(state="visible", timeout=20000)
        self.page.wait_for_timeout(1000)
        
        address_input.press("Enter")
        print("Address entered and ENTER key sent.")
        self.page.wait_for_timeout(2000)

    def _continue_click(self):
        print("Scrolling to and clicking 'Continue to Number setup'...")
        try:
            self.nav.stable_click("#id_SHIPPINGBILLING_CUSTOMERINFO_NEXT_LABEL")
            print("Successfully clicked 'Continue to Number setup'.")
        except Exception as e:
            print(f"Could not click 'Continue to Number setup': {e}")

        print("Checking for confirmation modal...")
        try:
            modal_title = self.page.locator("#modal-confirm-information-title, h2:has-text('Confirm information')")
            modal_title.wait_for(state="visible", timeout=5000)

            confirm_btn = self.page.locator("button[data-dtname='Confirm information button on Checkout Personal Info step'], button#confirm-billing-info-button")
            self.nav.stable_click(confirm_btn)
            print("Confirmed information modal.")
            
            modal_title.wait_for(state="hidden", timeout=10000)
        except Exception:
            print("No confirmation modal appeared, or it was handled already.")

    def setup_number(self):
        print("--- CHECKOUT STEP 2: NUMBER SETUP ---")

        new_number_label = self.page.locator("//*[contains(text(), 'Select a new number')]")
        self.nav.stable_click(new_number_label)
        print("Clicked label: 'Select a new number'")
        
        print("Waiting for numbers to populate...")
        self.page.wait_for_timeout(2000) 

        phone_label = self.page.locator("label[for='current-option2-0'], label[for='phoneNumber-1']").first
        self.nav.stable_click(phone_label)
        print("Selected the first available phone number.")

        current_url = self.page.url.lower()
        if "virgin" in current_url or "virginplus" in current_url:
            print("Detected Virgin Plus environment. Waiting for the first 'Continue' button...")
            try:
                self.page.wait_for_timeout(1500)
                virgin_continue = self.page.locator("#new-number-continue-button")
                self.nav.stable_click(virgin_continue)
                print("Clicked first 'Continue' button for Virgin Plus.")
            except Exception as e:
                print(f"Failed to click Virgin's first continue button: {e}")

        continue_btn = self.page.locator("#ContinueToPaymentInfo, #linkToContinue")
        self.nav.stable_click(continue_btn)
        print("Clicked 'Continue' to move to Payment.")

    def shipping(self):
        print("--- CHECKOUT STEP: SHIPPING ---")
        shipping_btn = self.page.locator("button[data-dtname*='Continue button']")
        
        try:
            shipping_btn.wait_for(state="attached", timeout=20000)
            self.nav.stable_click(shipping_btn)        
            print("Successfully found and clicked the Continue button.")
        except Exception as e:
            all_buttons = self.page.locator("button")
            print(f"DEBUG: Found {all_buttons.count()} total buttons layout configurations.")
            print(f"❌ Critical failure: {e}")

    def process_credit_check(self):
        print("--- CHECKOUT STEP 3: CREDIT CHECK & ID IDENTIFICATION ---")
        self.page.locator("#paymentInfo, #paymentDetails").wait_for(state="attached", timeout=10000)
        self.page.wait_for_timeout(3000)

        # Get window viewport measurement dynamically
        viewport_width = self.page.viewport_size["width"] if self.page.viewport_size else 1024

        if type(self).__name__ == "MobileCheckout" and viewport_width < 768:
            print("Mobile context detected: Attempting summary and accordion steps.")
            self.nav.stable_click('a[data-target="#summary-view-details"], button#view-details-button')

            if "bell" in self.page.url.lower():
                try:
                    self.nav.stable_click("#price-summary-accordion-button-1")
                    self.nav.stable_click("#purchase-accordion-button-2")
                    print("Successfully navigated mobile summary accordions.")
                    
                    why_online_mobile = self.page.locator("#whyPurchaseOnlineBtnMobile")
                    if why_online_mobile.is_visible(timeout=2000):
                        why_online_mobile.click()
                        print("Clicked mobile 'Why Purchase Online'.")
                except Exception as e:
                    print(f"Mobile accordions not found or failed to click: {e}. Skipping section.")
            
            self.nav.stable_click('#closeBtn-why-purchase-online-mobile, button#modal-title1-close-button')
        else:
            print("Desktop context detected: Attempting 'Why Purchase Online' check.")
            try:
                self.nav.stable_click("#whyPurchaseOnlineBtn")
                self.nav.stable_click("#closeBtn-why-purchase-online")
                print("Clicked desktop 'Why Purchase Online' and closed it.")
            except Exception:
                print("Desktop 'Why Purchase Online' button not found/not visible. Skipping.")
        
        self.nav.stable_click("#cardNumberWhyModalTrigger")
        self.nav.stable_click("#whyCreditCardClose, button[id$='-close-button']")
        self.nav.stable_click('//*[@aria-label="tooltip security code info"] | //a[@id="securityCodeModalTrigger"] | //a[contains(@aria-label, "What is a card security code?")]')
        self.nav.stable_click("#security-code-closeCTA, #security-code-modal-close-button")
        
        card_input = self.page.locator("#CreditCard_CardNumber")
        card_input.fill(self.config["card_number"])
        self.page.wait_for_timeout(2000)

        # --- MONTH DROPDOWN ---
        month_element = self.page.locator("#CreditCard_ExpirationDataMM")
        if month_element.evaluate("el => el.tagName.toLowerCase()") == "select":
            # Select the final item directly
            options_count = month_element.locator("option").count()
            month_element.select_option(index=options_count - 1)
        else:
            month_element.click()
            self.page.wait_for_timeout(1000)
            target_month = self.page.locator("#CreditCard_ExpirationDataMM-12")
            try:
                target_month.click(timeout=5000)
                print("Month selected via native context locator click emulation.")
            except Exception:
                target_month.scroll_into_view_if_needed()
                target_month.evaluate("el => el.click()")
                print("Month selected via fallback JS click iteration.")

        self.page.wait_for_timeout(1500)

        # --- YEAR DROPDOWN ---
        year_element = self.page.locator("#CreditCard_ExpirationDateYY")
        if year_element.evaluate("el => el.tagName.toLowerCase()") == "select":
            options_count = year_element.locator("option").count()
            year_element.select_option(index=options_count - 1)
        else:
            year_element.click()
            self.page.wait_for_timeout(1000)
            target_year = self.page.locator("#CreditCard_ExpirationDateYY-2035")
            target_year.click()
            print("Year selected via native context locator click emulation.")
                
        self.page.wait_for_timeout(2000)

        self.page.locator("#CreditCard_SecurityCode").fill(self.config["cvv"])
        self.page.locator("#PersonalInformation_CreditInformationViewModel_DateOfBirth, input[placeholder='MM/DD/YYYY']").fill(self.config["birthday"])
        self.page.wait_for_timeout(3000)

        self.nav.stable_click("#idhdnSHIPPINGBILLING_CUSTOMERINFO_NEXT_LABEL")
        print("--- CHECKOUT STEP 3: VALIDATING CREDIT CHECK ---")
        
        try:
            error_banner = self.page.locator(
                "//div[@role='alert'][contains(., 'The card you are trying to use is not supported')] | "
                "//div[@role='alert'][contains(., 'There is an issue with the credit card information provided')] | "
                ".form-validation-errors | .vrui-bg-pink"
            ).first
            
            error_banner.wait_for(state="visible", timeout=30000)
            print("✅ Success: Validation error detected as expected.")
            
            errors = error_banner.locator("li")
            for i in range(errors.count()):
                print(f"Found error: {errors.nth(i).text_content()}")
        except Exception as e:
            print(f"⚠️ Warning: Credit check did not trigger the expected error banner: {e}")

    def review_page(self):
        print("--- CHECKOUT STEP 4: FINAL ORDER SUMMARY REVIEW ---")
        current_url = self.page.url.lower()
        
        if "bell" in current_url:
             self.page.goto("https://bell.ca/Order/Index#/OrderReview")
        elif "virgin" in current_url:
            self.page.goto("https://myaccount.virginplus.ca/Eshop/Checkout#/OrderReview")
        else:
            print("Review page doesn't exist for this webpage")
            return
           
        self.page.wait_for_url("**/OrderReview**", timeout=20000)
        self.page.wait_for_load_state("load")
        self.page.wait_for_timeout(10000)

        submit_btn = self.page.locator("#LinkToPlaceOrder, #place-order-button")
        submit_btn.scroll_into_view_if_needed()
        self.page.wait_for_timeout(4000)

        self.nav.stable_click(submit_btn)
        print("✅ Order submitted successfully!")
        self.page.wait_for_timeout(5000)