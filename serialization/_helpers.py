import logging
from datetime import datetime
from typing import Any

from telethon import TelegramClient  # type: ignore[import-untyped]
from telethon.hints import EntitiesLike  # type: ignore[import-untyped]
from telethon.tl.types import Message  # type: ignore[import-untyped]

log = logging.getLogger(__name__)


def __format_time(time: datetime) -> tuple[str, str]:
    time = time.astimezone()
    return time.strftime("%Y-%m-%dT%H:%M:%S"), str(int(time.timestamp()))


async def __serialize_peer(
    client: TelegramClient,
    peer: EntitiesLike,
    prefix: str,
) -> dict[str, str | int]:
    entity = await client.get_entity(peer)
    return {
        prefix: " ".join(
            filter(
                None,
                [entity.first_name, entity.last_name],
            ),
        ),
        prefix + "_id": f"user{entity.id}",
    }


def __serialize_reply(
    message: Message,
    label: str = "reply_to_message_id",
) -> dict[str, Any]:
    data = {}
    reply = message.reply_to
    data[label] = reply.reply_to_msg_id
    if reply.reply_to_peer_id:
        data["reply_to_peer_id"] = reply.reply_to_peer_id
    return data
