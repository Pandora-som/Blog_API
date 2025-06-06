from fastapi import FastAPI, HTTPException, Depends, UploadFile, Query, Form
from database import get_db
from sqlalchemy.orm import Session
import models as m
from typing import List
import pyd
import shutil
from fastapi.staticfiles import StaticFiles
import string
import random
import os
from auth import basic_auth


app = FastAPI()

@app.get("/api/posts", response_model=List[pyd.BaseState])
def get_all_states(limit:int=Query(10,lt=100), page:None|int=Query(1),category:None|int=Query(None),status:None|int=Query(None),db: Session = Depends(get_db)):
    states = db.query(m.State)
    if category:
        states = states.filter(m.State.category_id == category)
    if status:
        states = states.filter(m.State.status_id == status)
    if limit:
        states = states[(page-1)*limit:page*limit]
    print(states)
    return states
    get_states = states.all()
    if not get_states:
        raise HTTPException(404, "Статьи не найдены!")
    return get_states
