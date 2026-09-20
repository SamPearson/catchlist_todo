from __future__ import annotations

import logging
from datetime import datetime, time
from typing import Any, Dict
from zoneinfo import ZoneInfo

from sqlalchemy import DateTime, Time
from sqlalchemy.orm import Session

from src.database.base.exceptions import ValidationError
from src.database.calendars.calendar_models import Calendar
from src.database.checkins.checkin_models import CheckinRecord
from src.database.commitments.commitment_models import Commitment
from src.database.db import db
from src.database.principles.principle_models import Principle, PrincipleAssociation
from src.database.projects.project_models import Project
from src.database.reports.report_models import Report
from src.database.routines.routine_models import Routine
from src.database.sessions.session_models import RoutineSession
from src.database.tags.tag_models import Tag, TagAssociation
from src.database.tasks.task_models import Task
from src.database.timeframes.timeframe_models import Timeframe
from src.database.users.user_models import User
from src.utils.timezone import validate_timezone

logger = logging.getLogger(__name__)

BACKUP_FORMAT = "catchlist-backup"
BACKUP_VERSION = 1

UTC = ZoneInfo("UTC")


class BackupValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# Entity models owned by the user (UserOwnedModel), serialized in export.
USER_OWNED_MODELS = {
    "tags": Tag,
    "principles": Principle,
    "projects": Project,
    "tasks": Task,
    "calendars": Calendar,
    "routines": Routine,
    "sessions": RoutineSession,
    "timeframes": Timeframe,
    "reports": Report,
    "commitments": Commitment,
    "checkins": CheckinRecord,
}

# Import insert order: dependencies first (parents before children).
INSERT_ORDER = [
    "tags",
    "principles",
    "projects",
    "tasks",
    "calendars",
    "routines",
    "sessions",
    "timeframes",
    "reports",
    "commitments",
    "checkins",
]

# Local keys whose value references an entity's exported id, remapped on import.
FK_MAP = {
    "tasks": {"project_id": "projects"},
    "routines": {"calendar_id": "calendars"},
    "sessions": {"routine_id": "routines"},
    "reports": {"timeframe_id": "timeframes"},
    "commitments": {"timeframe_id": "timeframes"},
}

ASSOCIATION_ENTITIES = {"tag_associations": (TagAssociation, "tag_id"), "principle_associations": (PrincipleAssociation, "principle_id")}

# Singular entity_type values (as stored in associations, commitments and
# checkins) map to the plural collection keys used in the backup blob.
ENTITY_TYPE_KEY = {
    "tag": "tags", "principle": "principles", "project": "projects",
    "task": "tasks", "calendar": "calendars", "routine": "routines",
    "session": "sessions", "timeframe": "timeframes", "report": "reports",
    "commitment": "commitments", "checkin": "checkins",
    # Tag/principle associations store the model class name lowercased.
    "routinesession": "sessions",
}


