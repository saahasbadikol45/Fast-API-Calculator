from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()


class Calculation(BaseModel):
    num1: float
    num2: float
    operation: str


def init_db():
    conn = sqlite3.connect("calculator.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num1 REAL,
            num2 REAL,
            operation TEXT,
            result REAL
        )
    """)

    conn.commit()
    conn.close()


# Create database/table when app starts
init_db()


@app.get("/")
def home():
    return {"message": "Calculator Running"}


@app.post("/calculate")
def calculate(data: Calculation):

    if data.operation == "+":
        result = data.num1 + data.num2

    elif data.operation == "-":
        result = data.num1 - data.num2

    elif data.operation == "*":
        result = data.num1 * data.num2

    elif data.operation == "/":
        if data.num2 == 0:
            return {"error": "Division by zero"}

        result = data.num1 / data.num2

    else:
        return {"error": "Invalid operation"}

    # Save calculation to database
    conn = sqlite3.connect("calculator.db")

    conn.execute(
        """
        INSERT INTO history
        (num1, num2, operation, result)
        VALUES (?, ?, ?, ?)
        """,
        (data.num1, data.num2, data.operation, result)
    )

    conn.commit()
    conn.close()

    return {"result": result}


@app.get("/history")
def history():

    conn = sqlite3.connect("calculator.db")

    rows = conn.execute(
        "SELECT * FROM history"
    ).fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "num1": row[1],
            "num2": row[2],
            "operation": row[3],
            "result": row[4]
        }
        for row in rows
    ]
