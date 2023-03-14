from marshmallow import Schema, fields

from app.web.schemes import OkResponseSchema


class AdminSchema(Schema):
    id = fields.Int()
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

    class Meta:
        ordered = True


class AdminRequestSchema(AdminSchema):
    class Meta:
        fields = ("email", "password")


class AdminResponseSchema(OkResponseSchema):
    data = fields.Nested(AdminSchema(only=("id", "email")))
