from app.store.vk_api.dataclasses import (
    Message,
    ObjectMessageNew,
    Update,
    UpdateMessage,
)


class TestHandleUpdates:
    async def test_no_messages(self, store):
        await store.bots_manager.handle_updates(updates=[])
        assert store.vk_api.send_message.called is False

    async def test_new_message(self, store):
        await store.bots_manager.handle_updates(
            updates=[
                Update(
                    type="message_new",
                    group_id=21,
                    object=ObjectMessageNew(
                        message=UpdateMessage(
                            id=1,
                            from_id=1,
                            peer_id=1,
                            text="kek",
                            payload=None,
                            date=11,
                            conversation_message_id=1,
                        )
                    ),
                )
            ]
        )
        assert store.vk_api.send_message.call_count == 1
        message: Message = store.vk_api.send_message.mock_calls[0].args[0]
        assert message.text
