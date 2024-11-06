"""Provides the "serialize" function to serialize a Telegram message."""

import asyncio
import logging
from pathlib import Path
from typing import Any

from telethon.errors import FloodWaitError
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

log = logging.getLogger(__name__)


async def serialize(message: Message, path: Path) -> dict[str, Any]:
    """Serialize a Telegram message into a json-like object.

    Parameters
    ----------
    message : Message
        The message to serialize.

    path : Path
        The directory that the export is saved to. This is used to store
        all the files and media.

    Returns
    -------
    dict[str, Any]
        The serialized message.

    """
    try:
        return await __try_serialize(message, path)
    except FloodWaitError as e:
        log.warning("Flood wait, waiting for: %s", e.seconds)
        await asyncio.sleep(e.seconds)
        return await serialize(message, path)


async def __try_serialize(message: Message, path: Path) -> dict[str, Any]:
    log.info("Serializing message %s", message.id)

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
                if sender.first_name:
                    data["forwarded_from"] = (
                        f"{sender.first_name} {sender.last_name}"
                        if sender.last_name
                        else sender.first_name
                    )
                elif sender.deleted:
                    data["forwarded_from"] = None
                else:
                    data["forwarded_from"] = sender.id
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

    data |= await __serialize_media(message, path)

    data["text"] = await __serialize_text(message, path)
    data["text_entities"] = await __serialize_text(
        message,
        path,
        serialize_entities=True,
    )

    if isinstance(message.reply_markup, ReplyInlineMarkup):
        data["inline_bot_buttons"] = __serialize_buttons(message.reply_markup.rows)

    return data
