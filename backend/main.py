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


@app.get("/api/customers/{customer_id}/profile")
def get_customer_profile(customer_id: int, token: str = Depends(require_auth)):
    """Return a customer's profile enriched with an external risk score.

    Falls back to a risk score of "unknown" if the external service is
    unreachable or slow, rather than failing the whole request.
    """
    row = db.execute(
        "SELECT id, name, company FROM customers WHERE id = ?",
        (customer_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    risk_score = "unknown"
    try:
        response = requests.get(
            f"https://api.example.com/risk-score/{customer_id}",
            timeout=5,
        )
        response.raise_for_status()
        risk_score = response.json().get("score", "unknown")
    except requests.RequestException:
        # External service is best-effort enrichment; a failure here
        # shouldn't take down the whole profile lookup.
        pass

    return {"id": row[0], "name": row[1], "company": row[2], "risk_score": risk_score}
