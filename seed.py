"""
seed.py - Swiggy database mein asli jaisa data bharne wali script 🌱

Kya karti hai:
  1. Naye tables banati hai: restaurants, menu_items, orders, order_items
  2. customers table mein 'phone' column jodti hai
  3. 20 naye customers, 12 restaurants, ~55 menu items aur 60 orders daalti hai

Chalane ka tarika (fast API folder mein, venv on karke):
    python seed.py

Dobara chalane pe data double nahi hoga (pehle check karti hai).
"""

import os
import random
from datetime import datetime, timedelta

import psycopg
from dotenv import load_dotenv

load_dotenv()

random.seed(42)  # har baar same "random" data bane


def get_conn():
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname="swiggy",
        user="atharva",
        password=os.getenv("password"),
    )


# ---------------------------------------------------------------------------
# 1. Tables
# ---------------------------------------------------------------------------
CREATE_TABLES = """
ALTER TABLE customers ADD COLUMN IF NOT EXISTS phone TEXT;

CREATE TABLE IF NOT EXISTS restaurants (
    id        SERIAL PRIMARY KEY,
    naam      TEXT NOT NULL,
    city      TEXT NOT NULL,
    cuisine   TEXT,
    rating    NUMERIC(2, 1)
);

CREATE TABLE IF NOT EXISTS menu_items (
    id             SERIAL PRIMARY KEY,
    restaurant_id  INTEGER NOT NULL REFERENCES restaurants(id) ON DELETE CASCADE,
    naam           TEXT NOT NULL,
    price          INTEGER NOT NULL,
    is_veg         BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS orders (
    id             SERIAL PRIMARY KEY,
    customer_id    INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    restaurant_id  INTEGER NOT NULL REFERENCES restaurants(id),
    status         TEXT NOT NULL,
    total_amount   INTEGER NOT NULL,
    order_time     TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id            SERIAL PRIMARY KEY,
    order_id      INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id  INTEGER NOT NULL REFERENCES menu_items(id),
    quantity      INTEGER NOT NULL
);
"""

# ---------------------------------------------------------------------------
# 2. Data
# ---------------------------------------------------------------------------
CUSTOMERS = [
    ("Rohan Kulkarni", "Pune", "9822001101"),
    ("Sneha Joshi", "Pune", "9822001102"),
    ("Aditya Deshpande", "Pune", "9822001103"),
    ("Pooja Patil", "Pune", "9822001104"),
    ("Kunal Mehta", "Mumbai", "9820001105"),
    ("Ananya Iyer", "Mumbai", "9820001106"),
    ("Siddharth Shah", "Mumbai", "9820001107"),
    ("Neha Gupta", "Mumbai", "9820001108"),
    ("Vikram Singh", "Delhi", "9811001109"),
    ("Ritika Malhotra", "Delhi", "9811001110"),
    ("Arjun Chopra", "Delhi", "9811001111"),
    ("Simran Kaur", "Delhi", "9811001112"),
    ("Karthik Reddy", "Bangalore", "9845001113"),
    ("Divya Nair", "Bangalore", "9845001114"),
    ("Rahul Rao", "Bangalore", "9845001115"),
    ("Meera Krishnan", "Bangalore", "9845001116"),
    ("Yash Bhosale", "Pune", "9822001117"),
    ("Tanvi Shinde", "Mumbai", "9820001118"),
    ("Harsh Agarwal", "Delhi", "9811001119"),
    ("Kavya Hegde", "Bangalore", "9845001120"),
]

