"""
scraper.py
----------
Scrapes detailed dish-level information from individual Swiggy restaurant pages.
Outputs per-restaurant CSV files + a combined master CSV file.

"""

import time
import pandas as pd
import csv
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# -------------------------------
# Headless Chrome Driver Setup
# -------------------------------
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# -------------------------------
# Scrape All Dishes from a Page
# -------------------------------
def scrape_restaurants(driver):
    time.sleep(2)  # Allow page to load

    # Basic metadata
    restaurant_name = driver.find_element(By.XPATH, "//h1").text
    restaurant_location = driver.find_element(By.XPATH, "//div[contains(@class,'_2gTwA')]").text
    print(f"📍 {restaurant_name} - {restaurant_location}")

    # Find all sections (grouped by categories)
    titles = driver.find_elements(By.XPATH, "//div[starts-with(@id, 'cid-')]")
    dishes = []

    for title in titles:
        headers = title.find_elements(By.XPATH, ".//h3")

        # Get section titles like 'Veg Curry (5)'
        tag_count_list = []
        for h in headers:
            text = h.text
            match = re.search(r'\((\d+)\)', text)
            count = int(match.group(1)) if match else 1
            clean_tag = re.sub(r'\s*\(\d+\)', '', text).strip()
            tag_count_list.append((clean_tag, count))

        dish_items = title.find_elements(By.XPATH, ".//div[@data-testid='normal-dish-item']")
        idx = 0

        for tag, count in tag_count_list:
            print(f"🍽️ Category: {tag}")
            for _ in range(count):
                if idx >= len(dish_items):
                    break
                dish = dish_items[idx]
                idx += 1

                # Extract dish details
                try:
                    name = dish.find_element(By.XPATH, ".//div[contains(@class,'dwSeRx')]").text
                except:
                    name = 'N/A'

                try:
                    info = dish.find_element(By.XPATH, ".//p[contains(@class,'_1QbUq')]").text
                except:
                    info = 'N/A'

                try:
                    rating = dish.find_element(By.XPATH, ".//div[contains(@class,'sc-gEvEer')]").text
                except:
                    rating = 'N/A'

                complete_info = dish.text

                dishes.append({
                    "cuisine_name": name,
                    "Complete Info": complete_info,
                    "Restaurant_Location": restaurant_location,
                    "dish_tags": tag
                })

    return dishes, restaurant_name


# -------------------------------
# Orchestrator Function
# -------------------------------
def scrape_multiple_cities_to_csv(output_file="complete_kanpur_restaurants_dishes.csv"):
    all_data = []
    restaurant_links = []

    # Load restaurant list from city crawler output
    with open("swiggy_restaurants_kanpur.csv", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            restaurant_links.append(row['link'])

    # Visit each restaurant
    for link in restaurant_links:
        print(f"\n🔗 Scraping from: {link}...")
        driver = get_driver()
        driver.get(link)
        time.sleep(3)

        try:
            dishes_data, restaurant_name = scrape_restaurants(driver)
            all_data.extend(dishes_data)

            # Save per-restaurant CSV
            df = pd.DataFrame(dishes_data)
            output_path = f"{restaurant_name}_dishes.csv"
            df.to_csv(output_path, index=False)
            print(f"✅ Saved: {output_path}")

        except Exception as e:
            print(f"❌ Error scraping {link}: {e}")

        finally:
            driver.quit()

    # Save final combined output
    df_all = pd.DataFrame(all_data)
    df_all.to_csv(output_file, index=False)
    print(f"\n📦 All data saved to: {output_file}")


# -------------------------------
# Entry Point
# -------------------------------
if __name__ == "__main__":
    scrape_multiple_cities_to_csv()
