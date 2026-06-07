from checkout_flow import CheckoutFlow

class DesktopCheckout(CheckoutFlow):
    pass

class MobileCheckout(CheckoutFlow):
    pass

# Refactored profile metrics schemas configured cleanly for Playwright contexts
DEVICE_PROFILES = {
    "iphone_15_pro_max": {
        "viewport": {"width": 393, "height": 852},
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "is_mobile": True,
        "has_touch": True
    },
    "galaxy_s24_fe": {
        "viewport": {"width": 360, "height": 780},
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S721B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
        "is_mobile": True,
        "has_touch": True
    },
    "tablet_mobile_ui": {
        "viewport": {"width": 820, "height": 1180},
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "is_mobile": True,
        "has_touch": True
    },
    "tablet_desktop_ui": {
        "viewport": {"width": 1366, "height": 1024},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "is_mobile": False,
        "has_touch": True
    }
}