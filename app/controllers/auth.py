from typing import Tuple
from http import HTTPStatus
from flask import jsonify, Response, request

from app.services.auth import AuthService
from app.common.messages import EMAIL_PASSWORD_REQUIRED
from app.common.exceptions import BadRequestException, DataAlreadyExists


class AuthController:
    def __init__(self, service: AuthService):
        self.service = service

    def login(self) -> Tuple[Response, int]:
        data = request.json
        if "email" not in data or "password" not in data:
            return (
                jsonify(
                    {
                        "message": EMAIL_PASSWORD_REQUIRED,
                        "error_code": HTTPStatus.BAD_REQUEST,
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        try:
            result = self.service.login(data)
            return jsonify(result), HTTPStatus.OK
        except BadRequestException as e:
            return jsonify(e.to_dict()), e.error_code

    def register(self) -> Tuple[Response, int]:
        try:
            data = request.json
            self.service.register(data)
            return "", HTTPStatus.CREATED
        except DataAlreadyExists as e:
            return jsonify(e.to_dict()), e.error_code

    def profile(self, current_user):
        return jsonify(current_user.to_dict()), HTTPStatus.OK
