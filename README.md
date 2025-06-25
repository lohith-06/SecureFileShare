
# 🔐 Secure File Sharing System (FastAPI)

A secure backend file-sharing system between two user roles — **Ops Users** and **Client Users** — built with **FastAPI**.  
The system enforces file type restrictions, secure downloads, and email verification logic using JWT-based encrypted URLs.

---

## 🚀 Features

### 👤 Ops User
- Login
- Upload `.pptx`, `.docx`, `.xlsx` files only

### 👤 Client User
- Sign up and receive an encrypted email verification link
- Email verification
- Login
- List all uploaded files
- Download files via secure, time-limited URLs

### 🔐 Security
- Role-based access control
- JWT for auth and download link encryption
- Only the requesting client can use their secure download URL

---

## 📁 Folder Structure

secure-file/
main.py  FastAPI app entry
test_logic.ipynb # (Optional) logic test notebook
├── uploads/ # Uploaded files directory
└── README.md
---

## ⚙️ Tech Stack

- **Python 3.8+**
- **FastAPI**
- **Uvicorn**
- **Pydantic**
- **Passlib (bcrypt)**
- **Jose (JWT)**
- **Cryptography**

---

## 🛠️ Installation & Setup

### 1. Clone the repo

```bash
git clone https://github.com/lohith-06/SecureFileShare.git
cd secure-file
