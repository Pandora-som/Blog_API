from fastapi import FastAPI, HTTPException, Depends, Query, Form
from database import get_db
from sqlalchemy.orm import Session
import models as m
from typing import List
import pyd
import os
import datetime
from auth import auth_handler
import logging
import bcrypt

logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w")
app = FastAPI()

@app.post("/api/login")
def login_user(user:pyd.LoginUser, db:Session=Depends(get_db)):
    user_db = db.query(m.User).filter(
        m.User.name == user.name
    ).first()
    if not user_db:
        raise HTTPException(404, "Пользователь не найден!")
    if auth_handler.verify_password(user.password, user_db.password):
        logging.info(f"User: {user_db.name} logged in at {datetime.datetime.now()}")
        return {"token": auth_handler.encode_token(user_db.id, user_db.role_id)}
    raise HTTPException(400, "Доступ запрещён!")

@app.patch("/api/post/{id}/like")
def like_state(id:int, db:Session=Depends(get_db), access:m.User=Depends(auth_handler.auth_wrapper)):
    state = db.query(m.State).filter(
        m.State.id == id
    ).first()
    if not state:
        raise HTTPException(404, "Такой статьи не существует!")
    user_db = db.query(m.User).filter(
        m.User.id == access["user_id"]
    ).first()
    if user_db in state.likes:
        raise HTTPException(400, "Вы уже ставили лайк этой статье!")
    
    state.likes.append(user_db)
    state.likes_amount = len(state.likes)

    db.add(state)
    db.commit()

    logging.info(f"User: {user_db.name} liked state: {state.id} at {datetime.datetime.now()}")
    return {"details": "Лайк оставлен!"}

@app.patch("/api/post/{id}/unlike")
def unlike_state(id:int, db:Session=Depends(get_db), access:m.User=Depends(auth_handler.auth_wrapper)):
    state = db.query(m.State).filter(
        m.State.id == id
    ).first()
    if not state:
        raise HTTPException(404, "Такой статьи не существует!")
    user_db = db.query(m.User).filter(
        m.User.id == access["user_id"]
    ).first()
    if user_db not in state.likes:
        raise HTTPException(400, "Вы ещё не оставляли лайк этой статье!")
    
    state.likes.remove(user_db)
    state.likes_amount = len(state.likes)

    db.add(state)
    db.commit()
    
    logging.info(f"User: {user_db.name} unliked state: {state.id} at {datetime.datetime.now()}")
    return {"details": "Лайк убран!"}


@app.get("/api/posts", response_model=List[pyd.SchemeState])
def get_all_states(page:None|int=Query(1), limit:int=Query(10,lt=100),category:None|str=Query(None),status:None|str=Query(None),
                   order_by:None|str=Query("desc"), db: Session = Depends(get_db)):
    states = db.query(m.State)
    if status:
        status_db = db.query(m.Status).filter(
            m.Status.name == status
        ).first()
        if not status_db:
            raise HTTPException(404, "Такого статуса не существует!")
        states = states.filter(m.State.status_id == status_db.id)
    if category:
        category_db = db.query(m.Category).filter(
            m.Category.name == category
        ).first()
        if not category_db:
            raise HTTPException(404, "Такой категории не существует!")
        states = states.filter(m.State.category_id == category_db.id)
    if order_by == "asc":
        states = states.order_by(m.State.likes_amount.asc())
    if order_by == "desc":
        states = states.order_by(m.State.likes_amount.desc())
    if limit:
        states = states[(page-1)*limit:page*limit]
        if not states:
            raise HTTPException(404, "Статьи не найдены!")
        return states
    get_states = states.all()
    if not get_states:
        raise HTTPException(404, "Статьи не найдены!")
    return get_states

@app.get("/api/post/{id}", response_model=pyd.SchemeState)
def get_post(id: int, db:Session=Depends(get_db)):
    post_db=db.query(m.State).filter(
        m.State.id==id
    ).first()
    if not post_db:
        raise HTTPException(404, "Статья не найдена!")
    return post_db

