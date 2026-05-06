from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import CompetitorWatch, Integration, NotificationRule, Product, ScheduledReport, Upload, User
from app.schemas.platform import (
    CompetitorWatchCreate,
    CompetitorWatchOut,
    IntegrationCreate,
    IntegrationOut,
    NotificationRuleCreate,
    NotificationRuleOut,
    ScheduledReportCreate,
    ScheduledReportOut,
)
from app.services.platform_catalog import platform_catalog

router = APIRouter()


@router.get("/platform/catalog")
def get_platform_catalog() -> dict:
    return platform_catalog()


@router.get("/platform/overview")
def platform_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    integrations = db.scalars(
        select(Integration).where(Integration.user_id == current_user.id)
    ).all()
    rules = db.scalars(
        select(NotificationRule).where(NotificationRule.user_id == current_user.id)
    ).all()
    competitors = db.scalars(
        select(CompetitorWatch).where(CompetitorWatch.user_id == current_user.id)
    ).all()
    schedules = db.scalars(
        select(ScheduledReport).where(ScheduledReport.user_id == current_user.id)
    ).all()

    return {
        "integrations": {
            "total": len(integrations),
            "connected": len([item for item in integrations if item.status == "connected"]),
            "by_category": {
                category: len([item for item in integrations if item.category == category])
                for category in ["marketplace", "accounting", "shipping"]
            },
        },
        "alerts": {
            "rules": len(rules),
            "enabled": len([rule for rule in rules if rule.enabled]),
            "channels": sorted({rule.channel for rule in rules}),
        },
        "competitors": {
            "tracked": len(competitors),
            "needs_check": len([item for item in competitors if item.status == "watching"]),
        },
        "scheduled_reports": {
            "total": len(schedules),
            "enabled": len([schedule for schedule in schedules if schedule.enabled]),
        },
    }


@router.get("/integrations", response_model=list[IntegrationOut])
def list_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Integration]:
    return db.scalars(
        select(Integration)
        .where(Integration.user_id == current_user.id)
        .order_by(Integration.category, Integration.provider)
    ).all()


@router.post("/integrations", response_model=IntegrationOut, status_code=201)
def upsert_integration(
    payload: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Integration:
    integration = db.scalar(
        select(Integration).where(
            Integration.user_id == current_user.id,
            Integration.category == payload.category,
            Integration.provider == payload.provider,
        )
    )
    if integration is None:
        integration = Integration(
            user_id=current_user.id,
            category=payload.category,
            provider=payload.provider,
        )
        db.add(integration)

    integration.sync_frequency = payload.sync_frequency
    integration.config = _masked_config(payload.config)
    integration.status = "connected" if payload.config else "needs_credentials"
    db.commit()
    db.refresh(integration)
    return integration


@router.post("/integrations/{integration_id}/sync")
def sync_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    integration = db.scalar(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.user_id == current_user.id,
        )
    )
    if integration is None:
        raise HTTPException(status_code=404, detail="Integration not found")

    integration.last_sync_at = datetime.now(timezone.utc)
    integration.status = "connected"
    db.commit()
    return {
        "status": "queued",
        "provider": integration.provider,
        "category": integration.category,
        "datasets": _datasets_for_category(integration.category),
        "message": "Real provider adapter is ready to be wired with API credentials.",
    }


@router.get("/notification-rules", response_model=list[NotificationRuleOut])
def list_notification_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NotificationRule]:
    return db.scalars(
        select(NotificationRule)
        .where(NotificationRule.user_id == current_user.id)
        .order_by(NotificationRule.event)
    ).all()


