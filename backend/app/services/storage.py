from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.core.config import settings


def save_upload_file(
    user_id: int, file: UploadFile, allowed_extensions: set[str]
) -> Path:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(allowed_extensions))}",
        )

    user_dir = settings.storage_dir / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    destination = user_dir / f"{uuid4().hex}{extension}"

    with destination.open("wb") as buffer:
        while chunk := file.file.read(1024 * 1024):
            buffer.write(chunk)

    return destination
