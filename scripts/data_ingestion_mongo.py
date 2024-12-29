import pymongo
import pandas as pd


df1 = pd.read_csv("dataset/food_1.csv")
df2 = pd.read_csv("dataset/food_2.csv")
df3 = pd.read_csv("dataset/food_3.csv")
df4 = pd.read_csv("dataset/food_4.csv")
df5 = pd.read_csv("dataset/food_5.csv")

final_df = pd.concat([df1,df2,df3,df4,df5])
final_df = final_df.drop_duplicates()

final_df['Food Item'] = final_df['Food Item'].str.replace('1pcs ', '')
final_df['Quantity'] = 1
df = final_df.copy()

mongo_uri = "mmbu"
database_name = "NomNom" 
collection_name = "Foods" 

client = pymongo.MongoClient(mongo_uri)

db = client[database_name]
collection = db[collection_name]
data_to_insert = df.to_dict(orient='records')

collection.insert_many(data_to_insert)

print(f"{len(data_to_insert)} records uploaded to MongoDB Cluster0.")
