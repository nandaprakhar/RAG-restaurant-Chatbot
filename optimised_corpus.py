"""
optimized_corpus.py
-------------------
This script transforms the structured knowledge base (`knowledge_base.json`) 
into a flat list of textual chunks + metadata optimized for retrieval 
(used in vector databases like FAISS).

Each document contains detailed dish information formatted as a paragraph,
and metadata contains structured fields used for filtering, faceting, and advanced retrieval.


"""

import json
import os

# -------------------------------
# Load Structured Knowledge Base
# -------------------------------
input_path = "knowledge_base.json"
with open(input_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

optimized_corpus = []  # final chunks (text for vector embeddings)
metadata_list = []     # structured metadata for each chunk


# -------------------------------
# Process Each Restaurant Entry
# -------------------------------
for entry in raw_data:
    restaurant = entry.get("restaurant_name", "Unknown")
    location = entry.get("restaurant_location", "Unknown")
    city = entry.get("city", "Unknown")
    rating = entry.get("restaurant_rating", "N/A")
    cuisine = entry.get("available_cuisine", "N/A")
    delivery = entry.get("delivery_time", "N/A")

    # 🧾 Iterate over dishes (menu)
    for dish in entry.get("restaurant_menu", []):
        name = dish.get("dish_name", "Unknown") or "Unknown"
        name = name.strip()

        # Handle missing or malformed descriptions
        description = dish.get("description", "") or "No description"
        description = description.strip()

        price = str(dish.get("price", "N/A"))

        # Normalize tags into comma-separated string
        tags = dish.get("tags", [])
        if tags is None:
            tags = []
        tags_str = ", ".join(tag.capitalize() for tag in tags if isinstance(tag, str))

        dish_type = dish.get("dish_type", "Unknown")
        dish_rating = dish.get("rating", "N/A")
        reviews = dish.get("num_reviews", "0")

        # ----------------------------
        # 🔹 Construct optimized text
        # ----------------------------
        text = (
            f"Dish: {name}\n"
            f"Description: {description}\n"
            f"Price: {price}\n"
            f"Type: {dish_type}, {tags_str}\n"
            f"Restaurant: {restaurant}\n"
            f"Location: {location}, {city}\n"
            f"Restaurant Rating: {rating} ({reviews} reviews)\n"
            f"Cuisine: {cuisine}\n"
            f"Delivery Time: {delivery}"
        )

        optimized_corpus.append(text)

        # ----------------------------
        # 🔸 Store metadata for filter
        # ----------------------------
        metadata_list.append({
            "restaurant_name": restaurant,
            "location": location,
            "city": city,
            "dish_name": name,
            "dish_type": dish_type,
            "tags": tags_str,
            "dish_rating": dish_rating,
            "restaurant_rating": rating,
            "price": price
        })


# -------------------------------
# Save Optimized Output
# -------------------------------
output_path = "optimized_corpus.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({
        "documents": optimized_corpus,
        "metadata": metadata_list
    }, f, indent=2)

print(f"✅ Optimized corpus saved to: {output_path}")
