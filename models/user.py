import datetime
from uuid import uuid4

from sqlalchemy import UUID, Boolean, Column, DateTime, String

from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        nullable=False,
        default=uuid4,
    )
    email = Column(String, unique=True, index=True, nullable=False)
    mail_confirmed = Column(Boolean, default=False)
    username = Column(String, unique=True, index=True, nullable=False)
    is_superuser = Column(Boolean, default=False)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now())
