import os
import psycopg
from dotenv import load_dotenv
from groq import Groq
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()                                          # 1. 📖 pehle .env padho

ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))    # 2. 🔑 phir key use karo

app = FastAPI()

def get_conn():
    return psycopg.connect(
        host = "localhost",
        port = 5432,
        dbname = "swiggy",
        user = "atharva",
        password = os.getenv("password")
    )

@app.get("/customers")
def get_customers():
    conn=get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id,naam,city FROM customers ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    
    customer=[]
    for id, naam, city in rows:
        customer.append({"id":id, "naam":naam, "city":city})
    return customer

@app.get("/customers/{customer_id}")
def get_customers(customer_id:int):
    conn= get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id,naam,city FROM customers WHERE id = %s", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        raise HTTPException(status_code=404,detail="No data found")
    
    id,naam,city = row
    return {"id": id, "naam": naam, "city": city}


@app.get("/customers/city/{city}")
def get_by_city(city: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, naam, city FROM customers WHERE LOWER(city) = LOWER(%s)",
        (city,)
    )
    rows = cursor.fetchall()
    conn.close()

    customers = []
    for id, naam, city in rows:
        customers.append({"id": id, "naam": naam, "city": city})
    return customers
        

from pydantic import BaseModel          # ← upar imports mein jodo

class CustomerCreate(BaseModel):        # ← form 📝
    naam: str
    city: str

@app.post("/customers", status_code=201)
def create_customer(customer: CustomerCreate):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO customers (naam, city) VALUES (%s, %s) RETURNING id",
        (customer.naam, customer.city)
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    return {"id": new_id, "naam": customer.naam, "city": customer.city}


@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer: CustomerCreate):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE customers SET naam = %s, city = %s WHERE id = %s",
        (customer.naam, customer.city, customer_id)
    )
    rows_changed = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_changed == 0:
        raise HTTPException(status_code=404, detail="Customer nahi mila ❌")

    return {"id": customer_id, "naam": customer.naam, "city": customer.city}


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM customers WHERE id = %s",    # 1. SQL DELETE query
        (customer_id,)                           # 2. placeholder mein kya?
    )
    rows_changed = cursor.rowcount            # 3. kitni rows gayi?
    conn.commit()                           # 4. save! 💾
    conn.close()

    if rows_changed == 0:
        raise HTTPException(status_code=404, detail="Customer nahi mila ❌")

    return {"message": f"Customer {customer_id} delete ho gaya 🗑️"}



@app.get("/customers/{customer_id}/welcome")
def welcome_customer(customer_id: int):
    # 1. 🐘 Database se customer nikaalo
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT naam, city FROM customers WHERE id = %s",
        (customer_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Customer nahi mila ❌")

    naam, city = row

    # 2. 🤖 AI se message likhwao
    response = ai_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "Tum ek food delivery app ke friendly assistant ho. Hinglish mein, 2 line ka chhota welcome message likho. Customer ki city ka koi famous khana zaroor mention karo."},
            {"role": "user", "content": f"Customer ka naam: {naam}. City: {city}."}
        ],
        temperature=0.1
    )
    message = response.choices[0].message.content

    # 3. 🚀 Jawab bhejo
    return {"customer": naam, "city": city, "message": message}
        
        
@app.get("/customers/{customer_id}/suggestion")
def suggest_customer(customer_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT naam, city FROM customers WHERE id = %s",
        (customer_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    naam, city = row

    response = ai_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "You are a food suggestion app. According to the customer's city, suggest 3 famous food items. Reply in Hinglish. give only the names of food items"},
            {"role": "user", "content": f"Customer ka naam: {naam}. City: {city}."}
        ],
        temperature=0.1
    )
    message = response.choices[0].message.content

    return {"customer": naam, "city": city, "suggestions": message}