import time
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================
#  USER SETTINGS – change these as you like (in seconds)
# ============================================================
ON_TIME = 120 * 60   # time the AC stays ON   (120 minutes here)
OFF_TIME = 30 * 60   # time the AC stays OFF  (30 minutes)

# ============================================================
#  CONFIGURATION (should work for all users)
# ============================================================
AC_PAGE = "https://w5.ab.ust.hk/njggt/app/"
SWITCH_XPATH = "//button[contains(@class, 'ant-switch')]"
WAIT_TIMEOUT = 20   # a bit longer to be safe
MAX_RETRIES = 3     # how many times to try if the switch disappears

# Dedicated profile folder (inside the user’s home directory)
PROFILE_DIR = os.path.join(os.path.expanduser("~"), "ChromeProfile_AC")

# ============================================================
#  SETUP THE BROWSER
# ============================================================
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={PROFILE_DIR}")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
driver.get(AC_PAGE)

input("Log in (if needed) and make sure the AC switch is visible, then press 'Enter' to start...")

wait = WebDriverWait(driver, WAIT_TIMEOUT)

def get_switch():
    """Return a fresh, clickable switch element. Raises TimeoutException if not found."""
    return wait.until(EC.element_to_be_clickable((By.XPATH, SWITCH_XPATH)))

# Check that the switch is present on the page
try:
    get_switch()
    print("Found AC switch.\n")
except TimeoutException:
    print("Could not find the AC switch. Are you logged in and on the right page?")
    driver.quit()
    exit()

# ============================================================
#  HELPER FUNCTIONS
# ============================================================
def is_ac_on():
    """Return True if AC is ON (aria-checked='true')."""
    switch = get_switch()
    return switch.get_attribute("aria-checked") == "true"

def accept_alert():
    """Accept any open alert. Returns True if an alert was handled."""
    try:
        WebDriverWait(driver, 2).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"Alert says: {alert.text}")
        alert.accept()
        print("Alert accepted.")
        return True
    except (NoAlertPresentException, TimeoutException):
        return False

def safe_ensure_state(turn_on: bool):
    """
    Toggle the AC to the desired state, retrying if the switch disappears.
    Returns True on success, False if it couldn't toggle after MAX_RETRIES.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            currently_on = is_ac_on()
            if currently_on == turn_on:
                print(f"Already {'ON' if turn_on else 'OFF'} (attempt {attempt})")
                return True

            print(f"Attempt {attempt}: Clicking to turn {'ON' if turn_on else 'OFF'}...")
            switch = get_switch()
            switch.click()

            # Wait a tiny bit, then accept the confirmation alert
            time.sleep(0.5)
            accept_alert()

            # Wait for UI to stabilise (you can adjust this if your connection is slow)
            time.sleep(5)

            # Verify the new state
            new_state = is_ac_on()
            print(f"State now: {'ON' if new_state else 'OFF'}\n")
            if new_state == turn_on:
                return True
            else:
                print("State didn't change, retrying...\n")

        except TimeoutException:
            print(f"Switch not found (page may be reloading). Taking a screenshot (debug_timeout.png)...")
            driver.save_screenshot("debug_timeout.png")
            print("Screenshot saved. Waiting a bit, then retrying.\n")
            time.sleep(5)

    print(f"Failed to change AC state after {MAX_RETRIES} attempts.")
    return False

# ============================================================
#  MAIN LOOP – with timestamps and cycle counter
# ============================================================
cycle = 1

try:
    while True:
        # --- TURN ON ---
        print(f"\n========== Cycle {cycle} : Turning ON ==========")
        safe_ensure_state(True)
        now_on = datetime.now()
        print(f"AC turned ON at: {now_on.strftime('%H:%M:%S')}")
        time.sleep(ON_TIME)

        # --- TURN OFF ---
        print(f"\n========== Cycle {cycle} : Turning OFF ==========")
        safe_ensure_state(False)
        now_off = datetime.now()
        print(f"AC turned OFF at: {now_off.strftime('%H:%M:%S')}")
        time.sleep(OFF_TIME)

        cycle += 1

except KeyboardInterrupt:
    print("\nScheduler stopped by user.")
    driver.quit()