from marshmallow import Schema, fields

from app.web.schemes import OkResponseSchema


class StateSchema(Schema):
    state_id = fields.Int()
    game_id = fields.Int()
    players_count = fields.Int()
    join_players_count = fields.Int()
    bet_placed_players_count = fields.Int()
    finished_players_count = fields.Int()
    type = fields.Str()

    class Meta:
        ordered = True


class UserSchema(Schema):
    user_id = fields.Int()
    vk_id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    is_admin = fields.Bool()

    class Meta:
        ordered = True


class CardShema(Schema):
    type = fields.Str()
    type_name = fields.Str()
    suit = fields.Str()
    suit_name = fields.Str()
    value = fields.Int()

    class Meta:
        ordered = True


class PlayerSchema(Schema):
    player_id = fields.Int()
    game_id = fields.Int()
    user_id = fields.Int()
    cash = fields.Int()
    bet = fields.Int()
    is_bet_placed = fields.Bool()
    is_finished = fields.Bool()
    hand: fields.Nested(CardShema(many=True))
    user = fields.Nested(UserSchema())

    class Meta:
        ordered = True


class GameSchema(Schema):
    game_id = fields.Int()
    chat_id = fields.Int()
    state = fields.Nested(StateSchema())
    players = fields.Nested(PlayerSchema(many=True))

    class Meta:
        ordered = True


class GameGetResponseSchema(OkResponseSchema):
    data = fields.Nested(GameSchema())


class GameGetQuerySchema(Schema):
    chat_id = fields.Int(required=True)


class GameListSchema(Schema):
    games = fields.Nested(GameSchema(many=True, only=("game_id", "chat_id")))


class GameListResponseSchema(OkResponseSchema):
    data = fields.Nested(GameListSchema())