from flask_jwt_extended import create_access_token


def get_auth_header(user_id):
    """Generate authorization header with JWT token for the given user id."""
    access_token = create_access_token(identity=user_id)
    return {"Authorization": f"Bearer {access_token}"}
