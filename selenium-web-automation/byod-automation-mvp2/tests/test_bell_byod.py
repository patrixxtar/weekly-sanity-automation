import pytest
from bell_config import CONFIG, SELECTORS
from landing_nav_framework import LandingNavigationFramework
from checkout_flow_framework import CheckoutFlowFramework

@pytest.mark.parametrize("sim_type", ["esim", "psim"])
@pytest.mark.parametrize("has_upc", [False, True])
def test_full_bell_checkout_flow(automation_env, sim_type, has_upc):
    utils = automation_env
    
    nav = LandingNavigationFramework(utils, CONFIG, SELECTORS)
    checkout = CheckoutFlowFramework(utils, CONFIG)
    
    nav.open_site()
    nav.bell_select_plan()
    nav.bell_handle_modals()
    nav.bell_configure_device(sim_type=sim_type, has_upc=has_upc)
    
    nav.enter_cart()
    nav.enter_checkout()
    
    if sim_type == "esim":
        checkout.esim_checkout_flow()
    else:
        checkout.psim_checkout_flow()
    
    assert "OrderReview" in utils.driver.current_url