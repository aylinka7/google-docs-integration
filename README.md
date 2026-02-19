# FastAPI Google Docs Template Demo

This project is a FastAPI backend that integrates with Google Drive API and Google Docs API to process and convert documents (e.g., Word → Google Docs template).

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

---

### 2️⃣ Create and Activate Virtual Environment

```bash
python -m venv venv
```

**Mac/Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables Setup

Create a `.env` file in the root directory of the project and add the following:

```
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REFRESH_TOKEN=your_google_refresh_token
```

⚠️ Important:

* Do NOT commit the `.env` file to Git.
* Make sure `.env` is added to `.gitignore`.

---

## ▶️ Running the Application

Start the server using:

```bash
uvicorn main:app --reload
```

The application will be available at:

```
http://127.0.0.1:8000
```

Interactive API documentation (Swagger UI):

```
http://127.0.0.1:8000/docs
```

---

## 🔧 Required Google Cloud Configuration (One-Time Setup)

To obtain the required credentials:

1. Create a project in Google Cloud Console
2. Enable:

   * Google Drive API
   * Google Docs API
3. Configure OAuth Consent Screen (External)
4. Create OAuth Client ID (Web Application)
5. Use OAuth 2.0 Playground to generate a Refresh Token

Then place the credentials inside the `.env` file.

---

## 📦 Environment Variables

| Variable             | Description                                         |
| -------------------- | --------------------------------------------------- |
| GOOGLE_CLIENT_ID     | OAuth Client ID from Google Cloud                   |
| GOOGLE_CLIENT_SECRET | OAuth Client Secret                                 |
| GOOGLE_REFRESH_TOKEN | Long-lived refresh token for backend authentication |

---

## 🛡 Security Notes

* Never expose your credentials publicly.
* If credentials are compromised, revoke them immediately in Google Cloud Console.
* Keep your `.env` file private.

---

## 📚 Tech Stack

* FastAPI
* Uvicorn
* Google Drive API
* Google Docs API
