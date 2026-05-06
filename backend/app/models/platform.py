from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Integration(Base):
    __tablename__ = "integrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), default="not_connected", nullable=False)
    sync_frequency: Mapped[str] = mapped_column(String(40), default="daily", nullable=False)
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    last_sync_at = mapped_column(DateTime(timezone=True), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class NotificationRule(Base):
    __tablename__ = "notification_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    event: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(40), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), default="warning", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    threshold: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


class CompetitorWatch(Base):
    __tablename__ = "competitor_watches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    own_sku: Mapped[str | None] = mapped_column(String(120), nullable=True)
    competitor_name: Mapped[str] = mapped_column(String(120), nullable=False)
    competitor_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    target_delta: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    latest_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    latest_stock: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="watching", nullable=False)
    last_checked_at = mapped_column(DateTime(timezone=True), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    frequency: Mapped[str] = mapped_column(String(40), default="weekly_monday", nullable=False)
    channel: Mapped[str] = mapped_column(String(40), default="email", nullable=False)
    report_types: Mapped[list | None] = mapped_column(JSON, nullable=True)
    recipients: Mapped[list | None] = mapped_column(JSON, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
