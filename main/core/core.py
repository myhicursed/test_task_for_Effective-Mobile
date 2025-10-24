import uuid
from main.database.database import Base, engine, get_session
from main.models.models import Users, Roles, UserSession
from sqlalchemy.orm import Session
from main.schemas.schemas import UserCreate, UserUpdate
from passlib.hash import bcrypt
from fastapi import HTTPException, Response, Request
from datetime import datetime, timedelta
from main.mock_data import permissions

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

def update_user(user_id: int,
                session: Session,
                update_data: UserUpdate
                ):
    user = session.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if update_data.first_name:
        user.first_name = update_data.first_name
    if update_data.last_name:
        user.last_name = update_data.last_name
    if update_data.patronymic:
        user.patronymic = update_data.patronymic
    if update_data.email:
        existing = session.query(Users).filter(Users.email == update_data.email).first()
        if existing and existing.user_id != user.user_id:
            raise HTTPException(status_code=409, detail="Email уже используется")
        user.email = update_data.email
    if update_data.password:
        user.password_hash = bcrypt.hash(update_data.password[:72])

    session.commit()
    session.refresh(user)
    return user

def deactivate_user(user_id: id, session: Session):
    user = session.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.is_active = False

    session.commit()
    session.refresh(user)
    return user

def login_user(session: Session,
               email: str,
               password: str,
               response: Response
               ):
    user = session.query(Users).filter(Users.email == email, Users.is_active == True).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    session_id = str(uuid.uuid4())
    expire_at = datetime.utcnow() + timedelta(days=1)
    db_session = UserSession(session_id=session_id, user_id=user.user_id, expire_at=expire_at)
    session.add(db_session)
    session.commit()

    response.set_cookie(
        key="sessionid",
        value=session_id,
        httponly=True,
        max_age=24 * 3600
    )
    return {"message": "Login успешен", "user_id": user.user_id}

def logout_user(session: Session, request: Request, response: Response):
    session_id = request.cookies.get("sessionid")
    if session_id:
        db_session = session.query(UserSession).filter(UserSession.session_id == session_id).first()
        if db_session:
            session.delete(db_session)
            session.commit()
        response.delete_cookie("sessionid")
    return {"message": "Logout успешен"}

def get_current_user(db: Session, request: Request):
    session_id = request.cookies.get("sessionid")
    if not session_id:
        return None
    db_session = db.query(UserSession).filter(
        UserSession.session_id == session_id,
        UserSession.expire_at > datetime.utcnow()
    ).first()
    if not db_session:
        return None
    return db.query(Users).filter(Users.user_id == db_session.user_id).first()


def check_access(user, write=False):
    if not user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    role = user.role.role_name
    if write and not permissions[role]["write"]:
        raise HTTPException(status_code=403, detail="Изменение запрещено")


