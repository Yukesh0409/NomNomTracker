from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify,Response
from rapidfuzz import process, fuzz
import datetime
import json
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from scripts import groq_call
import os
import csv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

app = Flask(__name__)
app.secret_key = "I_am_Batman"

client = MongoClient(MONGO_URI)
db = client["NomNom"]
users_collection = db["Users"]
food_collection = db["Foods"]
logs_collection = db["Logs"]

@app.route("/view_logs", methods=["GET", "POST"])
def view_logs():
    if "username" not in session:
        return redirect(url_for("login"))

    user_logs = list(logs_collection.find({"username": session["username"]}, {"_id": 0}))

    grouped_logs = {}
    for log in user_logs:
        date = log["time_logged"].date()
        if date not in grouped_logs:
            grouped_logs[date] = {"food_items": [], "total_calories": 0}
        
        grouped_logs[date]["food_items"].append({"food_item": log["food_item"], "calories": log["calories"]})
        grouped_logs[date]["total_calories"] += log["calories"]

    sorted_dates = sorted(grouped_logs.keys(), reverse=True)
    filter_date_from = request.form.get("filter_date_from")
    filter_date_to = request.form.get("filter_date_to")
    
    if filter_date_from and filter_date_to:
        filter_date_from = datetime.datetime.strptime(filter_date_from, "%Y-%m-%d").date()
        filter_date_to = datetime.datetime.strptime(filter_date_to, "%Y-%m-%d").date()
        
        sorted_dates = [
            date for date in sorted_dates
            if filter_date_from <= date <= filter_date_to
        ]

    return render_template("view_logs.html", grouped_logs={date: grouped_logs[date] for date in sorted_dates})

@app.route("/export_logs", methods=["POST"])
def export_logs():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_logs = logs_collection.find({"username": username})
    def generate_csv():
        yield "Date,Food Item,Quantity,Calories\n" 
        for log in user_logs:
            date = log["time_logged"].strftime("%Y-%m-%d %H:%M:%S")
            food_item = log["food_item"]
            quantity = log.get("quantity", 0)
            calories = log.get("calories", 0)
            yield f"{date},{food_item},{quantity},{calories}\n"
    return Response(
        generate_csv(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=logs.csv"},
    )

@app.route("/food_selection", methods=["GET", "POST"])
def food_selection():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        selected_food = request.form["food"]
        quantity = request.form["quantity"]
        custom_food = request.form.get("custom_food")
        food_details = food_collection.find_one({"Food Item": selected_food}, {"_id": 0, "Calories": 1})
        if custom_food:
            calorie_info = groq_call.get_calorie_info(custom_food)
            selected_food = custom_food
            quantity = calorie_info['quantity']
            print(calorie_info['calorie'])
        calories = calorie_info['calorie']
        log_entry = {
            "username": session["username"],
            "food_item": selected_food,
            "quantity": int(quantity),
            "calories": calories,
            "time_logged": datetime.datetime.now()
        }
        logs_collection.insert_one(log_entry)

        print(f"Logged: {log_entry}")
        return jsonify({"message": "Food selection submitted!"})

    all_food_items = list(food_collection.find({}, {"_id": 0, "Food Item": 1}))
    food_item_list = [item["Food Item"] for item in all_food_items if "Food Item" in item]
    return render_template("food_selection.html", food_items=food_item_list)


@app.route("/search_food", methods=["POST"])
def search_food():
    search_term = request.json.get("search_term", "")
    all_food_items = list(food_collection.find({}, {"_id": 0, "Food Item": 1}))
    food_item_list = [item["Food Item"] for item in all_food_items if "Food Item" in item]

    matches = process.extract(search_term, food_item_list, limit=5, scorer=fuzz.WRatio)
    recommendations = [{"food": match[0], "score": match[1]} for match in matches]
    return jsonify(recommendations)

@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("food_selection"))
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # username = request.form.get("username")
        # password = request.form.get("password")
        # re_password = request.form.get("re_password")

        # if not username or not password or not re_password:
        #     flash("All fields are required.", "error")
        #     return redirect(url_for("signup"))

        # if password != re_password:
        #     flash("Passwords do not match.", "error")
        #     return redirect(url_for("signup"))

        # if users_collection.find_one({"username": username}):
        #     flash("Username already exists. Please choose another.", "error")
        #     return redirect(url_for("signup"))

        # hashed_password = generate_password_hash(password)
        # users_collection.insert_one({"username": username, "password": hashed_password})

        # flash("Account created successfully. Please log in.", "success")
        # return redirect(url_for("login"))
        flash("Account creation is temporarily stopped", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            session["username"] = username
            flash("Logged in successfully.", "success")
            return redirect(url_for("profile"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/profile")
def profile():
    if "username" not in session:
        flash("You must log in first.", "error")
        return redirect(url_for("login"))
    return render_template("profile.html", username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
