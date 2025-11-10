import token
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import default_is_clause_element
from pwdlib import PasswordHash
from database import Base, engine, SessionLocal
from models import User

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Initialize Argon2 for hashing
password_hash = PasswordHash.recommended()

app = FastAPI()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

class UserSignup(BaseModel):
    username: str
    firstname: str
    lastname: str
    phonenumber: str
    email: EmailStr
    password: str
    
# User Login 
class UserLogin(BaseModel):
    username: str
    password: str

# Update Username 
class UpdateUsername(BaseModel):
    userID: int
    oldUsername: str
    newUsername: str

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

@app.post("/v1/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    # Base case 1 : Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User Email Already Exists")
    
    # Case 2: User doesn't exist so we create a new user 
    new_user = User(firstname=user.firstname, lastname=user.lastname, username=user.username, email=user.email, password=get_password_hash(user.password), phonenumber=user.phonenumber)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message":"User created successfully", "user":{"id":new_user.id, "email": new_user.email}}

@app.post("/v1/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(User.username == user.username).first()

    # Base case 1 user does not exist
    if not existing_user:
        raise HTTPException(status_code=400, detail=f"{user.username} does not exist")

    # Case 2 User exists & Password is correct
    if verify_password(user.password, existing_user.password):
        # send login token
        return {"message":"User logged in Successfully", "user":{"name":existing_user.firstname,"email":existing_user.email}}
    # Case 3 user does exists && password is incorrect
    raise HTTPException(status_code=400, detail="Password incorrect")
    



           









# Test APIs -------------------------------------------------------------------------
@app.delete("/users/delete/account/{user_email}")
def delete(user_email: str, db: Session = Depends(get_db)):
        existing_user = db.query(User).filter(User.email == user_email).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User Does Not Exists")
        db.delete(existing_user)
        db.commit()

        return {"message":"User deleted successfully", "email":user_email}

@app.get("/users/info/{user_name}")
def info(user_name: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_name).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User Does Not Exist")

    return {"message":"First name and email of:", "name":existing_user.name, "email":existing_user.email}

@app.put("/users/update/username/{id}")
def update_username(user: UpdateUsername, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.id == user.userID).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User does not exist")
    
    existing_user.username = user.newUsername
    db.commit()
    db.refresh(existing_user)

    return {"message": f"{user.oldUsername} updated username to '{user.newUsername}'"}