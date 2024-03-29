from app.store import Store
from tests.utils import ok_response


class TestAdminLoginView:
    async def test_create_on_startup(self, store: Store, config):
        admin = await store.admins.get_by_email(config.admin.email)
        assert admin is not None
        assert admin.email == config.admin.email
        # Password must be hashed
        assert admin.password != config.admin.password
        assert admin.id == 1

    async def test_success(self, cli, config):
        resp = await cli.post(
            "/admin.login",
            json={
                "email": config.admin.email,
                "password": config.admin.password,
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data == ok_response(
            {
                "id": 1,
                "email": config.admin.email,
            }
        )
        assert resp.cookies.values()

        cookie = resp.cookies.get("AIOHTTP_SESSION")
        assert cookie
        assert cookie.value

    async def test_missed_email(self, cli):
        resp = await cli.post(
            "/admin.login",
            json={
                "password": "qwerty",
            },
        )
        assert resp.status == 400
        data = await resp.json()
        assert data["status"] == "bad_request"
        assert data["data"]["email"][0] == "Missing data for required field."

    async def test_not_valid_credentials(self, cli):
        resp = await cli.post(
            "/admin.login",
            json={
                "email": "qwerty",
                "password": "qwerty",
            },
        )
        assert resp.status == 403
        data = await resp.json()
        assert data["status"] == "forbidden"

    async def test_different_method(self, cli):
        resp = await cli.get(
            "/admin.login",
            json={
                "email": "qwerty",
                "password": "qwerty",
            },
        )
        assert resp.status == 405
        data = await resp.json()
        assert data["status"] == "not_implemented"


class TestAdminLogoutView:
    async def test_success(self, authed_cli, config):
        resp = await authed_cli.post("/admin.logout")

        assert resp.status == 200

        data = await resp.json()

        assert data == ok_response(
            {
                "id": 1,
                "email": config.admin.email,
            }
        )

        cookie = resp.cookies.get("AIOHTTP_SESSION")
        assert cookie
        assert not cookie.value

    async def test_unauthorized(self, cli):
        resp = await cli.get("/admin.logout")

        assert resp.status == 401

        data = await resp.json()

        assert data["status"] == "unauthorized"

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.get("/admin.logout")

        assert resp.status == 405

        data = await resp.json()

        assert data["status"] == "not_implemented"


class TestAdminCurrentView:
    async def test_success(self, authed_cli, config):
        resp = await authed_cli.get("/admin.current")

        assert resp.status == 200

        data = await resp.json()

        assert data == ok_response({"id": 1, "email": config.admin.email})

    async def test_unauthorized(self, cli):
        resp = await cli.get("/admin.current")

        assert resp.status == 401

        data = await resp.json()

        assert data["status"] == "unauthorized"

    async def test_different_method(self, authed_cli):
        resp = await authed_cli.post("/admin.current")

        assert resp.status == 405

        data = await resp.json()

        assert data["status"] == "not_implemented"