@app.post("/api/posts", response_model=pyd.SchemeState)
def create_state(state:pyd.CreateState, db:Session=Depends(get_db), access:m.User=Depends(auth_handler.author_wrapper)):
    check_user = db.query(m.User).filter(
        m.User.id == state.author_id
    ).first()
    if not check_user:
        raise HTTPException(404, "Такого пользователя не существет!")

    state_db = m.State()

    state_db.title = state.title
    state_db.content = state.content
    state_db.date_publication = state.date_publication
    state_db.status_id = state.status_id
    state_db.author_id = state.author_id
    state_db.category_id = state.category_id

    db.add(state_db)
    db.commit()
    logging.info(f"User with id: {access["user_id"]} created state: {state_db.id} at {datetime.datetime.now()}")
    return state_db

@app.put("/api/post/{id}", response_model=pyd.SchemeState)
def edit_state(id:int, state:pyd.UpdateState, db:Session=Depends(get_db), access:m.User=Depends(auth_handler.author_wrapper)):
    state_db = db.query(m.State).filter(
        m.State.id == id
    ).first()
    if not state_db:
        raise HTTPException(404, "Такой статьи не существует!")
    if state.author_id != access["user_id"]:
        if access["role_id"] != 3:
            raise HTTPException(403, "Вы не можете редактировать чужую статью!")

    state_db.title = state.title
    state_db.content = state.content
    state_db.date_publication = state.date_publication
    state_db.status_id = state.status_id
    state_db.author_id = state.author_id
    state_db.category_id = state.category_id
    
    if access["role_id"] == 3:
        state_db.likes = []
        for like_id in state.likes_id:
            user_db = db.query(m.User).filter(m.User.id == like_id).first()
            if user_db:
                state_db.likes.append(user_db)
            else:
                raise HTTPException(status_code=404, detail=f"Пользователь с id:{like_id} не найден!")

    state_db.likes_amount = len(state_db.likes)

    db.add(state_db)
    db.commit()
    logging.info(f"User with id: {access["user_id"]} changed state: {state_db.id} at {datetime.datetime.now()}")
    return state_db

@app.delete("/api/post/{id}")
def delete_state(id:int, db:Session=Depends(get_db), access:m.User=Depends(auth_handler.author_wrapper)):
    state_db = db.query(m.State).filter(
        m.State.id == id
    ).first()
    if not state_db:
        raise HTTPException(404, "Такой статьи не существует!")
    if state_db.author_id != access["user_id"]:
        if access["role_id"] != 3:
            raise HTTPException(403, "Вы не можете удалить чужую статью!")
    db.delete(state_db)
    db.commit()
    logging.info(f"User with id: {access["user_id"]} deleted state: {state_db.id} at {datetime.datetime.now()}")
    return {"details": "Статья удалена"}

@app.get("/api/comments", response_model=List[pyd.SchemeComment])
def get_comments(db:Session=Depends(get_db)):
    comments = db.query(m.Comment).all()
    if not comments:
        raise HTTPException(404, "Комментариев пока нет!")
    return comments

@app.get("/api/comment/{id}", response_model=pyd.SchemeComment)
def get_comment(id:int, db:Session=Depends(get_db)):
    comment = db.query(m.Comment).filter(
        m.Comment.id == id
    ).first()
    if not comment:
        raise HTTPException(404, "Комментария не существует!")
    return comment

@app.post("/api/comment", response_model=pyd.SchemeComment)
def create_comment(comment:pyd.CreateComment, db:Session=Depends(get_db), access:m.User=Depends(auth_handler.auth_wrapper)):
    check_state = db.query(m.State).filter(
        m.State.id == comment.state_id
    ).first()
    if not check_state:
        raise HTTPException(404, "Такой статьи не существет!")
    
    check_user = db.query(m.User).filter(
        m.User.id == comment.user_id
    ).first()
    if not check_user:
        raise HTTPException(404, "Такого пользователя не существет!")
    
    comment_db = m.Comment()

    comment_db.text = comment.text
    comment_db.date = comment.date
    comment_db.state_id = comment.state_id
    comment_db.user_id = comment.user_id

    db.add(comment_db)
    db.commit()
    logging.info(f"User with id: {access["user_id"]} created comment: {comment_db.id} - {comment_db.text[:25:]} for state: {comment_db.state_id} at {datetime.datetime.now()}")
    return comment_db

