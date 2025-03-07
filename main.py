from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from schemas import UserCreate, UserUpdate, UserResponse
from services import UserService
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Allow requests from any origin 
    allow_credentials=True, # Allow credentials (e.g. Cookies, Auth Tokens)
    allow_methods=["*"],    # Allow all HTTP methods (e.g. GET, POST, PUT, DELETE)
    allow_headers=["*"],    # Allow all HTTP headers (e.g. Authorization, Content-Type)
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Welcome message
@app.get("/welcome/")
def read_root():
    return {"message": "Welcome to my FastAPI app!"}

# Add a new user
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.create_user(user)

# Get all users
@app.get("/all-users/")
def get_users(db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.get_users()

# Get a single user by email
@app.get("/users/{email}", response_model=UserResponse)
def get_user(email: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.get_user(email)

# Update a user's name, position, or university based on their email
@app.put("/users/{email}", response_model=UserResponse)
def update_user(email: str, user_data: UserUpdate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.update_user(email, user_data)

# Delete a user
@app.delete("/users/{email}")
def delete_user(email: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.delete_user(email)