# naam, city, cuisine, rating, [(dish, price, is_veg), ...]
RESTAURANTS = [
    ("Vaishali", "Pune", "South Indian", 4.5, [
        ("Masala Dosa", 120, True), ("Idli Sambar", 80, True),
        ("SPDP", 90, True), ("Filter Coffee", 50, True)]),
    ("Shabree", "Pune", "Maharashtrian Thali", 4.3, [
        ("Puranpoli Thali", 320, True), ("Misal Pav", 110, True),
        ("Sabudana Khichdi", 90, True), ("Solkadhi", 60, True)]),
    ("SP's Biryani House", "Pune", "Biryani", 4.4, [
        ("Chicken Biryani", 280, False), ("Mutton Biryani", 360, False),
        ("Veg Biryani", 220, True), ("Raita", 40, True), ("Gulab Jamun", 60, True)]),
    ("Kyani & Co.", "Mumbai", "Irani Cafe", 4.2, [
        ("Bun Maska", 60, True), ("Irani Chai", 40, True),
        ("Keema Pav", 180, False), ("Berry Pulao", 300, False)]),
    ("Swati Snacks", "Mumbai", "Gujarati Snacks", 4.6, [
        ("Panki", 160, True), ("Pav Bhaji", 190, True),
        ("Sev Puri", 140, True), ("Dahi Batata Puri", 150, True)]),
    ("Bademiya", "Mumbai", "Mughlai", 4.1, [
        ("Seekh Kebab Roll", 220, False), ("Chicken Tikka", 260, False),
        ("Paneer Tikka Roll", 200, True), ("Baida Roti", 180, False)]),
    ("Karim's", "Delhi", "Mughlai", 4.5, [
        ("Mutton Korma", 380, False), ("Butter Chicken", 340, False),
        ("Khamiri Roti", 30, True), ("Dal Makhani", 240, True)]),
    ("Sita Ram Diwan Chand", "Delhi", "North Indian", 4.4, [
        ("Chole Bhature", 150, True), ("Lassi", 80, True),
        ("Aloo Paratha", 120, True)]),
    ("Haldiram's", "Delhi", "Sweets & Snacks", 4.2, [
        ("Raj Kachori", 140, True), ("Rasmalai", 120, True),
        ("Chole Kulche", 160, True), ("Masala Chai", 50, True)]),
    ("MTR", "Bangalore", "South Indian", 4.6, [
        ("Rava Idli", 90, True), ("Bisi Bele Bath", 130, True),
        ("Masala Dosa", 110, True), ("Badam Halwa", 120, True)]),
    ("Meghana Foods", "Bangalore", "Andhra Biryani", 4.5, [
        ("Boneless Chicken Biryani", 320, False), ("Paneer Biryani", 260, True),
        ("Chicken 65", 240, False), ("Andhra Meals", 220, True)]),
    ("Truffles", "Bangalore", "Burgers & Cafe", 4.4, [
        ("All American Cheese Burger", 260, False), ("Veg Burger", 190, True),
        ("Peri Peri Fries", 150, True), ("Cold Coffee", 140, True)]),
]

STATUSES = ["delivered"] * 8 + ["cancelled", "on_the_way"]
NUM_ORDERS = 60


def main():
    conn = get_conn()
    cur = conn.cursor()

    # 1. Tables bana do
    cur.execute(CREATE_TABLES)

    # 2. Pehle se data hai? Toh dobara mat daalo
    cur.execute("SELECT COUNT(*) FROM restaurants")
    if cur.fetchone()[0] > 0:
        print("⚠️  Data pehle se hai, kuch nahi kiya. (Dobara bharna ho toh pehle tables khaali karo)")
        conn.commit()
        conn.close()
        return

    # 3. Customers
    customer_ids_by_city = {}
    for naam, city, phone in CUSTOMERS:
        cur.execute(
            "INSERT INTO customers (naam, city, phone) VALUES (%s, %s, %s) RETURNING id",
            (naam, city, phone),
        )
        customer_ids_by_city.setdefault(city, []).append(cur.fetchone()[0])

    # 4. Restaurants + menu
    restaurants_by_city = {}   # city -> [(restaurant_id, [(menu_item_id, price), ...])]
    menu_count = 0
    for naam, city, cuisine, rating, menu in RESTAURANTS:
        cur.execute(
            "INSERT INTO restaurants (naam, city, cuisine, rating) VALUES (%s, %s, %s, %s) RETURNING id",
            (naam, city, cuisine, rating),
        )
        restaurant_id = cur.fetchone()[0]
        items = []
        for dish, price, is_veg in menu:
            cur.execute(
                "INSERT INTO menu_items (restaurant_id, naam, price, is_veg) VALUES (%s, %s, %s, %s) RETURNING id",
                (restaurant_id, dish, price, is_veg),
            )
            items.append((cur.fetchone()[0], price))
            menu_count += 1
        restaurants_by_city.setdefault(city, []).append((restaurant_id, items))

    # 5. Orders (customer apni hi city ke restaurant se order karta hai)
    now = datetime.now()
    for _ in range(NUM_ORDERS):
        city = random.choice(list(customer_ids_by_city))
        customer_id = random.choice(customer_ids_by_city[city])
        restaurant_id, items = random.choice(restaurants_by_city[city])

        chosen = random.sample(items, k=random.randint(1, min(3, len(items))))
        lines = [(item_id, price, random.randint(1, 3)) for item_id, price in chosen]
        total = sum(price * qty for _, price, qty in lines)

        order_time = now - timedelta(
            days=random.randint(0, 59), hours=random.randint(8, 22), minutes=random.randint(0, 59)
        )
        cur.execute(
            """INSERT INTO orders (customer_id, restaurant_id, status, total_amount, order_time)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            (customer_id, restaurant_id, random.choice(STATUSES), total, order_time),
        )
        order_id = cur.fetchone()[0]

        for item_id, _, qty in lines:
            cur.execute(
                "INSERT INTO order_items (order_id, menu_item_id, quantity) VALUES (%s, %s, %s)",
                (order_id, item_id, qty),
            )

    conn.commit()
    conn.close()

    print("✅ Data bhar gaya!")
    print(f"   👤 Customers jode:   {len(CUSTOMERS)}")
    print(f"   🍽️  Restaurants:      {len(RESTAURANTS)}")
    print(f"   📋 Menu items:       {menu_count}")
    print(f"   🛵 Orders:           {NUM_ORDERS}")


if __name__ == "__main__":
    main()