from functools import wraps

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .result import Result


def handle_sqlalchemy_errors(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            return method(*args, **kwargs)
        except SQLAlchemyError as e:
            self.session.rollback()
            if isinstance(e, IntegrityError):
                return Result(success=False, message=str(e.orig))
            else:
                return Result(success=False, message=str(e))
        finally:
            self.session.commit()

    return wrapper
