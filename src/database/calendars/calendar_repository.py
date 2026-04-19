from src.database.base.base_repositories import UserOwnedRepository
from .calendar_models import Calendar
from sqlalchemy.orm import Session

class CalendarRepo(UserOwnedRepository[Calendar]):
    def __init__(self, session: Session):
        super().__init__(session=session, model_class=Calendar)