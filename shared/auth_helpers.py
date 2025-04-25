from flask_jwt_extended import create_access_token


def get_auth_header(user_email):
    """Generate authorization header with JWT token for the given user email."""
    access_token = create_access_token(identity=user_email)
    return {"Authorization": f"Bearer {access_token}"}
