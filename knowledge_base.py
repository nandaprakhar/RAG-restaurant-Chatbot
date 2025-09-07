"""
knowledge_base.py
-----------------
This script consolidates individual restaurant dish CSVs into a structured knowledge base JSON file.

Main Workflow:
- Reads the master Swiggy restaurant metadata CSV
- Cleans and parses individual dish data CSVs for each restaurant
- Builds a unified structured format containing restaurant and menu details

Output:
- `new_combined_knowledge_base.json` — contains a list of all restaurants with complete metadata and menu


"""

import pandas as pd
import numpy as np
import json
import os

# 🔁 Set the folder path containing all per-restaurant dish CSVs
csv_folder_path = "E:/Dekstop/GenAIProject/Scraping/CSV_data_new"
restaurant_csv_file = pd.read_csv("swiggy_restaurants_kanpur.csv")

# Final structured KB to be exported
knowledge_base = []


# -------------------------------------------------
# 🔧 Helper: Parse raw restaurant CSV (master file)
# -------------------------------------------------
def restaurant_data(df):
    df[['Ratings', 'Delivery_Time', 'Location']] = 'N/A'

    for idx, rating_string in enumerate(df['rating']):
        parts = rating_string.split('•')
        df.at[idx, 'Ratings'] = parts[0].strip()
        df.at[idx, 'Delivery_Time'] = parts[1].strip() if len(parts) > 1 else 'N/A'

    for idx, link in enumerate(df['link']):
        raw_slug = link.replace('https://www.swiggy.com/city/kanpur/', '')
        cleaned = raw_slug.replace(df.at[idx, 'name'].replace(' ', '-').lower() + '-', '')
        df.at[idx, 'Location'] = cleaned

    # Standardize location name
    df['cleaned_location'] = (
        df['Location']
        .str.replace(r'rest.*', '', regex=True)
        .str.rstrip('-')
        .str.replace('-', ' ')
    )
    return df


# -------------------------------------------------
# 🔧 Helper: Parse dish CSV and normalize fields
# -------------------------------------------------
def Data_Cleaning(csv_file):
    restaurant_location = csv_file["Restaurant_Location"][0]
    csv_file[['Raw_Info', 'Info', 'Cusine_Name', 'Price', 'Rating', 'Total_Reviews',
              'Description', 'Cuisine_type', 'Tags']] = 'N/A'

    for idx, entry in enumerate(csv_file['Complete Info']):
        lines = entry.split('\n')

        # Handle different layouts
        csv_file.at[idx, 'Raw_Info'] = lines
        csv_file.at[idx, 'Info'] = lines[0] if len(lines) > 0 else ''
        csv_file.at[idx, 'Cusine_Name'] = lines[1] if len(lines) > 1 else ''
        csv_file.at[idx, 'Price'] = lines[2] if len(lines) > 2 else ''
        
        if len(lines) >= 5 and len(lines[3]) <= 3 and lines[3] != 'ADD':
            csv_file.at[idx, 'Rating'] = lines[3]
            csv_file.at[idx, 'Total_Reviews'] = lines[4]

    # Extract description (if found)
    csv_file['AfterDescription'] = csv_file['Info'].str.extract(
        r'(?i)Description:\s+(.*?)\s+Swipe', expand=False)
    csv_file['AfterDescription'].fillna('N/A', inplace=True)

    # Extract cuisine type from Info
    csv_file['Cuisine_type'] = csv_file['Info'].apply(lambda x: x.split('.')[0])

    # Extract tags like Bestseller, Must Try
    def tag_extractor(info):
        tags = []
        if "Bestseller" in info:
            tags.append("Bestseller")
        if "Must Try" in info:
            tags.append("Must Try")
        return tags if tags else None

    csv_file['Tags'] = csv_file['Complete Info'].apply(tag_extractor)

    return csv_file, restaurant_location


# -------------------------------------------------
# 🚀 MAIN LOGIC: Iterate and consolidate all CSVs
# -------------------------------------------------

# Prepare metadata reference from main Swiggy metadata CSV
restaurant_info_file = restaurant_data(restaurant_csv_file)

# 🔁 Process each restaurant's dish CSV
for file in os.listdir(csv_folder_path):
    if file.endswith(".csv"):
        file_path = os.path.join(csv_folder_path, file)
        restaurant_name = file.replace("_dishes.csv", "").replace(".csv", "").replace("_", " ").title()

        print(f"\n📌 Processing: {restaurant_name}")

        # Match this restaurant in the master metadata CSV
        restaurant_info = restaurant_info_file[
            restaurant_info_file['name'].str.lower() == restaurant_name.lower()
        ]

        restaurant_menus = []
        restaurant_location = None

        try:
            dish_df = pd.read_csv(file_path)
            cleaned_df, restaurant_location = Data_Cleaning(dish_df)

            # Normalize columns
            cleaned_df.columns = [col.strip().lower().replace(" ", "_") for col in cleaned_df.columns]

            # 🧱 Convert each dish row to structured dict
            for _, row in cleaned_df.iterrows():
                menu_item = {
                    "dish_name": row.get("cuisine_name", ""),
                    "description": row.get("afterdescription", ""),
                    "price": row.get("price", ""),
                    "rating": row.get("rating", ""),
                    "num_reviews": row.get("total_reviews", ""),
                    "dish_type": row.get("cuisine_type", ""),
                    "tags": row.get("tags", ""),
                    "dish_tags": row.get("dish_tags", "")
                }
                restaurant_menus.append(menu_item)

        except Exception as e:
            print(f"⚠️ Error reading {file}: {e}")

        # ✅ Build restaurant-level entry
        for _, row in restaurant_info.iterrows():
            entry = {
                "restaurant_name": row.get("name", ""),
                "available_cuisine": row.get("cuisine", ""),
                "delivery_time": row.get("Delivery_Time", ""),
                "restaurant_rating": row.get("Ratings", ""),
                "city": row.get("city", ""),
                "restaurant_location": restaurant_location,
                "restaurant_menu": restaurant_menus
            }
            knowledge_base.append(entry)

        print(f"✅ {restaurant_name}: {len(restaurant_menus)} dishes processed")

# -------------------------------------------------
# 💾 Export Knowledge Base as JSON
# -------------------------------------------------
output_path = os.path.join(csv_folder_path, "new_combined_knowledge_base.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(knowledge_base, f, indent=4, ensure_ascii=False)

print(f"\n🎉 Saved final Knowledge Base to: {output_path}")
