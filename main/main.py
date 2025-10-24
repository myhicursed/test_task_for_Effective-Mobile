from sqlalchemy.orm import Session
from main.core.core import create_tables
from fastapi import FastAPI, Depends, HTTPException, Response, Request
from main.schemas.schemas import UserCreate, UserUpdate, UserLogin
from main.database.database import get_session
from main.core.core import create_user, update_user, deactivate_user, login_user, logout_user, get_current_user, check_access
from main.mock_data import MOCK_PASSENGERS
import uvicorn

app = FastAPI()

@app.post("/register")
def register(user: UserCreate, session: Session = Depends(get_session)):
    try:
        new_user = create_user(session, user)
        return {"message": "Пользователь успешно зарегистрирован", "user_id": new_user.user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(user: UserLogin, response: Response, session: Session = Depends(get_session)):
    return login_user(session, user.email, user.password, response)

@app.post("/logout")
def logout(request: Request, response: Response, session: Session = Depends(get_session)):
    return logout_user(session, request, response)

@app.patch("/users/me")
def update_profile(update_data: UserUpdate, request: Request, session: Session = Depends(get_session)):
    current_user = get_current_user(session, request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    updated_user = update_user(current_user.user_id, session, update_data)
    return {"message": "Профиль обновлен", "user_id": updated_user.user_id}

@app.delete("/users/me")
def delete_profile(request: Request, session: Session = Depends(get_session)):
    current_user = get_current_user(session, request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    user = deactivate_user(current_user.user_id, session)
    return {"message": "Аккаунт удален", "user_id": user.user_id}

@app.get("/passengers")
def read_passengers(request: Request, db: Session = Depends(get_session)):
    user = get_current_user(db, request)
    check_access(user)
    return MOCK_PASSENGERS

@app.post("/passengers")
def add_passenger(request: Request, db: Session = Depends(get_session)):
    user = get_current_user(db, request)
    check_access(user, write=True)
    new_passenger = {"id": len(MOCK_PASSENGERS) + 1, "name": "Новый пассажир"}
    MOCK_PASSENGERS.append(new_passenger)
    return {"message": "Пассажир добавлен", "passenger": new_passenger}

if __name__ == "__main__":
    create_tables()
    uvicorn.run("main.main:app", port=8080)






