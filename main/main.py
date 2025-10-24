
from sqlalchemy.orm import Session

from main.core.core import create_tables
from fastapi import FastAPI, Depends, HTTPException
from main.schemas.schemas import UserCreate
from main.database.database import get_session
from main.core.core import create_user
import uvicorn

app = FastAPI()

@app.post("/register")
def register(user: UserCreate, session: Session = Depends(get_session)):
    try:
        new_user = create_user(session, user)
        return {"message": "Пользователь успешно зарегистрирован", "user_id": new_user.user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))





if __name__ == "__main__":
    #create_tables()
    uvicorn.run("main.main:app", port=8080, reload=True)