@app.put("/api/comment/{id}", response_model=pyd.SchemeComment)
def edit_comment(id:int, comment:pyd.CreateComment, db:Session=Depends(get_db), access:m.User=Depends(auth_handler.auth_wrapper)):
    check_state = db.query(m.State).filter(
        m.State.id == comment.state_id
    ).first()
    if not check_state:
        raise HTTPException(404, "Такой статьи не существет!")
    if comment.user_id != access["user_id"]:
        if access["role_id"] != 3:
            raise HTTPException(403, "Вы не можете редактировать чужой комментарий!")
    
    check_user = db.query(m.User).filter(
        m.User.id == comment.user_id
    ).first()
    if not check_user:
        raise HTTPException(404, "Такого пользователя не существет!")
    comment_db = db.query(m.Comment).filter(
        m.Comment.id == id
    ).first()
    if not comment_db:
        raise HTTPException(404, "Такого комментария не существует!")
    
    comment_db.text = comment.text
    comment_db.date = comment.date
    comment_db.state_id = comment.state_id
    comment_db.user_id = comment.user_id

    db.add(comment_db)
    db.commit()
    logging.info(f"User with id: {access["user_id"]} changed comment: {comment_db.id} - {comment_db.text[:25:]} for state: {comment_db.state_id} at {datetime.datetime.now()}")
    return comment_db

@app.delete("/api/comment/{id}")
def delete_comment(id:int, db:Session=Depends(get_db), access:m.User=Depends(auth_handler.auth_wrapper)):
    comment_db = db.query(m.Comment).filter(
        m.Comment.id == id
    ).first()
    if not comment_db:
        raise HTTPException(404, "Такого комментария не существует!")
    if comment_db.user_id != access["user_id"]:
        if access["role_id"] != 3:
            raise HTTPException(403, "Вы не можете редактировать чужой комментарий!")
    db.delete(comment_db)
    db.commit()
    logging.info(f"User with id: {access["user_id"]} deleted comment: {comment_db.id} - {comment_db.text[:25:]} for state: {comment_db.state_id} at {datetime.datetime.now()}")
    return {"details": "Комментарий удалён!"}

@app.get("/api/categories", response_model=List[pyd.BaseCategory])
def get_categories(db:Session=Depends(get_db)):
    categories = db.query(m.Category).all()
    return categories

@app.get("/api/category/{id}", response_model=pyd.BaseCategory)
def get_category(id:int, db:Session=Depends(get_db)):
    category = db.query(m.Category).filter(
        m.Category.id == id
    ).first()
    if not category:
        raise HTTPException(404, "Такой категории не существует!")
    return category

@app.post("/api/category/{name}", response_model=pyd.BaseCategory)
def create_category(name:str, db:Session=Depends(get_db), access:m.User=Depends(auth_handler.moderator_wrapper)):
    check_category = db.query(m.Category).filter(
        m.Category.name == name
    ).first()
    if check_category:
        raise HTTPException(400, "Такая категория уже существует!")
    category_db = m.Category()
    category_db.name = name

    db.add(category_db)
    db.commit()
    logging.info(f"User with id: {access["user_id"]} created category: {category_db.name} at {datetime.datetime.now()}")
    return category_db

@app.put("/api/category/{id}/{name}", response_model=pyd.BaseCategory)
def edit_category(id:int, name:str, db:Session=Depends(get_db), access:m.User=Depends(auth_handler.moderator_wrapper)):
    check_category = db.query(m.Category).filter(
        m.Category.name == name
    ).first()
    if check_category:
        raise HTTPException(400, "Такая категория уже существует!")
    
    category_db = db.query(m.Category).filter(
        m.Category.id == id
    ).first()
    if not category_db:
        raise HTTPException(400, "Такой категории не существует!")

    category_db.name = name

    db.add(category_db)
    db.commit()
    logging.info(f"User with id: {access["user_id"]} changed category: {category_db.name} at {datetime.datetime.now()}")
    return category_db

@app.delete("/api/category/{id}")
def delete_category(id:int, db:Session=Depends(get_db), access:m.User=Depends(auth_handler.moderator_wrapper)):
    category_db = db.query(m.Category).filter(
        m.Category.id == id
    ).first()
    if not category_db:
        raise HTTPException(400, "Такой категории не существует!")

    db.delete(category_db)
    db.commit()
    logging.info(f"User with id: {access["user_id"]} deleted category: {category_db.name} at {datetime.datetime.now()}")
    return {"detail": "Категория удалена!"}

