from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from src.database.base.exceptions import ValidationError
from .repository import ReportTemplateRepository, ReportTemplateMetricRepository, MetricTypeRepository
from .models import ReportTemplate, ReportTemplateMetric


class TemplateValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


VALID_TIMEFRAME_KINDS = {'day', 'week', 'month', 'season', 'year'}


class TemplateService:
    """Service layer for report template operations"""

    def __init__(self, session: Session):
        self.session = session
        self.template_repo = ReportTemplateRepository(session)
        self.template_metric_repo = ReportTemplateMetricRepository(session)
        self.metric_type_repo = MetricTypeRepository(session)

    # ─────────────────────────────────────────────────────────────────────
    # Template CRUD
    # ─────────────────────────────────────────────────────────────────────

    def get_template(self, template_id: int, user_id: int) -> Optional[ReportTemplate]:
        """Get a template by ID"""
        return self.template_repo.get(template_id, user_id)

    def get_default_template(self, user_id: int, timeframe_kind: str) -> Optional[ReportTemplate]:
        """Get the default template for a timeframe kind"""
        return self.template_repo.get_default_for_kind(user_id, timeframe_kind)

    def list_templates(self, user_id: int, timeframe_kind: Optional[str] = None) -> List[ReportTemplate]:
        """List all templates for a user, optionally filtered by timeframe kind"""
        if timeframe_kind:
            return self.template_repo.list_for_kind(user_id, timeframe_kind)
        return self.template_repo.list_for_user(user_id)

    def create_template(self, user_id: int, name: str, timeframe_kind: str,
                        is_default: bool = False, metric_type_ids: Optional[List[int]] = None) -> ReportTemplate:
        """Create a new template, optionally with initial metrics"""
        name = (name or "").strip()
        if not name:
            raise TemplateValidationError("Name is required")

        if timeframe_kind not in VALID_TIMEFRAME_KINDS:
            raise TemplateValidationError(
                f"Invalid timeframe_kind: {timeframe_kind}. Must be one of: {', '.join(VALID_TIMEFRAME_KINDS)}"
            )

        # If setting as default, clear other defaults first
        if is_default:
            self.template_repo.clear_defaults_for_kind(user_id, timeframe_kind)

        template = self.template_repo.create(
            user_id=user_id,
            name=name,
            timeframe_kind=timeframe_kind,
            is_default=is_default
        )

        # Add initial metrics if provided
        if metric_type_ids:
            for idx, metric_type_id in enumerate(metric_type_ids):
                self.template_metric_repo.create(
                    user_id=user_id,
                    template_id=template.id,
                    metric_type_id=metric_type_id,
                    sort_order=idx
                )

        return template

    def update_template(self, template: ReportTemplate, data: Dict) -> ReportTemplate:
        """Update a template's name, timeframe_kind, or is_default"""
        update_data = {}

        if 'name' in data:
            name = (data['name'] or "").strip()
            if not name:
                raise TemplateValidationError("Name cannot be empty")
            update_data['name'] = name

        if 'timeframe_kind' in data:
            if data['timeframe_kind'] not in VALID_TIMEFRAME_KINDS:
                raise TemplateValidationError(
                    f"Invalid timeframe_kind: {data['timeframe_kind']}. Must be one of: {', '.join(VALID_TIMEFRAME_KINDS)}"
                )
            update_data['timeframe_kind'] = data['timeframe_kind']

        if 'is_default' in data and data['is_default']:
            # Use set_default to handle clearing other defaults
            kind = update_data.get('timeframe_kind', template.timeframe_kind)
            self.template_repo.clear_defaults_for_kind(template.user_id, kind)
            update_data['is_default'] = True
        elif 'is_default' in data:
            update_data['is_default'] = False

        if update_data:
            return self.template_repo.update(template, **update_data)
        return template

    def set_default_template(self, template: ReportTemplate) -> ReportTemplate:
        """Set a template as the default for its timeframe kind"""
        return self.template_repo.set_default(template)

    def delete_template(self, template: ReportTemplate) -> bool:
        """Delete a template (cascades to template metrics)"""
        return self.template_repo.delete(template)

    # ─────────────────────────────────────────────────────────────────────
    # Template Metrics
    # ─────────────────────────────────────────────────────────────────────

    def get_template_metrics(self, template_id: int, user_id: int) -> List[ReportTemplateMetric]:
        """Get all metrics in a template, ordered by sort_order"""
        return self.template_metric_repo.get_for_template(template_id, user_id)

    def add_metric_to_template(self, template: ReportTemplate, metric_type_id: int,
                                user_id: int, sort_order: Optional[int] = None) -> ReportTemplateMetric:
        """Add a metric to a template"""
        # Verify metric type exists and belongs to user
        metric_type = self.metric_type_repo.get(metric_type_id, user_id)
        if not metric_type:
            raise TemplateValidationError(f"Metric type {metric_type_id} not found")

        # Check if already in template
        existing = self.template_metric_repo.get_by_template_and_metric(
            template.id, metric_type_id, user_id
        )
        if existing:
            raise TemplateValidationError("Metric is already in this template")

        # If no sort_order specified, add at end
        if sort_order is None:
            current_metrics = self.get_template_metrics(template.id, user_id)
            sort_order = len(current_metrics)

        return self.template_metric_repo.create(
            user_id=user_id,
            template_id=template.id,
            metric_type_id=metric_type_id,
            sort_order=sort_order
        )

    def remove_metric_from_template(self, template: ReportTemplate, metric_type_id: int,
                                     user_id: int) -> bool:
        """Remove a metric from a template"""
        existing = self.template_metric_repo.get_by_template_and_metric(
            template.id, metric_type_id, user_id
        )
        if existing:
            return self.template_metric_repo.delete(existing)
        return False

    def reorder_template_metrics(self, template: ReportTemplate, metric_type_ids: List[int],
                                  user_id: int) -> List[ReportTemplateMetric]:
        """Reorder metrics in a template by providing ordered list of metric_type_ids"""
        results = []
        for idx, metric_type_id in enumerate(metric_type_ids):
            tm = self.template_metric_repo.get_by_template_and_metric(
                template.id, metric_type_id, user_id
            )
            if tm:
                updated = self.template_metric_repo.update(tm, sort_order=idx)
                results.append(updated)
        return results