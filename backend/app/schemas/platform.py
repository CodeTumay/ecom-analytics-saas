from pydantic import BaseModel, Field


class IntegrationCreate(BaseModel):
    category: str
    provider: str
    sync_frequency: str = "daily"
    config: dict | None = None


class IntegrationOut(BaseModel):
    id: int
    category: str
    provider: str
    status: str
    sync_frequency: str
    config: dict | None = None
    last_sync_at: object | None = None

    model_config = {"from_attributes": True}


class TrendyolOrderImportRequest(BaseModel):
    seller_id: str | None = None
    api_key: str | None = None
    api_secret: str | None = None
    start_date: int | None = None
    end_date: int | None = None
    status: str | None = None
    page: int = 0
    size: int = Field(default=200, le=200, ge=1)


class TrendyolOrderImportOut(BaseModel):
    upload_id: int
    status: str
    imported_rows: int
    message: str


class NotificationRuleCreate(BaseModel):
    event: str
    channel: str = "email"
    severity: str = "warning"
    enabled: bool = True
    threshold: dict | None = None


class NotificationRuleOut(BaseModel):
    id: int
    event: str
    channel: str
    severity: str
    enabled: bool
    threshold: dict | None = None

    model_config = {"from_attributes": True}


class CompetitorWatchCreate(BaseModel):
    product_name: str
    own_sku: str | None = None
    competitor_name: str
    competitor_url: str
    target_delta: float = 0


class CompetitorWatchOut(BaseModel):
    id: int
    product_name: str
    own_sku: str | None = None
    competitor_name: str
    competitor_url: str
    target_delta: float
    latest_price: float | None = None
    latest_stock: str | None = None
    status: str
    last_checked_at: object | None = None

    model_config = {"from_attributes": True}


class ScheduledReportCreate(BaseModel):
    name: str = Field(default="Weekly executive report")
    frequency: str = "weekly_monday"
    channel: str = "email"
    report_types: list[str] = Field(default_factory=list)
    recipients: list[str] = Field(default_factory=list)
    enabled: bool = True


class ScheduledReportOut(BaseModel):
    id: int
    name: str
    frequency: str
    channel: str
    report_types: list | None = None
    recipients: list | None = None
    enabled: bool

    model_config = {"from_attributes": True}
