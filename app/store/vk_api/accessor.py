import random
import typing
from typing import Any, List, Optional, Dict

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Keyboard, Message, Update, Profile
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.key: Optional[str] = None
        self.ts: Optional[int] = None
        self.server: Optional[str] = None

        self.session: Optional[ClientSession] = None
        self.poller: Optional[Poller] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))

        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)

        self.poller = Poller(app.store)
        self.logger.info("start polling")
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        query = self._build_query(
            host=API_PATH,
            method="groups.getLongPollServer",
            params={
                "group_id": self.app.config.bot.group_id,
                "access_token": self.app.config.bot.token,
            },
        )
        async with self.session.get(query) as response:
            data = (await response.json())["response"]

            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(self.server)

    async def _get_raw_updates(self) -> List[Any]:
        query = self._build_query(
            host=self.server,
            method="",
            params={
                "act": "a_check",
                "key": self.key,
                "ts": self.ts,
                "wait": 2,
            },
        )
        async with self.session.get(query) as response:
            data = await response.json()

            self.logger.info(data)
            self.ts = data["ts"]
            raw_updates = data.get("updates", [])

        return raw_updates

    async def poll(self):
        raw_updates = await self._get_raw_updates()
        updates = []

        for raw_update in raw_updates:
            update = Update.parse_update(raw_update)
            if update:
                updates.append(update)

        await self.app.store.bots_manager.handle_updates(updates=updates)

    async def send_message(
        self, message: Message, keyboard: Optional[Keyboard] = None
    ) -> None:
        params = {
            "peer_id": message.peer_id,
            "random_id": random.getrandbits(32),
            "message": message.text,
            "access_token": self.app.config.bot.token,
        }
        if keyboard:
            params["keyboard"] = keyboard.json

        query = self._build_query(API_PATH, "messages.send", params=params)

        async with self.session.get(query) as response:
            data = await response.json()
            self.logger.info(data)

    async def get_conversation_members(self, message: Message) -> List["Profile"]:
        query = self._build_query(
            host=API_PATH,
            method="messages.getConversationMembers",
            params={
                "peer_id": message.peer_id,
                "group_id": self.app.config.bot.group_id,
                "access_token": self.app.config.bot.token,
            },
        )
        async with self.session.get(query) as response:
            data = (await response.json())["response"]
            self.logger.info(data)

            raw_items = data["items"]
            raw_profiles = data["profiles"]

            profile_dict: Dict[str, "Profile"] = dict()

            for raw_profile in raw_profiles:
                _id = raw_profile["id"]

                profile_dict[_id] = Profile(
                    id=_id,
                    first_name=raw_profile["first_name"],
                    last_name=raw_profile["last_name"]
                )

            for raw_item in raw_items:
                member_id = raw_item["member_id"]

                profile = profile_dict.get(member_id, None)

                if profile is None:
                    continue

                profile.is_admin = raw_item.get("is_admin", False)
                profile_dict[member_id] = profile

        return list(profile_dict.values())
