import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from fastapi.responses import JSONResponse
from google.auth.transport.requests import Request
from fastapi.middleware.cors import CORSMiddleware  # Для фронтенда
import tempfile

load_dotenv()

app = FastAPI(title="Демо: Word to Google Docs Template")

# CORS для локального фронтенда (добавь свой origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для демо; в прод — укажи домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']

# Кэш токена
cached_token = None
token_expiry = 0
import time

async def get_credentials():
    global cached_token, token_expiry
    if time.time() < token_expiry:
        return cached_token

    credentials = Credentials(
        None,
        refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        scopes=SCOPES
    )

    # Правильный рефреш с Request()
    request = Request()
    credentials.refresh(request)

    cached_token = credentials
    # expiry — это datetime, переводим в timestamp
    token_expiry = credentials.expiry.timestamp() if credentials.expiry else time.time() + 3500

    return credentials

@app.post("/upload-and-template")
async def upload_and_template(file: UploadFile = File(...)):
    try:
        creds = await get_credentials()
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # Сохраняем файл временно
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
            tmp_file.write(await file.read())
            file_path = tmp_file.name

        # Загрузка + конвертация в Google Doc
        file_metadata = {
            'name': file.filename.replace('.docx', '') + ' (шаблон)',
            'mimeType': 'application/vnd.google-apps.document'
        }
        media = MediaFileUpload(file_path, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        doc_id = uploaded_file.get('id')

        # Замена на плейсхолдеры (адаптируй под твои Word-файлы)
        replacements = {
            "[Имя]": "{{client_name}}",
            "[Дата]": "{{date}}",
            "[Сумма]": "{{amount}}"
            # Добавь больше: ключ — что искать, значение — плейсхолдер
        }
        requests = []
        for find, replace in replacements.items():
            requests.append({
                'replaceAllText': {
                    'containsText': {'text': find, 'matchCase': True},
                    'replaceText': replace
                }
            })

        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

        # Чистим
        try:
            os.remove(file_path)
        except PermissionError as e:
            print(f"Не удалось удалить файл сразу: {e} — оставляем на диске")

        return {"doc_id": doc_id, "message": "Шаблон готов! Теперь вызови /get-preview для просмотра."}

    except HttpError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

@app.get("/get-preview")
async def get_preview(doc_id: str):
    try:
        creds = await get_credentials()
        access_token = creds.token  # Свежий access_token

        preview_url = f"https://drive.google.com/file/d/{doc_id}/preview?access_token={access_token}"
        edit_url = f"https://docs.google.com/document/d/{doc_id}/edit?access_token={access_token}"

        return {"preview_url": preview_url, "edit_url": edit_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")