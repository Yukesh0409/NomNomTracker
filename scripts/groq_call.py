from langchain_groq import ChatGroq
from langchain.llms import HuggingFaceHub
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import json
import os

load_dotenv()

HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY")

def get_calorie_info(food_item):
    chat = HuggingFaceHub(
        repo_id="mistralai/Mistral-Nemo-Instruct-2407",
        model_kwargs={"temperature": 0.7, "max_length": 512},
        huggingfacehub_api_token=HUGGING_FACE_API_KEY
    )

    prompt_template = """
        You are a helpful assistant that provides nutritional information. Your given foods are mainly south indian. Given a food item, respond with a JSON string containing the following keys:
        - "calorie" (integer value in kcal)
        - "quantity" (integer value representing the quantity, assume 1 if unspecified).

        Food item: {food_item}
    """
    formatted_prompt = ChatPromptTemplate.from_template(prompt_template)
    
    try:
        # Use `predict` method to get response
        response = chat.predict(formatted_prompt.format(food_item=food_item))

        # Parse response into JSON
        start_idx = response.find("{")
        end_idx = response.rfind("}") + 1
        if start_idx != -1 and end_idx != -1:
            result = response[start_idx:end_idx]
        else:
            result = "{}"
        
        result = json.loads(result)
        print(f"Response: {result}")
        return result

    except json.JSONDecodeError:
        print(f"Failed to parse response: {response}")
        return {"calorie": 0, "quantity": 1}  # Default values in case of error

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"calorie": 0, "quantity": 1}  # Default values in case of error
