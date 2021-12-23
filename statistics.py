from functools import wraps

from models import User, LogRecord, get_db, get_user, close_db
from config import Config


def log_function_call(log_unit_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            info = {
                'message': message.text,
                'args': args,
                'kwargs': kwargs,
            }
            try:
                result = func(message, *args, **kwargs)
            except Exception as ex:
                info['exception'] = str(ex)
                if Config.DEBUG:
                    raise ex
            else:
                info['result'] = result
                return result
            finally:
                db = get_db()
                user = get_user(db, message.from_user.id)
                if not user:
                    user = User.new(
                        message.from_user.id,
                        message.from_user.last_name,
                        message.from_user.first_name,
                        message.from_user.username
                    )
                    db.add(user)
                    db.commit()
                rec = LogRecord.new(user, log_unit_name, message.chat.id, info)
                db.add(rec)
                db.commit()
                close_db()
        return wrapper
    return decorator