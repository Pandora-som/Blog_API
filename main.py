from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
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
# from auth import basic_auth


app = FastAPI()

@app.get("/posts", response_model=List[pyd.BaseState])
def get_all_states(db: Session = Depends(get_db)):
    states = db.query(m.State).all()
    return states
