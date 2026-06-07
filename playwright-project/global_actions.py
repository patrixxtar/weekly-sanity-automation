import time
from playwright.sync_api import Page, Locator

class GlobalNav:
    
    def __init__(self, page: Page):
        self.page = page

    def stable_click(self, locator_or_selector, timeout=15000, scroll=True):
        """Clicks an element reliably, ensuring it's scrolled into view if needed."""
        # Check if we were passed a Playwright Locator object or a raw text/CSS selector string
        if isinstance(locator_or_selector, Locator):
            locator = locator_or_selector
        elif isinstance(locator_or_selector, tuple):
            # Fallback mapper converting old Selenium (By.ID, "xyz") or (By.XPATH, "xyz") patterns
            selector_type, search_str = locator_or_selector
            if selector_type == "id":
                locator = self.page.locator(f"#{search_str}")
            else:
                locator = self.page.locator(search_str)
        else:
            locator = self.page.locator(locator_or_selector)

        if scroll:
            locator.scroll_into_view_if_needed(timeout=timeout)
            
        # Playwright's click mechanism auto-waits for actionability and resolves overlays safely
        locator.click(timeout=timeout)

    def landing_popups(self):
        self.page.wait_for_timeout(2000)
        current_url = self.page.url.lower()
        is_bell = "bell.ca" in current_url
        is_virgin = "virginplus.ca" in current_url

        try:
            if is_bell:
                # 1. Handle potential Lightbox
                connector = self.page.locator("#connector")
                if connector.is_visible(timeout=3000):
                    lightbox_close = self.page.locator("#close-lightbox")
                    if lightbox_close.is_visible(timeout=2000):
                        lightbox_close.click()
                        print("Lightbox dismissed instantly.")

                # 2. Handle Cookie Banner
                cookie_btn = self.page.locator("#onetrust-accept-btn-handler")
                if cookie_btn.is_visible(timeout=2000):
                    cookie_btn.click()
                    print("Cookie banner dismissed.")
            
            elif is_virgin:
                lightbox = self.page.locator("#roaming-lightbox-fifa")
                if lightbox.is_visible(timeout=5000):
                    lightbox_close = self.page.locator("#close-lightbox, .closeBtn[title='Close']")
                    lightbox_close.first.click()
                    print("Virgin Plus Lightbox dismissed.")
                
                cookie_btn = self.page.locator("#onetrust-accept-btn-handler")
                if cookie_btn.is_visible(timeout=2000):
                    cookie_btn.click()
                    print("Virgin Plus Cookie banner dismissed.")
            else:
                print("Current page not supported")
        except Exception:
            print("No brand lightbox active or timeout exception reached, proceeding.")