from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from src.database.base.exceptions import ValidationError
from .repository import MetricTypeRepository
from .models import MetricType


class MetricTypeValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


VALID_VALUE_TYPES = {'integer', 'float', 'rating', 'boolean'}


class MetricTypeService:
    """Service layer for metric type operations"""

    def __init__(self, session: Session):
        self.session = session
        self.repo = MetricTypeRepository(session)

    def get_metric_type(self, metric_type_id: int, user_id: int) -> Optional[MetricType]:
        """Get a metric type by ID"""
        return self.repo.get(metric_type_id, user_id)

    def list_metric_types(self, user_id: int, include_archived: bool = False) -> List[MetricType]:
        """List all metric types for a user"""
        if include_archived:
            metrics = self.repo.list_for_user(user_id)
        else:
            metrics = self.repo.list_active(user_id)
        return sorted(metrics, key=lambda m: (m.sort_order or 0, m.name))

    def create_metric_type(self, user_id: int, name: str, value_type: str,
                           data: Optional[Dict] = None) -> MetricType:
        """Create a new metric type"""
        name = (name or "").strip()
        if not name:
            raise MetricTypeValidationError("Name is required")

        if value_type not in VALID_VALUE_TYPES:
            raise MetricTypeValidationError(
                f"Invalid value_type: {value_type}. Must be one of: {', '.join(VALID_VALUE_TYPES)}"
            )

        data = data or {}

        # Validate min/max for rating type
        if value_type == 'rating':
            min_val = data.get('min_value')
            max_val = data.get('max_value')
            if min_val is not None and max_val is not None and min_val >= max_val:
                raise MetricTypeValidationError("min_value must be less than max_value")

        return self.repo.create(
            user_id=user_id,
            name=name,
            value_type=value_type,
            unit=data.get('unit'),
            min_value=data.get('min_value'),
            max_value=data.get('max_value'),
            sort_order=data.get('sort_order')
        )

    def update_metric_type(self, metric_type: MetricType, data: Dict) -> MetricType:
        """Update a metric type"""
        update_data = {}

        if 'name' in data:
            name = (data['name'] or "").strip()
            if not name:
                raise MetricTypeValidationError("Name cannot be empty")
            update_data['name'] = name

        if 'value_type' in data:
            if data['value_type'] not in VALID_VALUE_TYPES:
                raise MetricTypeValidationError(
                    f"Invalid value_type: {data['value_type']}. Must be one of: {', '.join(VALID_VALUE_TYPES)}"
                )
            update_data['value_type'] = data['value_type']

        for field in ('unit', 'min_value', 'max_value', 'sort_order'):
            if field in data:
                update_data[field] = data[field]

        # Validate min/max if both are being set or already exist
        new_min = update_data.get('min_value', metric_type.min_value)
        new_max = update_data.get('max_value', metric_type.max_value)
        if new_min is not None and new_max is not None and new_min >= new_max:
            raise MetricTypeValidationError("min_value must be less than max_value")

        if update_data:
            return self.repo.update(metric_type, **update_data)
        return metric_type

    def archive_metric_type(self, metric_type: MetricType) -> MetricType:
        """Archive a metric type (soft delete)"""
        return self.repo.archive(metric_type)

    def reactivate_metric_type(self, metric_type: MetricType) -> MetricType:
        """Reactivate an archived metric type"""
        return self.repo.reactivate(metric_type)

    def delete_metric_type(self, metric_type: MetricType) -> bool:
        """
        Hard delete a metric type.
        Warning: This cascades to all MetricValues using this type.
        Prefer archive_metric_type to preserve historical data.
        """
        return self.repo.delete(metric_type)