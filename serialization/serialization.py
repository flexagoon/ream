"""Provides the "serialize" function to serialize a Telegram message."""

from typing import Any

from telethon.tl.types import Message, MessageService  # type: ignore[import-untyped]

from ._action import __serialize_action
from ._helpers import __format_time, __serialize_peer, __serialize_reply
from ._text import __serialize_text


async def serialize(message: Message) -> dict[str, Any]:
    """Serialize a Telegram message into a json-like object.

    Parameters
    ----------
    message : Message
        The message to serialize.

    Returns
    -------
    dict[str, Any]
        The serialized message.

    """
    if not message.from_id:
        message.from_id = message.peer_id

    message_type = "service" if type(message) is MessageService else "message"

    date, date_unixtime = __format_time(message.date)

    data = {
        "id": message.id,
        "type": message_type,
        "date": date,
        "date_unixtime": date_unixtime,
    }

    if message.edit_date:
        edit_date, edit_date_unixtime = __format_time(message.edit_date)
        data["edited"] = edit_date
        data["edited_unixtime"] = edit_date_unixtime

    if message_type == "service":
        data |= await __serialize_action(message)
    else:
        data |= await __serialize_peer(message.client, message.from_id, "from")

        if forward := message.fwd_from:
            entity = forward.from_name or await message.client.get_entity(
                forward.from_id,
            )
            if hasattr(entity, "first_name"):
                data["forwarded_from"] = entity.first_name or entity.id
            else:
                data["forwarded_from"] = entity.title or entity.id

        if message.reply_to and hasattr(message.reply_to, "reply_to_msg_id"):
            data |= __serialize_reply(message)

        if message.via_bot_id:
            bot = await message.client.get_entity(message.via_bot_id)
            if bot.username:
                data["via_bot"] = bot.username

    data["text"] = __serialize_text(message.entities, message.raw_text)
    data["text_entities"] = __serialize_text(
        message.entities,
        message.raw_text,
        serialize_entities=True,
    )

    return data
