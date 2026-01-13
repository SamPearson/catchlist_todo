from typing import Dict, List, Optional
from datetime import date
from sqlalchemy.orm import Session

from src.database.base.exceptions import ValidationError
from src.database.timeframes.service import TimeframeService
from .repositories import ReportRepository, MetricValueRepository, ReportTemplateRepository, \
    ReportTemplateMetricRepository
from .models import Report, MetricValue


class ReportValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ReportService:
    """Service layer for report and metric value operations"""

    def __init__(self, session: Session):
        self.session = session
        self.report_repo = ReportRepository(session)
        self.metric_value_repo = MetricValueRepository(session)
        self.template_repo = ReportTemplateRepository(session)
        self.template_metric_repo = ReportTemplateMetricRepository(session)
        self.timeframe_service = TimeframeService(session)

    # ─────────────────────────────────────────────────────────────────────
    # Report CRUD
    # ─────────────────────────────────────────────────────────────────────

    def get_report(self, report_id: int, user_id: int) -> Optional[Report]:
        """Get a report by ID"""
        return self.report_repo.get(report_id, user_id)

    def get_report_by_timeframe(self, timeframe_id: int, user_id: int) -> Optional[Report]:
        """Get a report by its timeframe"""
        return self.report_repo.get_by_timeframe(timeframe_id, user_id)

    def list_reports(self, user_id: int, kind: Optional[str] = None) -> List[Report]:
        """List all reports for a user, optionally filtered by timeframe kind"""
        reports = self.report_repo.list_for_user(user_id)
        if kind:
            reports = [r for r in reports if r.timeframe and r.timeframe.kind == kind]
        return sorted(reports, key=lambda r: r.timeframe.start_at_utc if r.timeframe else r.created_at, reverse=True)

    def create_report(self, user_id: int, timeframe_id: int,
                      data: Optional[Dict] = None, template_id: Optional[int] = None) -> Report:
        """Create a new report, optionally applying a template"""
        # Check if report already exists for this timeframe
        existing = self.report_repo.get_by_timeframe(timeframe_id, user_id)
        if existing:
            raise ReportValidationError("A report already exists for this timeframe")

        data = data or {}
        report = self.report_repo.create(
            user_id=user_id,
            timeframe_id=timeframe_id,
            plan=data.get('plan'),
            reason=data.get('reason'),
            pre_notes=data.get('pre_notes'),
            post_notes=data.get('post_notes')
        )

        # Apply template if specified
        if template_id:
            self._apply_template_to_report(report, template_id, user_id)

        return report

    def update_report(self, report: Report, data: Dict) -> Report:
        """Update a report's text fields"""
        update_data = {}
        for field in ('plan', 'reason', 'pre_notes', 'post_notes'):
            if field in data:
                update_data[field] = data[field]

        if update_data:
            return self.report_repo.update(report, **update_data)
        return report

    def delete_report(self, report: Report) -> bool:
        """Delete a report (cascades to metric values)"""
        return self.report_repo.delete(report)

    # ─────────────────────────────────────────────────────────────────────
    # Get or Create (primary workflow)
    # ─────────────────────────────────────────────────────────────────────

    def get_or_create_report(
            self,
            user_id: int,
            kind: str,
            local_day: date,
            user_tz: str,
            template_id: Optional[int] = None,
            use_default_template: bool = True
    ) -> tuple[Report, bool]:
        """
        Get existing report or create new one for the given timeframe.
        Returns (report, created) tuple.

        If creating and template_id is provided, uses that template.
        If creating and use_default_template is True, uses the default template for that kind.
        """
        # Get or create the timeframe
        timeframe = self.timeframe_service.get_or_create_for_local_date(
            user_id=user_id,
            kind=kind,
            local_day=local_day,
            user_tz=user_tz
        )

        # Check for existing report
        existing = self.report_repo.get_by_timeframe(timeframe.id, user_id)
        if existing:
            return existing, False

        # Determine template to use
        if template_id is None and use_default_template:
            default_template = self.template_repo.get_default_for_kind(user_id, kind)
            if default_template:
                template_id = default_template.id

        # Create new report
        report = self.report_repo.create(
            user_id=user_id,
            timeframe_id=timeframe.id
        )

        if template_id:
            self._apply_template_to_report(report, template_id, user_id)

        return report, True

    def get_or_create_report_for_timeframe(
            self,
            user_id: int,
            timeframe_id: int,
            template_id: Optional[int] = None
    ) -> tuple[Report, bool]:
        """
        Get existing report or create new one for an existing timeframe.
        Returns (report, created) tuple.
        """
        existing = self.report_repo.get_by_timeframe(timeframe_id, user_id)
        if existing:
            return existing, False

        report = self.report_repo.create(
            user_id=user_id,
            timeframe_id=timeframe_id
        )

        if template_id:
            self._apply_template_to_report(report, template_id, user_id)

        return report, True

    # ─────────────────────────────────────────────────────────────────────
    # Metric Values
    # ─────────────────────────────────────────────────────────────────────

    def get_metric_values(self, report_id: int, user_id: int) -> List[MetricValue]:
        """Get all metric values for a report"""
        return self.metric_value_repo.get_for_report(report_id, user_id)

    def set_metric_value(self, report: Report, metric_type_id: int,
                         value: Optional[int | float | bool], user_id: int) -> MetricValue:
        """Set a metric value on a report (create or update)"""
        existing = self.metric_value_repo.get_by_report_and_metric(
            report.id, metric_type_id, user_id
        )

        # Determine which value field to set based on value type
        value_data = self._prepare_value_data(value)

        if existing:
            return self.metric_value_repo.update(existing, **value_data)
        else:
            return self.metric_value_repo.create(
                user_id=user_id,
                report_id=report.id,
                metric_type_id=metric_type_id,
                **value_data
            )

    def remove_metric_value(self, report: Report, metric_type_id: int, user_id: int) -> bool:
        """Remove a metric value from a report"""
        existing = self.metric_value_repo.get_by_report_and_metric(
            report.id, metric_type_id, user_id
        )
        if existing:
            return self.metric_value_repo.delete(existing)
        return False

    def bulk_set_metric_values(self, report: Report, values: Dict[int, any], user_id: int) -> List[MetricValue]:
        """Set multiple metric values at once. Keys are metric_type_ids."""
        results = []
        for metric_type_id, value in values.items():
            mv = self.set_metric_value(report, metric_type_id, value, user_id)
            results.append(mv)
        return results

    # ─────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────

    def _apply_template_to_report(self, report: Report, template_id: int, user_id: int) -> None:
        """Apply a template's metrics to a report (creates null MetricValues)"""
        template_metrics = self.template_metric_repo.get_for_template(template_id, user_id)
        for tm in template_metrics:
            # Create metric value with null value (to be filled in later)
            self.metric_value_repo.create(
                user_id=user_id,
                report_id=report.id,
                metric_type_id=tm.metric_type_id
            )

    def _prepare_value_data(self, value: Optional[int | float | bool]) -> Dict:
        """Prepare value data dict based on Python type"""
        if value is None:
            return {'value_int': None, 'value_float': None, 'value_bool': None}
        elif isinstance(value, bool):
            return {'value_int': None, 'value_float': None, 'value_bool': value}
        elif isinstance(value, int):
            return {'value_int': value, 'value_float': None, 'value_bool': None}
        elif isinstance(value, float):
            return {'value_int': None, 'value_float': value, 'value_bool': None}
        else:
            raise ReportValidationError(f"Invalid value type: {type(value)}")