def _serialize_datetime(value) -> str | None:
    """Serialize a datetime as naive-UTC ISO string (lossless round-trip)."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if value.tzinfo is not None:
        value = value.astimezone(UTC).replace(tzinfo=None)
    return value.isoformat()


def _parse_datetime(value) -> datetime | None:
    """Parse a naive-UTC ISO string back into a naive datetime."""
    if value is None or value == "":
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        from dateutil.parser import parse as dateutil_parse

        dt = dateutil_parse(str(value))
    if dt.tzinfo is not None:
        dt = dt.astimezone(UTC).replace(tzinfo=None)
    return dt


def _serialize_time(value) -> str | None:
    if value is None:
        return None
    return value.strftime("%H:%M")


def _parse_time(value) -> time | None:
    if value is None or value == "":
        return None
    hours, minutes = map(int, str(value).split(":"))
    return time(hours, minutes)


def _serialize_row(instance) -> dict:
    """Serialize a model instance preserving raw DB column values (naive UTC)."""
    row: Dict[str, Any] = {"id": instance.id}
    for column in instance.__table__.columns:
        name = column.name
        if name in ("id", "user_id"):
            continue
        value = getattr(instance, name)
        if isinstance(column.type, DateTime):
            row[name] = _serialize_datetime(value)
        elif isinstance(column.type, Time):
            row[name] = _serialize_time(value)
        else:
            row[name] = value
    return row


class BackupService:
    def __init__(self, session: Session):
        self.session = session

    def export_all(self, user: User) -> dict:
        """Return the entirety of a user's data as a backup blob."""
        data: Dict[str, Any] = {
            "format": BACKUP_FORMAT,
            "version": BACKUP_VERSION,
            "exported_at": datetime.utcnow().isoformat(),
            "user": {
                "username": user.username,
                "name": user.name,
                "timezone": user.timezone,
            },
        }

        for key, model in USER_OWNED_MODELS.items():
            rows = (
                self.session.query(model)
                .filter_by(user_id=user.id)
                .order_by(model.id.asc())
                .all()
            )
            data[key] = [_serialize_row(r) for r in rows]

        tag_associations = []
        for tag in self.session.query(Tag).filter_by(user_id=user.id).all():
            for assoc in tag.associations:
                tag_associations.append(
                    {
                        "tag_id": assoc.tag_id,
                        "entity_id": assoc.entity_id,
                        "entity_type": assoc.entity_type,
                    }
                )
        data["tag_associations"] = tag_associations

        principle_associations = []
        for principle in self.session.query(Principle).filter_by(user_id=user.id).all():
            for assoc in principle.associations:
                principle_associations.append(
                    {
                        "principle_id": assoc.principle_id,
                        "entity_id": assoc.entity_id,
                        "entity_type": assoc.entity_type,
                    }
                )
        data["principle_associations"] = principle_associations

        return data

    def _validate_blob(self, data: dict) -> None:
        if not isinstance(data, dict):
            raise BackupValidationError("Backup data must be a JSON object.")
        if data.get("format") != BACKUP_FORMAT:
            raise BackupValidationError(f"Unsupported backup format: {data.get('format')!r}")
        version = data.get("version")
        if version != BACKUP_VERSION:
            raise BackupValidationError(f"Unsupported backup version: {version!r}")

        user_info = data.get("user")
        if not isinstance(user_info, dict) or not user_info.get("username"):
            raise BackupValidationError("Backup is missing user profile information.")
        if user_info.get("timezone") and validate_timezone(user_info["timezone"]):
            raise BackupValidationError(f"Invalid timezone: {user_info['timezone']}")

        for key in USER_OWNED_MODELS:
            if key in data and not isinstance(data[key], list):
                raise BackupValidationError(f"Backup field '{key}' must be a list.")
        for key in ASSOCIATION_ENTITIES:
            if key in data and not isinstance(data[key], list):
                raise BackupValidationError(f"Backup field '{key}' must be a list.")

    def _delete_all(self, user_id: int) -> None:
        """Delete all user data, leaf-first to respect FK constraints."""
        # Polymorphic children with no FK to other user tables.
        self.session.query(CheckinRecord).filter_by(user_id=user_id).delete(synchronize_session=False)
        self.session.query(Commitment).filter_by(user_id=user_id).delete(synchronize_session=False)
        self.session.query(Report).filter_by(user_id=user_id).delete(synchronize_session=False)
        self.session.query(RoutineSession).filter_by(user_id=user_id).delete(synchronize_session=False)

        # Associations belong to the user via their tags/principles.
        tag_ids = self.session.query(Tag.id).filter_by(user_id=user_id)
        self.session.query(TagAssociation).filter(TagAssociation.tag_id.in_(tag_ids)).delete(synchronize_session=False)
        principle_ids = self.session.query(Principle.id).filter_by(user_id=user_id)
        self.session.query(PrincipleAssociation).filter(PrincipleAssociation.principle_id.in_(principle_ids)).delete(synchronize_session=False)

        self.session.query(Task).filter_by(user_id=user_id).delete(synchronize_session=False)
        self.session.query(Routine).filter_by(user_id=user_id).delete(synchronize_session=False)
        self.session.query(Timeframe).filter_by(user_id=user_id).delete(synchronize_session=False)
        self.session.query(Project).filter_by(user_id=user_id).delete(synchronize_session=False)
        self.session.query(Calendar).filter_by(user_id=user_id).delete(synchronize_session=False)
        self.session.query(Tag).filter_by(user_id=user_id).delete(synchronize_session=False)
        self.session.query(Principle).filter_by(user_id=user_id).delete(synchronize_session=False)

    def _column_kwargs(self, row: dict, model) -> dict:
        kwargs: Dict[str, Any] = {}
        for column in model.__table__.columns:
            name = column.name
            if name in ("id", "user_id"):
                continue
            value = row.get(name)
            if isinstance(column.type, DateTime):
                kwargs[name] = _parse_datetime(value)
            elif isinstance(column.type, Time):
                kwargs[name] = _parse_time(value)
            else:
                kwargs[name] = value
        return kwargs

    def import_replace(self, user: User, data: dict) -> None:
        """Replace all of a user's data with the contents of a backup blob."""
        self._validate_blob(data)
        user_id = user.id

        # Persist profile fields that are writable on restore.
        user_info = data.get("user", {})
        if user_info.get("name") is not None:
            user.name = user_info["name"]
        if user_info.get("timezone"):
            user.timezone = user_info["timezone"]

        try:
            self._delete_all(user_id)

            id_maps: Dict[str, Dict[int, int]] = {key: {} for key in USER_OWNED_MODELS}

            for key in INSERT_ORDER:
                model = USER_OWNED_MODELS[key]
                rows = data.get(key, [])
                for row in rows:
                    old_id = row.get("id")
                    kwargs = self._column_kwargs(row, model)

                    for local_col, parent_key in FK_MAP.get(key, {}).items():
                        old_fk = kwargs.get(local_col)
                        if old_fk is not None:
                            kwargs[local_col] = id_maps[parent_key].get(old_fk, old_fk)

                    instance = model(user_id=user_id, **kwargs)
                    self.session.add(instance)
                    self.session.flush()
                    if old_id is not None:
                        id_maps[key][old_id] = instance.id

            # Rebuild tag/principles associations using remapped ids.
            for key, (_model, _id_col) in ASSOCIATION_ENTITIES.items():
                for assoc_row in data.get(key, []):
                    entity_type = assoc_row.get("entity_type")
                    entity_map = id_maps.get(ENTITY_TYPE_KEY.get(entity_type, entity_type), {})
                    entity_id = entity_map.get(assoc_row.get("entity_id"), assoc_row.get("entity_id"))
                    owner_id = assoc_row.get("tag_id" if key == "tag_associations" else "principle_id")
                    new_owner_id = id_maps["tags" if key == "tag_associations" else "principles"].get(owner_id, owner_id)
                    if entity_id is None:
                        continue
                    if key == "tag_associations":
                        self.session.add(TagAssociation(tag_id=new_owner_id, entity_id=entity_id, entity_type=entity_type))
                    else:
                        self.session.add(PrincipleAssociation(principle_id=new_owner_id, entity_id=entity_id, entity_type=entity_type))

            # Define checkin/commitment target ids last (they reference many entity types).
            for key, target_attr in (("commitments", "target_id"), ("checkins", "target_id")):
                model = USER_OWNED_MODELS[key]
                for row in data.get(key, []):
                    old_target_id = row.get(target_attr)
                    entity_type = row.get("target_type")
                    entity_map = id_maps.get(ENTITY_TYPE_KEY.get(entity_type, entity_type), {})
                    new_target_id = entity_map.get(old_target_id, old_target_id)
                    instance = (
                        self.session.query(model)
                        .filter_by(id=id_maps[key].get(row.get("id")), user_id=user_id)
                        .first()
                    )
                    if instance is not None:
                        setattr(instance, target_attr, new_target_id)

            self.session.commit()
        except BackupValidationError:
            self.session.rollback()
            raise
        except Exception as e:
            logger.exception("Backup import failed")
            self.session.rollback()
            raise BackupValidationError(f"Backup import failed: {str(e)}")