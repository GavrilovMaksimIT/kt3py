import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
THUMB_DIR = UPLOAD_DIR / "thumbnails"
UPLOAD_DIR.mkdir(exist_ok=True)
THUMB_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {"image/png", "image/jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Разрешены только изображения PNG и JPEG")

    contents = await file.read()
    await file.seek(0)
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл слишком большой. Максимальный размер — 5 МБ")

    extension = ".png" if file.content_type == "image/png" else ".jpg"
    file_id = uuid.uuid4().hex
    original_path = UPLOAD_DIR / f"{file_id}{extension}"
    thumb_path = THUMB_DIR / f"{file_id}_thumb{extension}"
    original_path.write_bytes(contents)

    try:
        with Image.open(original_path) as image:
            image.verify()
        with Image.open(original_path) as image:
            image.thumbnail((200, 200))
            if extension == ".jpg" and image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGB")
            image.save(thumb_path, format="PNG" if extension == ".png" else "JPEG")
    except (UnidentifiedImageError, OSError):
        original_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Файл не является корректным изображением")

    base_url = "http://localhost:8000"
    return {
        "original_url": f"{base_url}/uploads/{original_path.name}",
        "thumbnail_url": f"{base_url}/uploads/thumbnails/{thumb_path.name}",
    }
