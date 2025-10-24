from main.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import text, ForeignKey
from datetime import datetime, timedelta

class Users(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    patronymic: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id"), default=1) #по дефоту дается роль обычного юзера
    role: Mapped["Roles"] = relationship("Roles", backref="users")
    created_at: Mapped[datetime] = mapped_column(server_default=text(
                                                "TIMEZONE('utc', now())"
    ))
    updated_at: Mapped[datetime] = mapped_column(server_default=text(
                                                "TIMEZONE('utc', now())"),
                                                onupdate=datetime.utcnow)

class Roles(Base):
    __tablename__ = 'roles'

    role_id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(unique=True, nullable=False)

class UserSession(Base):
    __tablename__ = 'sessions'

    session_id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))
    created_at: Mapped[datetime] = mapped_column(server_default=text(
                                                "TIMEZONE('utc', now())"),
                                                onupdate=datetime.utcnow)
    expire_at: Mapped[datetime] = mapped_column(default=lambda: datetime.utcnow() + timedelta(days=1))

