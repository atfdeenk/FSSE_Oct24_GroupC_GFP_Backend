from instance.database import db
from models.user import Users
from sqlalchemy import select


def create_user(data):
    user = Users(**data)
    db.session.add(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return user


def get_user_by_email(email):
    # Uses select() + scalars() for modern query style
    stmt = select(Users).where(Users.email == email)
    return db.session.execute(stmt).scalars().first()


def get_user_by_id(user_id):
    return db.session.get(Users, user_id)  # ✅ new Session.get() style


def update_user(user, data):
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return user


def get_all_users():
    # Use select() + scalars() for SQLAlchemy 2.0+
    stmt = select(Users)
    return db.session.execute(stmt).scalars().all()


def delete_user(user):
    db.session.delete(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
