from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models import Product, Upload, UploadStatus
from app.processing.processor import process_file
from app.worker.celery_app import celery_app


@celery_app.task(name="process_upload")
def process_upload(upload_id: int, user_mapping: dict[str, str] | None = None) -> None:
    db = SessionLocal()
    try:
        upload = db.get(Upload, upload_id)
        if upload is None:
            return

        upload.status = UploadStatus.PROCESSING
        upload.error_message = None
        db.commit()

        result = process_file(upload.file_path, user_mapping or upload.mapping)
        upload.mapping = result.get("mapping")

        if result["status"] == "needs_mapping":
            upload.status = UploadStatus.NEEDS_MAPPING
            upload.analysis = {
                "columns": result["columns"],
                "missing_required": result["missing_required"],
                "missing_optional": result["missing_optional"],
            }
            db.commit()
            return

        db.execute(delete(Product).where(Product.upload_id == upload.id))
        for product in result["analysis"]["products"]:
            db.add(
                Product(
                    upload_id=upload.id,
                    name=product["product_name"],
                    revenue=product["revenue"],
                    cost=product["cost"],
                    commission=product["commission"],
                    shipping=product["shipping"],
                    ads_spend=product["ads_spend"],
                    profit=product["net_profit"],
                    margin=product["profit_margin"],
                )
            )

        upload.status = UploadStatus.COMPLETED
        upload.analysis = result["analysis"]
        upload.error_message = None
        db.commit()
    except Exception as exc:
        db.rollback()
        upload = db.get(Upload, upload_id)
        if upload:
            upload.status = UploadStatus.FAILED
            upload.error_message = str(exc)
            db.commit()
        raise
    finally:
        db.close()
