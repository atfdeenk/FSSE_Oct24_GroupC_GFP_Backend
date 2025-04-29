from instance.database import db
from models.user import Users
from sqlalchemy import select
from models.user import RoleType
from decimal import Decimal

def create_user(data):
    user = Users(**data)
    db.session.add(user)
    db.session.commit()
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
    db.session.commit()
    return user

def get_all_users():
    # Use select() + scalars() for SQLAlchemy 2.0+
    stmt = select(Users)
    return db.session.execute(stmt).scalars().all()

def delete_user(user):
    db.session.delete(user)
    db.session.commit()

def get_users_by_role(role_value: str):
    stmt = select(Users).where(Users.role == RoleType(role_value))
    return db.session.execute(stmt).scalars().all()

def get_users_exclude_role(role_value: str):
    stmt = select(Users).where(Users.role != RoleType(role_value))
    return db.session.execute(stmt).scalars().all()

def update_user_balance(user_id: int, new_balance: Decimal) -> Users:
    user = db.session.get(Users, user_id)
    if not user:
        return None
    user.balance = new_balance
    db.session.commit()
    return user

