from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from utils import Result
from utils.wrapper import handle_sqlalchemy_errors
from sqlalchemy.orm.attributes import InstrumentedAttribute

T = TypeVar("T")


class AbstractDAO(Generic[T], ABC):
    def __init__(self, session: Session, model: T):
        self.session = session
        self.model = model

    @handle_sqlalchemy_errors
    def get_all(self) -> Result[T]:
        data: T = self.session.query(self.model).all()
        return Result(success=True, data=data)

    @handle_sqlalchemy_errors
    def get_by(self, column_name: InstrumentedAttribute, column_value) -> Result[T]:
        data: T = (
            self.session.query(self.model)
            .filter(getattr(self.model, column_name.key) == column_value)
            .first()
        )
        return Result(success=True, data=data)

    @handle_sqlalchemy_errors
    def create(self, obj: T) -> Result[T]:
        self.session.add(obj)
        self.session.commit()
        return Result(success=True, data=obj)

    @handle_sqlalchemy_errors
    def update(self, obj: T, update_data: dict) -> Result[T]:
        for key, value in update_data.items():
            setattr(obj, key, value)
        self.session.commit()
        return Result(success=True, data=obj)

    @handle_sqlalchemy_errors
    def delete(self, obj: T) -> Result[T]:
        self.session.delete(obj)
        self.session.commit()
        return Result(success=True, data=obj)
