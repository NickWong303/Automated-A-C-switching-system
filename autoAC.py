import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#Set the off time and on time you like (the unit here is second)
ON_TIME = 30 * 60    # 30 minutes
OFF_TIME = 30 * 60   # 30 minutes



# ---------- CONFIG ----------
AC_PAGE = "https://w5.ab.ust.hk/njggt/app/"
SWITCH_XPATH = "//button[contains(@class, 'ant-switch')]"
WAIT_TIMEOUT = 15


PROFILE_DIR = os.path.join(os.path.expanduser("~"), "ChromeProfile_AC")

# ---------- SETUP DRIVER ----------
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={PROFILE_DIR}")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.get(AC_PAGE)

input("Log in (if needed) and navigate to the AC control page, then press Enter here...")

wait = WebDriverWait(driver, WAIT_TIMEOUT)

def get_switch():
    """Return a fresh, clickable switch element. Raises TimeoutException if not found."""
    return wait.until(EC.element_to_be_clickable((By.XPATH, SWITCH_XPATH)))

# Make sure the switch is on the page before we start
try:
    get_switch()
    print("Found AC switch.")
except TimeoutException:
    print("Could not find the AC switch. Are you logged in and on the right page?")
    driver.quit()
    exit()

# ---------- HELPER FUNCTIONS ----------
def is_ac_on():
    """Return True if AC is currently ON (aria-checked='true')."""
    switch = get_switch()
    return switch.get_attribute("aria-checked") == "true"

def ensure_state(turn_on: bool):
    """Click the switch only if needed, handle confirmation alert."""
    currently_on = is_ac_on()
    if currently_on == turn_on:
        print(f"Already {'ON' if turn_on else 'OFF'}")
        return

    print(f"Clicking to turn {'ON' if turn_on else 'OFF'}...")
    switch = get_switch()
    switch.click()

    # Handle the pop‑up alert ("Do you want to Turn-on?")
    try:
        wait.until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"Alert says: {alert.text}")
        alert.accept()
        print("Alert accepted.")
    except NoAlertPresentException:
        pass   # no alert appeared – that's fine too

    # Wait for the UI to settle after the toggle + alert
    time.sleep(2)

    # After toggling, re‑read the state (fresh element)
    new_state = is_ac_on()
    print(f"State now: {'ON' if new_state else 'OFF'}")

# ---------- SCHEDULE ----------

try:
    while True:
        print("\n--- Cycle: Turning ON ---")
        ensure_state(True)
        time.sleep(ON_TIME)

        print("\n--- Cycle: Turning OFF ---")
        ensure_state(False)
        time.sleep(OFF_TIME)

except KeyboardInterrupt:
    print("\nStopped.")
    driver.quit()