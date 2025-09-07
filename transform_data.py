import json

def transform_knowledge_base(input_path, output_path):
    """
    Transforms the knowledge base from the original format to an optimized
    format for a vector database.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file {input_path} is not a valid JSON file.")
        return

    optimized_corpus = []

    for restaurant in knowledge_base:
        restaurant_name = restaurant.get("restaurant_name", "N/A")
        city = restaurant.get("city", "N/A")
        cuisine = restaurant.get("available_cuisine", "N/A")
        restaurant_rating = restaurant.get("restaurant_rating", "N/A")

        if "restaurant_menu" in restaurant and restaurant["restaurant_menu"] is not None:
            for dish in restaurant["restaurant_menu"]:
                dish_name = dish.get("dish_name", "N/A")
                description = dish.get("description", "")
                if description is None:
                    description = ""
                price = dish.get("price", "N/A")
                rating = dish.get("rating", "N/A")
                dish_type = dish.get("dish_type", "N/A")

                text_chunk = (
                    f"{dish_name} is a dish served at {restaurant_name}, which is a {cuisine} restaurant in {city}. "
                    f"It is described as: {description}. The price of the dish is {price} and it has a rating of {rating}. "
                    f"The restaurant has an overall rating of {restaurant_rating}."
                )

                metadata = {
                    "restaurant_name": restaurant_name,
                    "city": city,
                    "cuisine": cuisine,
                    "dish_name": dish_name,
                    "price": price,
                    "rating": rating,
                    "dish_type": dish_type,
                }

                optimized_corpus.append({
                    "text_chunk": text_chunk,
                    "metadata": metadata
                })

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(optimized_corpus, f, indent=4)
        print(f"Successfully transformed data and saved to {output_path}")
    except IOError:
        print(f"Error: Could not write to the file {output_path}.")

if __name__ == "__main__":
    transform_knowledge_base('Structured_data/knowledge_base.json', 'Structured_data/optimized_corpus.json')