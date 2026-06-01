import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException

from selenium.webdriver.common.keys import Keys

from global_actions import GlobalNav
from checkout_flow import CheckoutFlow


class DesktopCheckout(CheckoutFlow):
    # Desktop uses the same flow as Base, no changes needed!
    pass

class MobileCheckout(CheckoutFlow):
    # Mobile uses the same flow, but other params are configured on Base flow
    pass

DEVICE_PROFILES = {
    "iphone_15_pro_max": {
        "display_size": (393, 852),  # iOS CSS Viewport
        "mobile_emulation": {
            "deviceMetrics": {
                "width": 393,
                "height": 852,
                "pixelRatio": 3.0,
                "touch": True
            },
            "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
        }
    },
    "galaxy_s24_fe": {
        "display_size": (360, 780),  # Android CSS Viewport
        "mobile_emulation": {
            "deviceMetrics": {
                "width": 360,
                "height": 780,
                "pixelRatio": 3.0,
                "touch": True
            },
            "userAgent": "Mozilla/5.0 (Linux; Android 14; SM-S721B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36"
        }
    },
    "tablet_mobile_ui": {
        "display_size": (820, 1180),  # iPad Air Viewport
        "mobile_emulation": {
            "deviceMetrics": {
                "width": 820,
                "height": 1180,
                "pixelRatio": 2.0,
                "touch": True
            },
            # Explicit "iPad" Mobile User Agent (forces mobile/tablet breakpoints)
            "userAgent": "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
        }
    },
    "tablet_desktop_ui": {
        "display_size": (1366, 1024),  # iPad Pro 12.9" Viewport
        "mobile_emulation": {
            "deviceMetrics": {
                "width": 1366,
                "height": 1024,
                "pixelRatio": 2.0,
                "touch": True
            },
            # "Macintosh" Desktop User Agent (forces full desktop layout on a touch screen)
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
        }
    }
}