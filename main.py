import os

import groq
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from groq import Groq
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
load_dotenv()  # 📖 sabse pehle .env padho

app = FastAPI(title="Swiggy Customer API")
ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_conn():
    """🔌 Database connection (DRY: har endpoint yahi use karega)"""
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname="swiggy",
        user="atharva",
        password=os.getenv("password"),
    )


def ask_ai(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    """🤖 AI se poocho, timeout aur error handling ke saath"""
    try:
        response = ai_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            timeout=20,
        )
        return response.choices[0].message.content

    except groq.RateLimitError:
        raise HTTPException(status_code=429, detail="AI abhi busy hai, thodi der baad try karein ⏳")

    except groq.APIError:
        raise HTTPException(status_code=503, detail="AI service abhi available nahi hai 🔧")


# ---------------------------------------------------------------------------
# Forms (Pydantic) 📝
# ---------------------------------------------------------------------------
class CustomerCreate(BaseModel):
    naam: str
    city: str
    phone: str | None = None  # optional


# ---------------------------------------------------------------------------
# 👤 Customers: CRUD
# ---------------------------------------------------------------------------
@app.get("/customers")
def get_customers():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, naam, city, phone FROM customers ORDER BY id")
    rows = cursor.fetchall()
    conn.close()

    customers = []
    for id, naam, city, phone in rows:
        customers.append({"id": id, "naam": naam, "city": city, "phone": phone})
    return customers


@app.get("/customers/city/{city}")
def get_customers_by_city(city: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, naam, city, phone FROM customers WHERE LOWER(city) = LOWER(%s) ORDER BY id",
        (city,),
    )
    rows = cursor.fetchall()
    conn.close()

    customers = []
    for id, naam, city, phone in rows:
        customers.append({"id": id, "naam": naam, "city": city, "phone": phone})
    return customers


@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, naam, city, phone FROM customers WHERE id = %s",
        (customer_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Customer nahi mila ❌")

    id, naam, city, phone = row
    return {"id": id, "naam": naam, "city": city, "phone": phone}


@app.post("/customers", status_code=201)
def create_customer(customer: CustomerCreate):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customers (naam, city, phone) VALUES (%s, %s, %s) RETURNING id",
        (customer.naam, customer.city, customer.phone),
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    return {"id": new_id, "naam": customer.naam, "city": customer.city, "phone": customer.phone}


@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer: CustomerCreate):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE customers SET naam = %s, city = %s, phone = %s WHERE id = %s",
        (customer.naam, customer.city, customer.phone, customer_id),
    )
    rows_changed = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_changed == 0:
        raise HTTPException(status_code=404, detail="Customer nahi mila ❌")

    return {"id": customer_id, "naam": customer.naam, "city": customer.city, "phone": customer.phone}


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
    rows_changed = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_changed == 0:
        raise HTTPException(status_code=404, detail="Customer nahi mila ❌")

    return {"message": f"Customer {customer_id} delete ho gaya 🗑️"}


@app.get("/customers/{customer_id}/orders")
def get_customer_orders(customer_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT o.id, r.naam, o.total_amount, o.status, o.order_time
        FROM orders o
        INNER JOIN restaurants r ON o.restaurant_id = r.id
        WHERE o.customer_id = %s
        ORDER BY o.order_time DESC
        """,
        (customer_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    orders = []
    for id, restaurant, amount, status, order_time in rows:
        orders.append({
            "order_id": id,
            "restaurant": restaurant,
            "amount": amount,
            "status": status,
            "time": order_time,
        })
    return orders


# ---------------------------------------------------------------------------
# 🍽️ Restaurants
# ---------------------------------------------------------------------------
@app.get("/restaurants")
def get_restaurants(city: str | None = None):
    conn = get_conn()
    cursor = conn.cursor()

    if city is None:
        cursor.execute(
            "SELECT id, naam, city, cuisine, rating FROM restaurants ORDER BY rating DESC"
        )
    else:
        cursor.execute(
            """SELECT id, naam, city, cuisine, rating FROM restaurants
               WHERE LOWER(city) = LOWER(%s) ORDER BY rating DESC""",
            (city,),
        )
    rows = cursor.fetchall()
    conn.close()

    restaurants = []
    for id, naam, city, cuisine, rating in rows:
        restaurants.append({
            "id": id,
            "naam": naam,
            "city": city,
            "cuisine": cuisine,
            "rating": float(rating),
        })
    return restaurants


@app.get("/restaurants/{restaurant_id}/menu")
def get_menu(restaurant_id: int):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT naam FROM restaurants WHERE id = %s", (restaurant_id,))
    restaurant = cursor.fetchone()
    if restaurant is None:
        conn.close()  # raise se pehle close!
        raise HTTPException(status_code=404, detail="Restaurant nahi mila ❌")

    cursor.execute(
        "SELECT id, naam, price, is_veg FROM menu_items WHERE restaurant_id = %s ORDER BY price",
        (restaurant_id,),
    )
    rows = cursor.fetchall()
    conn.close()

    menu = []
    for id, naam, price, is_veg in rows:
        menu.append({"id": id, "naam": naam, "price": price, "veg": is_veg})

    return {"restaurant": restaurant[0], "menu": menu}


# ---------------------------------------------------------------------------
# 🤖 AI endpoints
# ---------------------------------------------------------------------------
def get_naam_city(customer_id: int):
    """Customer ka naam aur city laao, nahi mila toh 404"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT naam, city FROM customers WHERE id = %s", (customer_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Customer nahi mila ❌")
    return row


@app.get("/customers/{customer_id}/welcome")
def welcome_customer(customer_id: int):
    naam, city = get_naam_city(customer_id)

    message = ask_ai(
        system_prompt=(
            "Tum ek food delivery app ke friendly assistant ho. Hinglish mein, 2 line ka "
            "chhota welcome message likho. Customer ki city ka koi famous khana zaroor mention karo."
        ),
        user_prompt=f"Customer ka naam: {naam}. City: {city}.",
        temperature=0.8,  # welcome thoda creative 🔥
    )
    return {"customer": naam, "city": city, "message": message}


@app.get("/customers/{customer_id}/suggestion")
def suggest_customer(customer_id: int):
    naam, city = get_naam_city(customer_id)

    suggestions = ask_ai(
        system_prompt=(
            "You are a food suggestion app. According to the customer's city, suggest 3 famous "
            "food items. Reply in Hinglish. Suggest only food items."
        ),
        user_prompt=f"Customer ka naam: {naam}. City: {city}.",
        temperature=0.1,  # facts hain, toh safe 🧊
    )
    return {"customer": naam, "city": city, "suggestions": suggestions}