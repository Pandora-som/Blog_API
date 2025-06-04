from sqlalchemy.orm import Session
from database import engine
import models as m
from datetime import datetime as dt

m.Base.metadata.drop_all(bind=engine)
m.Base.metadata.create_all(bind=engine)

with Session(bind=engine) as session:
    state1 = m.State(
        title="Как засолить огурчики",
        content="Статья про огурчики, вкусные огурчики",
        date_publication=dt.strptime("2019-01-01T08:00:00Z", "%Y-%m-%dT%H:%M:%SZ").date(),
        likes_amount="6",
        likes_from_users=[1,2],
    )
    session.add(state1)
    
    comment1 = m.Comment(
        text="cool",
        date=dt.strptime("2019-02-01T08:20:00Z", "%Y-%m-%dT%H:%M:%SZ").date(),
    )
    session.add(comment1)
    
    user1 = m.User(
        name="Ami",
        password="666666",
        email="mari@mail.ru",
    )
    session.add(user1)
    
    role1 = m.Role(name="читатель")
    session.add(role1)
    
    category1 = m.Category(name="Еда")
    session.add(category1)
    
    status1 = m.Status(name="Черновик")
    session.add(status1)
    
    
    session.commit()