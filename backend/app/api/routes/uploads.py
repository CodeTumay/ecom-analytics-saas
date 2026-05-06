from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Upload, UploadStatus, User
from app.schemas.uploads import UploadOut
from app.services.storage import save_upload_file
from app.services.usage import assert_upload_allowed
from app.worker.tasks import process_upload

router = APIRouter()

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


@router.post("/upload", response_model=UploadOut, status_code=status.HTTP_202_ACCEPTED)
def upload_file(
    file: UploadFile = File(...),
    report_type: str = Form("profitability"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Upload:
    assert_upload_allowed(db, current_user)
    file_path = save_upload_file(current_user.id, file, ALLOWED_EXTENSIONS)

    upload = Upload(
        user_id=current_user.id,
        file_path=str(file_path),
        original_filename=file.filename or "upload",
        status=UploadStatus.QUEUED,
        mapping={"__report_type": report_type},
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    try:
        process_upload.delay(upload.id, None, report_type)
    except Exception as exc:
        upload.status = UploadStatus.FAILED
        upload.error_message = f"Could not enqueue processing job: {exc}"
        db.commit()
        raise HTTPException(status_code=503, detail=upload.error_message) from exc

    return upload