@router.post("/notification-rules", response_model=NotificationRuleOut, status_code=201)
def create_notification_rule(
    payload: NotificationRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationRule:
    rule = NotificationRule(user_id=current_user.id, **payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/competitors", response_model=list[CompetitorWatchOut])
def list_competitors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CompetitorWatch]:
    return db.scalars(
        select(CompetitorWatch)
        .where(CompetitorWatch.user_id == current_user.id)
        .order_by(CompetitorWatch.created_at.desc())
    ).all()


@router.post("/competitors", response_model=CompetitorWatchOut, status_code=201)
def create_competitor_watch(
    payload: CompetitorWatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompetitorWatch:
    watch = CompetitorWatch(user_id=current_user.id, **payload.model_dump())
    db.add(watch)
    db.commit()
    db.refresh(watch)
    return watch


@router.post("/competitors/{watch_id}/check")
def check_competitor_watch(
    watch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    watch = db.scalar(
        select(CompetitorWatch).where(
            CompetitorWatch.id == watch_id,
            CompetitorWatch.user_id == current_user.id,
        )
    )
    if watch is None:
        raise HTTPException(status_code=404, detail="Competitor watch not found")

    watch.last_checked_at = datetime.now(timezone.utc)
    watch.status = "queued"
    db.commit()
    return {
        "status": "queued",
        "message": "Scraping job queued. Add a provider-specific scraper before production use.",
    }


@router.get("/scheduled-reports", response_model=list[ScheduledReportOut])
def list_scheduled_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ScheduledReport]:
    return db.scalars(
        select(ScheduledReport)
        .where(ScheduledReport.user_id == current_user.id)
        .order_by(ScheduledReport.created_at.desc())
    ).all()


@router.post("/scheduled-reports", response_model=ScheduledReportOut, status_code=201)
def create_scheduled_report(
    payload: ScheduledReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScheduledReport:
    schedule = ScheduledReport(user_id=current_user.id, **payload.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


@router.get("/planning/summary")
def planning_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    upload_ids_query = select(Upload.id).where(Upload.user_id == current_user.id)
    totals = db.execute(
        select(
            func.coalesce(func.sum(Product.revenue), 0),
            func.coalesce(func.sum(Product.cost), 0),
            func.coalesce(func.sum(Product.ads_spend), 0),
            func.coalesce(func.sum(Product.profit), 0),
        ).where(Product.upload_id.in_(upload_ids_query))
    ).one()

    monthly_revenue = float(totals[0] or 0)
    monthly_cost = float(totals[1] or 0)
    monthly_ads = float(totals[2] or 0)
    monthly_profit = float(totals[3] or 0)
    daily_revenue = monthly_revenue / 30 if monthly_revenue else 0

    return {
        "sales_forecast": {
            "next_30_days": round(daily_revenue * 30, 2),
            "next_60_days": round(daily_revenue * 60, 2),
            "next_90_days": round(daily_revenue * 90, 2),
            "method": "baseline_daily_average",
        },
        "cash_projection": {
            "expected_income": round(monthly_revenue, 2),
            "expected_outflow": round(monthly_cost + monthly_ads, 2),
            "expected_profit": round(monthly_profit, 2),
        },
        "scenarios": [
            _scenario("price_down_10", monthly_revenue * 0.9, monthly_cost, monthly_ads),
            _scenario("ads_double", monthly_revenue * 1.15, monthly_cost, monthly_ads * 2),
            _scenario("remove_loss_products", monthly_revenue * 0.92, monthly_cost * 0.85, monthly_ads * 0.9),
        ],
    }


def _masked_config(config: dict | None) -> dict | None:
    if not config:
        return None
    masked: dict = {}
    for key, value in config.items():
        lowered = key.lower()
        if any(secret in lowered for secret in ["token", "secret", "password", "key"]):
            masked[key] = "***"
        else:
            masked[key] = value
    return masked


def _datasets_for_category(category: str) -> list[str]:
    return {
        "marketplace": ["orders", "stock", "invoices"],
        "accounting": ["ledger", "e_invoice", "expenses"],
        "shipping": ["shipping_cost", "delivery_status", "delivery_time"],
    }.get(category, ["dataset"])


def _scenario(name: str, revenue: float, cost: float, ads: float) -> dict:
    profit = revenue - cost - ads
    return {
        "id": name,
        "revenue": round(revenue, 2),
        "cost": round(cost, 2),
        "ads_spend": round(ads, 2),
        "profit": round(profit, 2),
        "margin": round((profit / revenue * 100) if revenue else 0, 2),
    }
