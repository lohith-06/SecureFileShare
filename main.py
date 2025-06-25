# main.py

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import List
from jose import jwt, JWTError
from passlib.context import CryptContext
import uvicorn, os, shutil
from datetime import datetime, timedelta

app = FastAPI()

# Simulated DB
users_db = {}
files_db = []
SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------------------- Models --------------------------
class User(BaseModel):
    email: EmailStr
    password: str
    role: str  # "ops" or "client"
    verified: bool = False

# ---------------------------- Utils --------------------------
def create_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

def verify_user(token: str = Form(...)):
    payload = decode_token(token)
    email = payload.get("sub")
    if email not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    return users_db[email]

# ---------------------------- Routes --------------------------
@app.post("/signup")
def signup(email: EmailStr = Form(...), password: str = Form(...)):
    if email in users_db:
        raise HTTPException(status_code=400, detail="Email exists")
    users_db[email] = User(email=email, password=pwd_context.hash(password), role="client", verified=False)
    # Simulate email verification URL
    verify_token = create_token({"sub": email}, timedelta(minutes=60))
    return {"encrypted_url": f"/verify-email?token={verify_token}"}

@app.get("/verify-email")
def verify_email(token: str):
    data = decode_token(token)
    email = data.get("sub")
    if email in users_db:
        users_db[email].verified = True
        return {"message": "Email verified"}
    raise HTTPException(status_code=404, detail="Invalid verification")

@app.post("/login")
def login(email: EmailStr = Form(...), password: str = Form(...)):
    user = users_db.get(email)
    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": email, "role": user.role})
    return {"token": token}

@app.post("/upload")
def upload_file(file: UploadFile = File(...), user=Depends(verify_user)):
    if user.role != "ops":
        raise HTTPException(status_code=403, detail="Only ops user can upload")
    if file.filename.split(".")[-1] not in ["pptx", "docx", "xlsx"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    files_db.append(file.filename)
    return {"message": "Uploaded successfully"}

@app.get("/files")
def list_files(user=Depends(verify_user)):
    if user.role != "client":
        raise HTTPException(status_code=403, detail="Only client user can list files")
    return {"files": files_db}

@app.get("/download/{filename}")
def get_download_url(filename: str, user=Depends(verify_user)):
    if user.role != "client":
        raise HTTPException(status_code=403, detail="Access denied")
    download_token = create_token({"filename": filename, "sub": user.email}, timedelta(minutes=10))
    return {"download-link": f"/secure-download/{download_token}", "message": "success"}

@app.get("/secure-download/{token}")
def secure_download(token: str):
    data = decode_token(token)
    email = data.get("sub")
    filename = data.get("filename")
    user = users_db.get(email)
    if not user or user.role != "client":
        raise HTTPException(status_code=403, detail="Invalid access")
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

# ---------------------------- Run --------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
