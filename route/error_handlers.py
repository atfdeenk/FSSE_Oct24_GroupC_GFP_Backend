from flask import jsonify
from flask_jwt_extended.exceptions import NoAuthorizationError, ExpiredSignatureError
from flask_jwt_extended import JWTManager


def register_error_handlers(app: "Flask", jwt: JWTManager):
    @app.errorhandler(NoAuthorizationError)
    def handle_no_auth_error(e):
        return jsonify({"error": "Authorization token is missing"}), 401

    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_token_error(e):
        return jsonify({"error": "Authorization token has expired"}), 401

    @app.errorhandler(401)
    def handle_unauthorized(e):
        return jsonify({"error": "Unauthorized access"}), 401

    @app.errorhandler(422)
    def handle_unprocessable_entity(e):
        # This error can occur when the JWT is malformed
        return jsonify({"error": "Invalid authorization token"}), 422
