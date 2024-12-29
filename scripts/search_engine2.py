from pymongo import MongoClient
from rapidfuzz import fuzz, process

client = MongoClient("mmbu")
db = client["NomNom"]  
collection = db["Foods"] 

def get_food_recommendations(search_term):
    all_food_items = list(collection.find({}, {"_id": 0, "Food Item": 1}))
    food_item_list = [item["Food Item"] for item in all_food_items if "Food Item" in item]
    matches = process.extract(search_term, food_item_list, limit=5, scorer=fuzz.WRatio)

    if matches:
        print(f"Top recommendations for '{search_term}':")
        for match_tuple in matches:
            match = match_tuple[0] 
            score = match_tuple[1] 

            food_details = collection.find_one({"Food Item": match}, {"_id": 0})
            print(
                f"- Food Item: {food_details.get('Food Item', 'N/A')}\n"
                f"  Category: {food_details.get('Category', 'N/A')}\n"
                f"  Calories: {food_details.get('Calories', 'N/A')} kcal\n"
                f"  Quantity: {food_details.get('Quantity', 'N/A')}\n"
            )
    else:
        print(f"No recommendations found for '{search_term}'.")

if __name__ == "__main__":
    search_term = input("Enter a food name or part of a name: ")
    get_food_recommendations(search_term)
