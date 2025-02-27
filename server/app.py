#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api
from models import db, Restaurant, RestaurantPizza, Pizza
import os

# Database Setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

# Home Route
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Route: Get All Restaurants (EXCLUDES `restaurant_pizzas`)
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    rest = [{"address": restaurant.address, "id": restaurant.id, "name": restaurant.name} for restaurant in Restaurant.query.all()]
    return make_response(rest, 200)

# Route: Get or Delete Restaurant by ID
@app.route('/restaurants/<int:id>', methods=["GET", "DELETE"])
def restaurant_by_id(id):
    rest = Restaurant.query.filter(Restaurant.id == id).first()

    if not rest:
        return make_response({"error": "Restaurant not found"}, 404)

    if request.method == "GET":
        return make_response(rest.to_dict(include_relationships=True), 200)

    elif request.method == "DELETE":
        db.session.delete(rest)
        db.session.commit()
        return make_response({}, 204)

# Route: Get All Pizzas
@app.route('/pizzas', methods=['GET'])
def pizzas():
    pizza_list = [{"id": pizza.id, "ingredients": pizza.ingredients, "name": pizza.name} for pizza in Pizza.query.all()]
    return make_response(pizza_list, 200)

# Route: Create a RestaurantPizza
@app.route('/restaurant_pizzas', methods=["POST"])
def restaurant_pizzas():
    data = request.get_json()
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    try:
        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()
        return make_response(restaurant_pizza.to_dict(), 201)
    except Exception:
        return make_response({"errors": ["validation errors"]}, 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
