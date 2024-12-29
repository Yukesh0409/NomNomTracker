from pymongo import MongoClient

client = MongoClient("mmbu") 
db = client["NomNom"]
collection = db["Foods"]  

def get_food_recommendations(search_term):
    query = {"Food Item": {"$regex": search_term, "$options": "i"}}
    results = collection.find(query, {"_id": 0, "Food Item": 1, "Category": 1, "Calories": 1, "Quantity": 1})

    recommendations = list(results)

    if recommendations:
        print(f"Recommendations for '{search_term}':")
        for rec in recommendations:
            print(
                f"- Food Item: {rec.get('Food Item', 'N/A')}\n"
                f"  Category: {rec.get('Category', 'N/A')}\n"
                f"  Calories: {rec.get('Calories', 'N/A')} kcal\n"
                f"  Quantity: {rec.get('Quantity', 'N/A')}\n"
            )
    else:
        print(f"No recommendations found for '{search_term}'.")

if __name__ == "__main__":
    search_term = input("Enter a food name or part of a name: ")
    get_food_recommendations(search_term)
