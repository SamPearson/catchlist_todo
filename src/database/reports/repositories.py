from typing import List, Optional
from sqlalchemy.orm import Session

from src.database.base.repositories import UserOwnedRepository
from .models import Report, MetricType, MetricValue, ReportTemplate, ReportTemplateMetric


class ReportRepository(UserOwnedRepository[Report]):
    """Repository for Report operations"""

    def __init__(self, session: Session):
        super().__init__(session=session, model_class=Report)

    def get_by_timeframe(self, timeframe_id: int, user_id: int) -> Optional[Report]:
        """Get report by timeframe ID"""
        return self.session.query(Report).filter_by(
            timeframe_id=timeframe_id,
            user_id=user_id
        ).first()

    def create(self, user_id: int, timeframe_id: int, plan: Optional[str] = None,
               reason: Optional[str] = None, pre_notes: Optional[str] = None,
               post_notes: Optional[str] = None) -> Report:
        """Create a new report"""
        return super().create(
            user_id=user_id,
            timeframe_id=timeframe_id,
            plan=plan,
            reason=reason,
            pre_notes=pre_notes,
            post_notes=post_notes
        )


class MetricTypeRepository(UserOwnedRepository[MetricType]):
    """Repository for MetricType operations"""

    def __init__(self, session: Session):
        super().__init__(session=session, model_class=MetricType)

    def list_active(self, user_id: int) -> List[MetricType]:
        """List all active metric types for a user"""
        return self.list_for_user(user_id, active=True)

    def create(self, user_id: int, name: str, value_type: str,
               unit: Optional[str] = None, min_value: Optional[int] = None,
               max_value: Optional[int] = None, sort_order: Optional[int] = None) -> MetricType:
        """Create a new metric type"""
        return super().create(
            user_id=user_id,
            name=name,
            value_type=value_type,
            unit=unit,
            min_value=min_value,
            max_value=max_value,
            active=True,
            sort_order=sort_order
        )

    def archive(self, metric_type: MetricType) -> MetricType:
        """Archive a metric type (soft delete)"""
        return self.update(metric_type, active=False)

    def reactivate(self, metric_type: MetricType) -> MetricType:
        """Reactivate an archived metric type"""
        return self.update(metric_type, active=True)


class MetricValueRepository(UserOwnedRepository[MetricValue]):
    """Repository for MetricValue operations"""

    def __init__(self, session: Session):
        super().__init__(session=session, model_class=MetricValue)

    def get_for_report(self, report_id: int, user_id: int) -> List[MetricValue]:
        """Get all metric values for a report"""
        return self.list_for_user(user_id, report_id=report_id)

    def get_by_report_and_metric(self, report_id: int, metric_type_id: int,
                                  user_id: int) -> Optional[MetricValue]:
        """Get a specific metric value by report and metric type"""
        return self.session.query(MetricValue).filter_by(
            report_id=report_id,
            metric_type_id=metric_type_id,
            user_id=user_id
        ).first()

    def create(self, user_id: int, report_id: int, metric_type_id: int,
               value_int: Optional[int] = None, value_float: Optional[float] = None,
               value_bool: Optional[bool] = None) -> MetricValue:
        """Create a new metric value"""
        return super().create(
            user_id=user_id,
            report_id=report_id,
            metric_type_id=metric_type_id,
            value_int=value_int,
            value_float=value_float,
            value_bool=value_bool
        )


class ReportTemplateRepository(UserOwnedRepository[ReportTemplate]):
    """Repository for ReportTemplate operations"""

    def __init__(self, session: Session):
        super().__init__(session=session, model_class=ReportTemplate)

    def get_default_for_kind(self, user_id: int, timeframe_kind: str) -> Optional[ReportTemplate]:
        """Get the default template for a timeframe kind"""
        return self.session.query(ReportTemplate).filter_by(
            user_id=user_id,
            timeframe_kind=timeframe_kind,
            is_default=True
        ).first()

    def list_for_kind(self, user_id: int, timeframe_kind: str) -> List[ReportTemplate]:
        """List all templates for a timeframe kind"""
        return self.list_for_user(user_id, timeframe_kind=timeframe_kind)

    def create(self, user_id: int, name: str, timeframe_kind: str,
               is_default: bool = False) -> ReportTemplate:
        """Create a new template"""
        return super().create(
            user_id=user_id,
            name=name,
            timeframe_kind=timeframe_kind,
            is_default=is_default
        )

    def clear_defaults_for_kind(self, user_id: int, timeframe_kind: str) -> None:
        """Clear default flag for all templates of a given kind"""
        templates = self.list_for_kind(user_id, timeframe_kind)
        for template in templates:
            if template.is_default:
                self.update(template, is_default=False)

    def set_default(self, template: ReportTemplate) -> ReportTemplate:
        """Set a template as default, clearing other defaults for that kind"""
        self.clear_defaults_for_kind(template.user_id, template.timeframe_kind)
        return self.update(template, is_default=True)


class ReportTemplateMetricRepository(UserOwnedRepository[ReportTemplateMetric]):
    """Repository for ReportTemplateMetric operations"""

    def __init__(self, session: Session):
        super().__init__(session=session, model_class=ReportTemplateMetric)

    def get_for_template(self, template_id: int, user_id: int) -> List[ReportTemplateMetric]:
        """Get all metrics for a template, ordered by sort_order"""
        metrics = self.list_for_user(user_id, template_id=template_id)
        return sorted(metrics, key=lambda m: m.sort_order or 0)

    def get_by_template_and_metric(self, template_id: int, metric_type_id: int,
                                    user_id: int) -> Optional[ReportTemplateMetric]:
        """Get a specific template metric association"""
        return self.session.query(ReportTemplateMetric).filter_by(
            template_id=template_id,
            metric_type_id=metric_type_id,
            user_id=user_id
        ).first()

    def create(self, user_id: int, template_id: int, metric_type_id: int,
               sort_order: Optional[int] = None) -> ReportTemplateMetric:
        """Add a metric to a template"""
        return super().create(
            user_id=user_id,
            template_id=template_id,
            metric_type_id=metric_type_id,
            sort_order=sort_order
        )