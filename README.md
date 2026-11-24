# 🍕 Swiggy Customer CRUD API

A RESTful backend API for managing customers, built with **FastAPI** and **PostgreSQL**.
Supports full CRUD operations with input validation and secure database queries.

## ✨ Features

- **Full CRUD** – Create, read, update and delete customers
- **Input validation** using Pydantic (invalid data is rejected with `422`)
- **SQL injection safe** – all queries use parameterized placeholders
- **Proper HTTP status codes** – `200`, `201`, `404`, `422`
- **Auto-generated API docs** with Swagger UI at `/docs`
- **Secrets kept out of code** using environment variables (`.env`)

## 🛠️ Tech Stack

- **Python 3**
- **FastAPI** – web framework
- **PostgreSQL** – database
- **psycopg 3** – PostgreSQL driver
- **Pydantic** – data validation
- **Uvicorn** – ASGI server

## 📌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers` | Get all customers |
| GET | `/customers/{id}` | Get a customer by ID (404 if not found) |
| GET | `/customers/city/{city}` | Get customers by city |
| POST | `/customers` | Create a new customer |
| PUT | `/customers/{id}` | Update a customer |
| DELETE | `/customers/{id}` | Delete a customer |

### Example: Create a customer

**Request** – `POST /customers`
```json
{
  "naam": "Atharva",
  "city": "Pune"
}
```

**Response** – `201 Created`
```json
{
  "id": 5,
  "naam": "Atharva",
  "city": "Pune"
}
```

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/swiggy-crud-api.git
cd swiggy-crud-api
```

**2. Create a virtual environment and install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Create the database table** (in PostgreSQL, database `swiggy`)
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    naam TEXT,
    city TEXT
);
```

**4. Add a `.env` file** with your database password
```
password=your_db_password
```

**5. Start the server**
```bash
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/docs** to try the API. 🎉

## 👤 Author

**Atharva** – [GitHub](https://github.com/Atharvatiwari28)