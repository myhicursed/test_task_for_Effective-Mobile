from main.database.database import Base, engine, get_session
from main.models.models import Users, Roles
from sqlalchemy.orm import Session
from main.schemas.schemas import UserCreate
from passlib.hash import bcrypt

def create_tables():
    Base.metadata.create_all(bind=engine)

def create_user(session: Session, user: UserCreate):
    if user.password != user.password_repeat:
        raise ValueError("Пароли не совпадают")
    user_email = session.query(Users).filter(Users.email == user.email).first()
    if user_email:
        raise ValueError("Пользователь с таким email уже существует")

    """
    ограничение в 72 байта во избежание ошибки по длине пароля
    """
    hashed_password = bcrypt.hash(user.password[:72])

    new_user = Users(
        first_name = user.first_name,
        last_name = user.last_name,
        patronymic = user.patronymic,
        email = user.email,
        password_hash = hashed_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


