from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import imageio
import os
from PIL import Image
import uuid

# Configuration
BASE_URL = "https://www.govmap.gov.il/"
OUTPUT_DIR = "screenshots"
GIF_OUTPUT = "historical_map.gif"
LOCATION = "ירושלים, ישראל"  # User-specified location (e.g., Jerusalem, Israel)
YEARS = list(range(2005, 2026))  # Years from 2005 to 2025 (adjust based on availability)
SPECIFIC_YEARS = None  # Set to list of years (e.g., [2005, 2010, 2015]) or None for all
FORWARD = True  # True for forward, False for backward
DELAY = 3  # Seconds to wait for map rendering

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in headless mode for efficiency
options.add_argument("--window-size=1920,1080")  # Set window size for consistent screenshots
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Navigate to GovMap
    driver.get(BASE_URL)
    time.sleep(5)  # Wait for page to load

    # Search for location
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchInput"))
        )
        search_box.send_keys(LOCATION)
        search_box.send_keys(Keys.RETURN)
        time.sleep(DELAY)  # Wait for map to center
    except Exception as e:
        print(f"Error finding search box: {e}")
        raise

    # Switch to aerial imagery (assuming a button or dropdown exists)
    try:
        # Note: The exact selector depends on GovMap's UI. This is a placeholder.
        background_dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'תצלום אוויר')]"))
        )
        background_dropdown.click()
        time.sleep(2)
    except Exception as e:
        print(f"Error switching to aerial imagery: {e}")
        raise

    # Collect screenshots for each year
    screenshots = []
    years_to_process = SPECIFIC_YEARS if SPECIFIC_YEARS else YEARS
    if not FORWARD:
        years_to_process = years_to_process[::-1]

    for year in years_to_process:
        try:
            # Select year (assuming a year selector dropdown or slider)
            year_selector = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{year}')]"))
            )
            year_selector.click()
            time.sleep(DELAY)  # Wait for map to update

            # Capture screenshot
            screenshot_path = os.path.join(OUTPUT_DIR, f"map_{year}.png")
            driver.save_screenshot(screenshot_path)
            screenshots.append(screenshot_path)
            print(f"Captured screenshot for year {year}")
        except Exception as e:
            print(f"Error processing year {year}: {e}")
            continue

    # Generate GIF
    images = []
    for screenshot in screenshots:
        img = Image.open(screenshot)
        images.append(img)
    
    # Save GIF
    imageio.mimsave(GIF_OUTPUT, images, duration=1.0)  # 1 second per frame
    print(f"GIF saved as {GIF_OUTPUT}")

finally:
    # Clean up
    driver.quit()
    # Optionally, remove screenshot files
    for screenshot in screenshots:
        try:
            os.remove(screenshot)
        except:
            pass
