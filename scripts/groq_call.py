from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import json
import os

load_dotenv()

def get_calorie_info(food_item):

    chat = ChatGroq(
        model="llama-3.1-70b-versatile",
        temperature=0,
        max_retries=5,
    )

    prompt_template ="""
        You are a helpful assistant that provides nutritional information. Given a food item, respond with a JSON string containing the following keys:
        - "calorie" (integer value in kcal)
        - "quantity" (integer value representing the quantity, assume 1 if unspecified).

        Food item: {food_item}
        """
    formatted_prompt = ChatPromptTemplate.from_template(prompt_template)
    response = chat.predict(formatted_prompt.format(food_item=food_item))
    result = response.strip()
    start_idx = result.find("{")
    end_idx = result.rfind("}") + 1
    if start_idx != -1 and end_idx != -1:
        result = result[start_idx:end_idx]
    else:
        result = "{}"

    result = json.loads(result)
    print(result)
    print("Food Item:" ,food_item)
    print("Calorie: ",result['calorie'])
    return result
