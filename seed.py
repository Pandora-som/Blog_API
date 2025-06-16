from sqlalchemy.orm import Session
from database import engine
import models as m
from datetime import datetime as dt
import bcrypt

m.Base.metadata.drop_all(bind=engine)
m.Base.metadata.create_all(bind=engine)

with Session(bind=engine) as session:
    state1 = m.State(
        title="Как засолить огурчики",
        content="Статья про огурчики, вкусные огурчики",
        date_publication=dt.strptime("2019-01-01T08:00:00Z", "%Y-%m-%dT%H:%M:%SZ").date(),
        category_id="1",
        status_id="2",
        author_id="1"
    )
    session.add(state1)
    state2 = m.State(
        title="Что сажать рядом с луком?",
        content="В этой статье мы расскажем о самых лучших соседях для лука.",
        date_publication=dt.strptime("2020-01-01T08:00:00Z", "%Y-%m-%dT%H:%M:%SZ").date(),
        category_id="2",
        status_id="2",
        author_id="2"
    )
    session.add(state2)
    state3 = m.State(
        title="Какие книги прочитать для хорошего сочинения",
        content="Разбираемся в произведениях",
        date_publication=dt.strptime("2020-01-01T08:00:00Z", "%Y-%m-%dT%H:%M:%SZ").date(),
        category_id="1",
        status_id="2",
        author_id="2"
    )
    session.add(state3)
    
    state4 = m.State(
        title="Что бы приготовить?",
        content="Думаем что съесть на завтрак",
        date_publication=dt.strptime("2020-01-01T08:00:00Z", "%Y-%m-%dT%H:%M:%SZ").date(),
        category_id="1",
        status_id="1",
        author_id="2"
    )
    session.add(state4)
    
    comment1 = m.Comment(
        text="здорово",
        date=dt.strptime("2019-02-01T08:20:00Z", "%Y-%m-%dT%H:%M:%SZ").date(),
        state_id="1",
        user_id="1"
    )
    session.add(comment1)
    comment2 = m.Comment(
        text="очень круто",
        date=dt.strptime("2020-03-01T08:20:00Z", "%Y-%m-%dT%H:%M:%SZ").date(),
        state_id="1",
        user_id="1"
    )
    session.add(comment2)
    
    comment3 = m.Comment(
        text="Спасибо за статью",
        date=dt.strptime("2020-03-01T08:20:00Z", "%Y-%m-%dT%H:%M:%SZ").date(),
        state_id="1",
        user_id="1"
    )
    session.add(comment3)
    
    user1 = m.User(
        name="Ami-reader",
        password=bcrypt.hashpw(b'AmiReader', bcrypt.gensalt()),
        email="ami-reader@mail.ru",
        role_id="1"
    )
    session.add(user1)
    
    user2 = m.User(
        name="Ami-avtor",
        password=bcrypt.hashpw(b'AmiAvtor', bcrypt.gensalt()),
        email="ami-avtor@mail.ru",
        role_id="2"
    )
    session.add(user2)

    user3 = m.User(
        name="Ami-moderator",
        password=bcrypt.hashpw(b'AmiModerator', bcrypt.gensalt()),
        email="ami-moderator@mail.ru",
        role_id="3"
    )
    session.add(user3)
    
    role1 = m.Role(name="Читатель")
    session.add(role1)
    
    role2 = m.Role(name="Автор")
    session.add(role2)

    role3 = m.Role(name="Модератор")
    session.add(role3)
    
    category1 = m.Category(name="Рецепты")
    session.add(category1)
    category2 = m.Category(name="Огород и дача")
    session.add(category2)
    category3 = m.Category(name="Учёба")
    session.add(category3)
    
    status1 = m.Status(name="Черновик")
    session.add(status1)
    status2 = m.Status(name="Опубликовано")
    session.add(status2)
    
    l1=m.StateLike(user_id=1, state_id=1)
    session.add(l1)
    
    session.commit()