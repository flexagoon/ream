"""Provides the "serialize" function to serialize a Telegram message."""

from typing import Any

from telethon.tl.types import (
    Message,
    MessageService,
    ReplyInlineMarkup,
)

from ._action import __serialize_action
from ._buttons import __serialize_buttons
from ._helpers import __format_time, __serialize_peer, __serialize_reply
from ._media import __serialize_media
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

        if forward := message.forward:
            if sender := forward.sender:
                data["forwarded_from"] = sender.first_name or sender.id
            elif chat := forward.chat:
                data["forwarded_from"] = chat.title or chat.id
            else:
                data["forwarded_from"] = forward.original_fwd.from_name

        if message.reply_to and hasattr(message.reply_to, "reply_to_msg_id"):
            data |= __serialize_reply(message)

        if message.via_bot_id:
            bot = await message.client.get_entity(message.via_bot_id)
            if bot.username:
                data["via_bot"] = f"@{bot.username}"

    data |= await __serialize_media(message)

    data["text"] = __serialize_text(message.entities, message.raw_text)
    data["text_entities"] = __serialize_text(
        message.entities,
        message.raw_text,
        serialize_entities=True,
    )

    if isinstance(message.reply_markup, ReplyInlineMarkup):
        data["inline_bot_buttons"] = __serialize_buttons(message.reply_markup.rows)

    return data
