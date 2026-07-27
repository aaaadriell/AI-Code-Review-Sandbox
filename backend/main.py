import secrets
import sqlite3

import requests
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data import CUSTOMERS

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

# In-memory session tokens. Fine for a demo; a real app would use a proper
# auth/session store.
active_tokens: set[str] = set()

db = sqlite3.connect(":memory:", check_same_thread=False)
db.execute("CREATE TABLE customers (id INTEGER, name TEXT, company TEXT)")
db.executemany(
    "INSERT INTO customers VALUES (?, ?, ?)",
    [(c["id"], c["name"], c["company"]) for c in CUSTOMERS],
)
db.commit()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


def require_auth(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ")
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return token


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    """Login User"""
    if payload.username != ADMIN_USERNAME or payload.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = secrets.token_urlsafe(32)
    active_tokens.add(token)
    return LoginResponse(token=token)


@app.post("/api/auth/logout")
def logout(token: str = Depends(require_auth)):
    """Log out the user and invalidate their session token"""
    active_tokens.discard(token)
    return {"detail": "Logged out"}


@app.get("/api/customers")
def list_customers(search: str = "", token: str = Depends(require_auth)):
    """Return a list of customers, optionally filtered by a search term"""
    query = search.strip().lower()
    if not query:
        return CUSTOMERS
    return [
        customer
        for customer in CUSTOMERS
        if query in customer["name"].lower() or query in customer["company"].lower()
    ]


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: int, token: str = Depends(require_auth)):
    """Return information about a specific customer"""
    for customer in CUSTOMERS:
        if customer["id"] == customer_id:
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")


# Violates "All DB queries must use parameterised inputs" — user input is
# concatenated directly into the SQL string instead of using a placeholder.
@app.get("/api/customers/search-raw")
def search_customers_raw(name: str, token: str = Depends(require_auth)):
    """Search customers by exact name using a raw SQL query"""
    query = f"SELECT id, name, company FROM customers WHERE name = '{name}'"
    rows = db.execute(query).fetchall()
    return [{"id": r[0], "name": r[1], "company": r[2]} for r in rows]


# Violates "All external API calls must have explicit timeout values" — the
# requests.get call below has no timeout and can hang indefinitely.
@app.get("/api/customers/{customer_id}/enrich")
def enrich_customer(customer_id: int, token: str = Depends(require_auth)):
    """Fetch enrichment data for a customer from an external service"""
    response = requests.get(f"https://api.example.com/enrich/{customer_id}")
    return response.json()


# Violates "All functions must have a docstring" — no docstring here.
@app.get("/api/customers/stats/count")
def get_customer_count(token: str = Depends(require_auth)):
    active = sum(1 for customer in CUSTOMERS if customer["status"] == "Active")
    return {"total": len(CUSTOMERS), "active": active}
