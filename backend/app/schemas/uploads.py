from pydantic import BaseModel


class UploadOut(BaseModel):
    id: int
    original_filename: str
    status: str
    mapping: dict | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}


class MappingRequest(BaseModel):
    mapping: dict[str, str]


class CombinedReportRequest(BaseModel):
    upload_ids: list[int]


class AnalysisOut(BaseModel):
    upload_id: int
    status: str
    report_type: str | None = None
    mapping: dict | None = None
    analysis: dict | None = None
    error_message: str | None = None
