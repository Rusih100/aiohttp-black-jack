from aiohttp.abc import StreamResponse
from aiohttp.web_exceptions import HTTPUnauthorized


class AuthRequiredMixin:
    async def _iter(self) -> StreamResponse:
        if not getattr(self.request, "admin", None):
            raise HTTPUnauthorized(
                reason="Authentication is required to receive the requested response"
            )

        return await super(AuthRequiredMixin, self)._iter()
