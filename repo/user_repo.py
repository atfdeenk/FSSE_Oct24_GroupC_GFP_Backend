from instance.database import db
from models.user import Users

def create_user(data):
    user = Users(**data)
    db.session.add(user)
    db.session.commit()
    return user

def get_user_by_email(email):
    return Users.query.filter_by(email=email).first()

def get_user_by_id(user_id):
    return Users.query.get(user_id)

def update_user(user, data):
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.session.commit()
    return user

def get_all_users():
    return Users.query.all()


def delete_user(user):
    db.session.delete(user)
    db.session.commit()
