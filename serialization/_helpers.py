import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from telethon import TelegramClient
from telethon.hints import EntitiesLike, MessageLike
from telethon.tl.types import Message, PhotoSize

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


def __get_next_file_n(path: Path) -> int:
    n = 1
    for file in path.iterdir():
        try:
            file_n = int(file.stem.split("_")[1])
            n = max(n, file_n + 1)
        except (IndexError, ValueError):
            continue
    return n


async def __download_file(
    message: MessageLike,
    file: Path,
    *,
    thumb: PhotoSize | None = None,
    client: TelegramClient | None = None,
) -> str:
    dl_client = client or message.client
    if not file.exists():
        await dl_client.download_media(
            message,
            file,
            thumb=thumb,
            progress_callback=lambda current, total: log.info(
                "Downloading %s: %s/%s",
                file.name,
                current,
                total,
            ),
        )

    relative_path = Path(file.parent.name) / file.name

    return relative_path.as_posix()
