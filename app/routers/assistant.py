from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models import User
from app.services.assistant import answer

router = APIRouter(prefix="/assistant", tags=["assistant"])


class AskIn(BaseModel):
    question: str = Field(min_length=2, max_length=500)


@router.post("/ask")
def ask(body: AskIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return answer(body.question, db, user)
