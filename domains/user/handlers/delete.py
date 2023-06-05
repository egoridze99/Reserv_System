from db import db
from models import User, UserStatusEnum


def remove_user(id: str):
    user = User.query.filter(User.id == int(id)).first()

    if not user:
        return {"msg": "Пользователь не найден"}, 404

    user.status = UserStatusEnum.deprecated
    try:
        db.session.add(user)
        db.session.commit()
        return {"msg": "Пользователь успешно удален"}, 200
    except:
        return {"msg": "Произошла непредвиденная ошибка"}, 400
