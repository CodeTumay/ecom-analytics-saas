from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    revenue: Mapped[float] = mapped_column(Float, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0)
    commission: Mapped[float] = mapped_column(Float, default=0)
    shipping: Mapped[float] = mapped_column(Float, default=0)
    ads_spend: Mapped[float] = mapped_column(Float, default=0)
    profit: Mapped[float] = mapped_column(Float, default=0)
    margin: Mapped[float] = mapped_column(Float, default=0)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    upload = relationship("Upload", back_populates="products")
