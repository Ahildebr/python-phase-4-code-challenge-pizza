from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

# Restaurant Model
class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates="restaurant", cascade="all, delete")

    # Serialize Rules: By default, exclude relationships unless explicitly included
    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def to_dict(self, include_relationships=False):
        """Custom serialization to conditionally include relationships"""
        data = super().to_dict()
        if not include_relationships:
            data.pop("restaurant_pizzas", None)  # Exclude relationship by default
        return data

# Pizza Model
class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship("RestaurantPizza", back_populates="pizza")

    serialize_rules = ('-restaurant_pizzas.pizza',)

# RestaurantPizza Model (Join Table)
class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)

    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")

    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas',)

    @validates('price')
    def validate_price(self, key, price):
        """Ensure price is between 1 and 30."""
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30.")
        return price