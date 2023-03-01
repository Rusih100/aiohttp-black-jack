from aiohttp.web import HTTPForbidden
from aiohttp_apispec import docs, request_schema
from aiohttp_session import get_session, new_session

from app.admin.models import Admin
from app.admin.schemes import (
    AdminRequestSchema,
    AdminResponseSchema,
    AdminSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.schemes import ErrorResponseSchema
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(
        tags=["Admin"],
        summary="Administrator authorization",
        description="Authorization of the administrator. The method accepts the email and password fields as "
        "input and return information about the user along with the active session, if such a user exists "
        "in the service.",
        responses={
            200: {  # Успешно
                "description": "Ok",
                "schema": AdminResponseSchema,
            },
            400: {  # Непреобразуемая сущность
                "description": "Error: Bad request",
                "schema": ErrorResponseSchema,
            },
            403: {  # Некоректные данные
                "description": "Error: Forbidden",
                "schema": ErrorResponseSchema,
            },
            405: {  # Не реализовано
                "description": "Error: Not implemented",
                "schema": ErrorResponseSchema,
            },
        },
    )
    @request_schema(AdminRequestSchema)
    async def post(self):
        email = self.data["email"]
        password = self.data["password"]

        admin: Admin = await self.store.admins.get_by_email(email)

        if admin and admin.is_password_valid(password):
            session = await new_session(self.request)
            session["admin"] = {
                "id": admin.id,
                "email": admin.email,
            }

            return json_response(data=AdminSchema().dump(admin))

        raise HTTPForbidden(reason="Incorrect data")


class AdminLogoutView(AuthRequiredMixin, View):
    @docs(
        tags=["Admin"],
        summary="Administrator logout",
        description="A method that logs out of the system and closes the session for the administrator.",
        responses={
            200: {  # Успешно
                "description": "Ok",
                "schema": AdminResponseSchema,
            },
            401: {  # Неавторизован
                "description": "Error: Unauthorized",
                "schema": ErrorResponseSchema,
            },
            405: {  # Не реализовано
                "description": "Error: Not implemented",
                "schema": ErrorResponseSchema,
            },
        },
    )
    async def post(self):
        admin = self.request.admin
        self.request.admin = None

        session = await get_session(self.request)
        session.clear()

        return json_response(data=AdminSchema().dump(admin))


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(
        tags=["Admin"],
        summary="About yourself",
        description="Request information about yourself. Gives data about the administrator.",
        responses={
            200: {  # Успешно
                "description": "Ok",
                "schema": AdminResponseSchema,
            },
            401: {  # Неавторизован
                "description": "Error: Unauthorized",
                "schema": ErrorResponseSchema,
            },
            405: {  # Не реализовано
                "description": "Error: Not implemented",
                "schema": ErrorResponseSchema,
            },
        },
    )
    async def get(self):
        return json_response(data=AdminSchema().dump(self.request.admin))
