"""
crawler.py
-----------
Scrapes restaurant metadata (name, cuisine, rating, URL) from Swiggy's restaurant listing pages.

Target Output:
- A CSV file (e.g., `swiggy_restaurants_kanpur.csv`) containing metadata for all restaurants in specified cities.

Dependencies:
- Selenium (browser automation)
- BeautifulSoup (HTML parsing)
- ChromeDriverManager (auto installs ChromeDriver)


"""

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
)

# -----------------------------------------
# 🧠 Configuration
# -----------------------------------------
city_slugs = ['kanpur']  # Add more cities if needed
OUTPUT_CSV = "swiggy_restaurants_kanpur.csv"


# -----------------------------------------
# 🚀 Setup: ChromeDriver with Headless Mode
# -----------------------------------------
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


# -----------------------------------------
# 🔄 Auto-scroll and click "Show More"
# -----------------------------------------
def click_show_more(driver, max_clicks=10):
    clicks_done = 0
    while clicks_done < max_clicks:
        try:
            show_more = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[@data-testid='restaurant_list_show_more']//div[contains(text(),'Show more')]"
                ))
            )
            try:
                show_more.click()
            except ElementClickInterceptedException:
                print("⚠️ Click intercepted — using JavaScript click.")
                driver.execute_script("arguments[0].click();", show_more)

            # Wait for more restaurants to load
            prev_count = len(driver.find_elements(By.XPATH, "//div[@data-testid='restaurant_list_card']"))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, "//div[@data-testid='restaurant_list_card']")) > prev_count
            )

            clicks_done += 1
            new_count = len(driver.find_elements(By.XPATH, "//div[@data-testid='restaurant_list_card']"))
            print(f"✅ Clicked 'Show More' ({clicks_done}/{max_clicks}) - {new_count} restaurants now loaded")

        except (TimeoutException, NoSuchElementException):
            print(f"⛔ 'Show More' not clickable or missing. Ending at {clicks_done} clicks.")
            break


# -----------------------------------------
# 🍽️ Scrape Restaurant Info
# -----------------------------------------
def scrape_restaurants(driver, city):
    time.sleep(2)  # Allow final content load
    restaurant_elements = driver.find_elements(By.XPATH, "//div[@data-testid='restaurant_list_card']")
    results = []

    for res in restaurant_elements:
        try:
            name = res.find_element(By.XPATH, ".//div[contains(@class,'eLaouz')]").text
            cuisine = res.find_element(By.XPATH, ".//div[contains(@class,'bfOHNR')]").text
            link = res.find_element(By.CLASS_NAME, 'kcEtBq').get_attribute("href")
            rating = res.find_element(By.XPATH, ".//div[contains(@class,'hhnNfO')]").text

            results.append({
                "name": name,
                "cuisine": cuisine,
                "rating": rating,
                "link": link,
                "city": city
            })
        except Exception as e:
            print("⚠️ Error extracting a restaurant:", e)
    return results


# -----------------------------------------
# 🏁 Main Controller
# -----------------------------------------
def scrape_multiple_cities_to_csv(city_slugs, output_file=OUTPUT_CSV):
    all_data = []

    for city in city_slugs:
        print(f"\n🌆 Scraping city: {city}")
        url = f"https://www.swiggy.com/city/{city}/order-online"
        driver = get_driver()
        driver.get(url)
        time.sleep(3)

        click_show_more(driver, max_clicks=10)
        city_data = scrape_restaurants(driver, city)
        all_data.extend(city_data)

        driver.quit()
        print(f"✅ Done scraping {len(city_data)} restaurants in {city}.")

    # Save to CSV
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    print(f"\n📦 All data saved to: `{output_file}`")


# -----------------------------------------
# 📍 Entry Point
# -----------------------------------------
if __name__ == "__main__":
    scrape_multiple_cities_to_csv(city_slugs)
