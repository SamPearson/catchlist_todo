from sqlalchemy import (
    Column, Integer, Float, String, Text, Boolean, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from src.database.base.models import UserOwnedModel


class Report(UserOwnedModel):
    """
    Unified report model linked 1:1 with a Timeframe.
    The timeframe determines the "kind" of report (day, week, month, season, year).
    """
    __tablename__ = "reports"

    timeframe_id = Column(Integer, ForeignKey('timeframes.id'), nullable=False, unique=True)

    # Planning and reflection text fields
    plan = Column(Text)
    reason = Column(Text)
    pre_notes = Column(Text)
    post_notes = Column(Text)

    # Relationships
    timeframe = relationship("Timeframe", backref="report", uselist=False)
    metric_values = relationship("MetricValue", back_populates="report", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("timeframe_id", name="uq_reports_timeframe"),
    )

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'timeframe_id': self.timeframe_id,
            'plan': self.plan,
            'reason': self.reason,
            'pre_notes': self.pre_notes,
            'post_notes': self.post_notes,
            'timeframe': self.timeframe.as_dict() if self.timeframe else None,
            'metric_values': [mv.as_dict() for mv in self.metric_values]
        })
        return data


class MetricType(UserOwnedModel):
    """
    User-defined metric definitions.
    Examples: "Sleep Hours", "Work RPE", "Diet Adherence"
    """
    __tablename__ = "metric_types"

    name = Column(String(100), nullable=False)
    value_type = Column(String(20), nullable=False)  # integer, float, rating, boolean
    unit = Column(String(20))  # e.g., "hours", "1-10"
    min_value = Column(Integer)  # for rating/bounded types
    max_value = Column(Integer)  # for rating/bounded types
    active = Column(Boolean, default=True)
    sort_order = Column(Integer)

    # Relationships
    metric_values = relationship("MetricValue", back_populates="metric_type")
    template_metrics = relationship("ReportTemplateMetric", back_populates="metric_type")

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'name': self.name,
            'value_type': self.value_type,
            'unit': self.unit,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'active': self.active,
            'sort_order': self.sort_order
        })
        return data


class MetricValue(UserOwnedModel):
    """
    Actual metric measurements recorded on a specific report.
    Uses polymorphic value storage based on metric_type's value_type.
    """
    __tablename__ = "metric_values"

    report_id = Column(Integer, ForeignKey('reports.id'), nullable=False)
    metric_type_id = Column(Integer, ForeignKey('metric_types.id'), nullable=False)

    # Polymorphic value storage - only one should be set based on metric_type.value_type
    value_int = Column(Integer)  # For integer and rating types
    value_float = Column(Float)  # For float types
    value_bool = Column(Boolean)  # For boolean types

    # Relationships
    report = relationship("Report", back_populates="metric_values")
    metric_type = relationship("MetricType", back_populates="metric_values")

    __table_args__ = (
        UniqueConstraint("report_id", "metric_type_id", name="uq_metric_values_report_metric"),
    )

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'report_id': self.report_id,
            'metric_type_id': self.metric_type_id,
            'value_int': self.value_int,
            'value_float': self.value_float,
            'value_bool': self.value_bool,
            'metric_type': self.metric_type.as_dict() if self.metric_type else None
        })
        return data

    @property
    def value(self):
        """Get the actual value based on metric type"""
        if self.metric_type:
            vt = self.metric_type.value_type
            if vt in ('integer', 'rating'):
                return self.value_int
            elif vt == 'float':
                return self.value_float
            elif vt == 'boolean':
                return self.value_bool
        return None


class ReportTemplate(UserOwnedModel):
    """
    Templates define which metrics to include when creating a report
    for a specific timeframe kind.
    """
    __tablename__ = "report_templates"

    name = Column(String(100), nullable=False)
    timeframe_kind = Column(String(16), nullable=False)  # day, week, month, season, year
    is_default = Column(Boolean, default=False)

    # Relationships
    template_metrics = relationship(
        "ReportTemplateMetric",
        back_populates="template",
        cascade="all, delete-orphan"
    )

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'name': self.name,
            'timeframe_kind': self.timeframe_kind,
            'is_default': self.is_default,
            'metrics': [tm.as_dict() for tm in self.template_metrics]
        })
        return data


class ReportTemplateMetric(UserOwnedModel):
    """
    Join table linking templates to the metrics they include.
    """
    __tablename__ = "report_template_metrics"

    template_id = Column(Integer, ForeignKey('report_templates.id'), nullable=False)
    metric_type_id = Column(Integer, ForeignKey('metric_types.id'), nullable=False)
    sort_order = Column(Integer)

    # Relationships
    template = relationship("ReportTemplate", back_populates="template_metrics")
    metric_type = relationship("MetricType", back_populates="template_metrics")

    __table_args__ = (
        UniqueConstraint("template_id", "metric_type_id", name="uq_template_metrics_template_metric"),
    )

    def as_dict(self):
        data = super().as_dict()
        data.update({
            'template_id': self.template_id,
            'metric_type_id': self.metric_type_id,
            'sort_order': self.sort_order,
            'metric_type': self.metric_type.as_dict() if self.metric_type else None
        })
        return data