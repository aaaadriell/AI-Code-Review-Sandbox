import secrets

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data import CUSTOMERS

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

# In-memory session tokens. Fine for a demo; a real app would use a proper
# auth/session store.
active_tokens: set[str] = set()

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


@app.get("/api/customers/summary")
def get_customer_summary(token: str = Depends(require_auth)):
    """Return aggregate customer stats for the dashboard header (totals by status and revenue)"""
    status_counts: dict[str, int] = {}
    for customer in CUSTOMERS:
        status_counts[customer["status"]] = status_counts.get(customer["status"], 0) + 1

    return {
        "totalCustomers": len(CUSTOMERS),
        "totalRevenue": sum(customer["totalSpent"] for customer in CUSTOMERS),
        "statusCounts": status_counts,
    }


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: int, token: str = Depends(require_auth)):
    """Return information about a specific customer"""
    for customer in CUSTOMERS:
        if customer["id"] == customer_id:
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")


