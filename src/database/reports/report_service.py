from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session

from src.database.base.exceptions import ValidationError, EntityNotFoundError
from src.database.reports.report_models import Report
from src.database.reports.report_repository import ReportRepo
from src.database.timeframes.timeframe_service import TimeframeService


@dataclass(frozen=True)
class ReportValidationError(ValidationError):
    message: str


@dataclass(frozen=True)
class ReportNotFoundError(EntityNotFoundError):
    message: str


class ReportService:
    """
    Service for managing reports.

    Handles CRUD operations for report planning and reflection content.
    Commitments and stats are queried separately via CommitmentService.
    """

    def __init__(self, session: Session):
        self.session = session
        self.repo = ReportRepo(session)
        self.timeframe_service = TimeframeService(session)

    def get_or_create_for_timeframe(
            self,
            *,
            user_id: int,
            timeframe_id: int,
    ) -> Report:
        """
        Get or create a report for a timeframe.

        Args:
            user_id: The user ID
            timeframe_id: The timeframe ID

        Returns:
            The report (existing or newly created)
        """
        # Check if report already exists
        existing = self.repo.find_by_timeframe(user_id=user_id, timeframe_id=timeframe_id)
        if existing:
            return existing

        # Get the timeframe to validate it exists
        timeframe = self.timeframe_service.get_timeframe(timeframe_id, user_id)
        if not timeframe:
            raise ReportValidationError(f"Timeframe {timeframe_id} not found")

        # Create the report
        return self.repo.create(
            user_id=user_id,
            timeframe_id=timeframe_id,
        )

    def get_report(self, report_id: int, user_id: int) -> Report | None:
        """Get a specific report by ID."""
        return self.repo.get(report_id, user_id=user_id)

    def get_by_timeframe(self, timeframe_id: int, user_id: int) -> Report | None:
        """Get a report by its timeframe ID."""
        return self.repo.find_by_timeframe(user_id=user_id, timeframe_id=timeframe_id)

    def update_report(
            self,
            *,
            report_id: int,
            user_id: int,
            plan: str | None = None,
            reason: str | None = None,
            pre_notes: str | None = None,
            post_notes: str | None = None,
    ) -> Report | None:
        """
        Update a report's editable fields.

        Args:
            report_id: The report ID
            user_id: The user ID
            plan: New plan text (or None to leave unchanged)
            reason: New reason text (or None to leave unchanged)
            pre_notes: New pre_notes text (or None to leave unchanged)
            post_notes: New post_notes text (or None to leave unchanged)

        Returns:
            The updated report, or None if not found
        """
        report = self.get_report(report_id, user_id)
        if not report:
            return None

        # Build update dict (only include non-None values)
        updates = {}
        if plan is not None:
            updates['plan'] = plan
        if reason is not None:
            updates['reason'] = reason
        if pre_notes is not None:
            updates['pre_notes'] = pre_notes
        if post_notes is not None:
            updates['post_notes'] = post_notes

        return self.repo.update(report, **updates)

    def delete_report(self, report_id: int, user_id: int) -> bool:
        """Delete a report."""
        report = self.get_report(report_id, user_id)
        if not report:
            return False
        return self.repo.delete(report)

    def build_report_dict(
            self,
            report: Report,
            *,
            commitment_scope: str = 'window',
            full: bool = False,
    ) -> dict:
        """
        Build a complete report dictionary with dynamic data.

        Args:
            report: The report instance
            commitment_scope: How to query commitments:
                - 'window': All commitments within this timeframe's time boundaries (default)
                - 'direct': Only commitments directly to this timeframe
                - 'none': Don't include commitments or stats in response
            full: Whether to include full metadata (id, timestamps, etc.)

        Returns:
            Complete report dictionary
        """
        # Start with base report data
        data = report.as_dict_full() if full else report.as_dict()

        # Add label and report_type from timeframe
        if report.timeframe:
            data['label'] = report.timeframe.label
            data['report_type'] = report.timeframe.kind

        # If scope is 'none', skip all commitment querying
        if commitment_scope == 'none':
            return data

        # Query commitments
        commitments = self._get_commitments_for_report(
            report=report,
            scope=commitment_scope,
        )

        # Add commitments and stats to response
        data['commitments'] = [
            self._serialize_commitment(c) for c in commitments
        ]
        data['stats'] = self._compute_stats(commitments)

        return data


    def _get_commitments_for_report(
            self,
            report: Report,
            scope: str = 'window',
    ) -> list:
        """
        Get commitments for a report based on the specified scope.

        Args:
            report: The report instance
            scope: 'direct' for commitments to this exact timeframe,
                   'window' for all commitments within the timeframe's boundaries

        Returns:
            List of commitments with targets eagerly loaded
        """
        from src.database.commitments.commitment_service import CommitmentService
        commitment_service = CommitmentService(self.session)

        if scope == 'direct':
            # Only commitments directly to this timeframe
            return commitment_service.search(
                user_id=report.user_id,
                timeframe_id=report.timeframe_id,
                include_targets=True,
            )
        else:
            # All commitments within this timeframe's time window
            # This includes both:
            # 1. Soft commitments to nested timeframes (weeks within a month, etc.)
            # 2. Hard commitments with due dates in this window

            if not report.timeframe:
                return []

            # Query using time boundaries
            # For hard commitments: use due_after/due_before
            # For soft commitments: we need to query by nested timeframe boundaries

            # Get all timeframes that fall within this timeframe's window
            nested_timeframes = self._get_nested_timeframes(report.timeframe)
            nested_timeframe_ids = [tf.id for tf in nested_timeframes]
            nested_timeframe_ids.append(report.timeframe_id)  # Include the target timeframe itself

            # Query commitments:
            # - Soft commitments to any of these timeframes
            # - Hard commitments with due dates in this window
            soft_commitments = commitment_service.search(
                user_id=report.user_id,
                timeframe_ids=nested_timeframe_ids,
                is_hard=False,
                include_targets=True,
            )

            hard_commitments = commitment_service.search(
                user_id=report.user_id,
                is_hard=True,
                due_after=report.timeframe.start_at_utc,
                due_before=report.timeframe.end_at_utc,
                include_targets=True,
            )

            # Combine and deduplicate by ID
            all_commitments = soft_commitments + hard_commitments
            seen_ids = set()
            unique_commitments = []
            for c in all_commitments:
                if c.id not in seen_ids:
                    seen_ids.add(c.id)
                    unique_commitments.append(c)

            # Sort by due_at (nulls last), then created_at
            unique_commitments.sort(
                key=lambda c: (
                    c.due_at_utc is None,
                    c.due_at_utc if c.due_at_utc else c.created_at,
                    c.created_at
                )
            )

            return unique_commitments

    def _get_nested_timeframes(self, timeframe) -> list:
        """
        Get all timeframes that fall within the given timeframe's boundaries.

        Args:
            timeframe: The parent timeframe

        Returns:
            List of timeframes that start and end within the parent's boundaries
        """
        from src.database.timeframes.timeframe_models import Timeframe

        # Query for all timeframes that are fully contained within this timeframe's boundaries
        nested = (
            self.session.query(Timeframe)
            .filter(
                Timeframe.user_id == timeframe.user_id,
                Timeframe.start_at_utc >= timeframe.start_at_utc,
                Timeframe.end_at_utc <= timeframe.end_at_utc,
                Timeframe.id != timeframe.id,  # Exclude the timeframe itself
            )
            .all()
        )

        return nested

    def _serialize_commitment(self, commitment) -> dict:
        """
        Serialize a commitment with its target for API response.

        Args:
            commitment: Commitment instance (with .target attached if include_targets was True)

        Returns:
            Dictionary representation of the commitment
        """
        data = commitment.as_dict()

        # Add target details if available
        if hasattr(commitment, 'target') and commitment.target:
            data['target'] = commitment.target.as_dict()

        return data

    def _compute_stats(self, commitments: list) -> dict:
        """
        Compute statistics from a list of commitments.

        Args:
            commitments: List of commitment instances

        Returns:
            Dictionary with computed statistics
        """
        stats = {
            'total': len(commitments),
            'planned': 0,
            'completed': 0,
            'by_status': {},
            'by_type': {},
        }

        for commitment in commitments:
            # Count by status
            status = commitment.status or 'planned'
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

            if status == 'planned':
                stats['planned'] += 1
            elif status == 'done':
                stats['completed'] += 1

            # Count by target type
            target_type = commitment.target_type
            stats['by_type'][target_type] = stats['by_type'].get(target_type, 0) + 1

        return stats