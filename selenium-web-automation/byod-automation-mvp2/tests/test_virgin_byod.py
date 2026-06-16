import pytest
from virgin_config import CONFIG, SELECTORS
from landing_nav_framework import LandingNavigationFramework
from checkout_flow_framework import CheckoutFlowFramework

@pytest.mark.parametrize("sim_type", ["esim", "psim"])
def test_full_virgin_checkout_flow(automation_env, sim_type):
    utils = automation_env
    
    # Initialize frameworks with dynamic brand configs
    nav = LandingNavigationFramework(utils, CONFIG, SELECTORS)
    checkout = CheckoutFlowFramework(utils, CONFIG)
    
    # Execution Flow
    nav.open_site()
    nav.virgin_select_plan()
    nav.virgin_handle_modals()
    
    nav.virgin_configure_device(sim_type=sim_type)
    
    nav.enter_cart()
    nav.enter_checkout()
    
    # VIRGIN PSIM FLOW FOLLOWS ESIM CHECKOUT
    """ if sim_type == "esim": """
    checkout.esim_checkout_flow()
    """ else: """
    """ checkout.psim_checkout_flow() """
    
    assert "OrderReview" in utils.driver.current_url