import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from telethon import TelegramClient
from telethon.hints import EntitiesLike, MessageLike
from telethon.tl.types import Message, PeerChannel, PeerChat, PeerUser, PhotoSize

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
    if not message.reply_to:
        return {}
    data = {}
    reply = message.reply_to
    if hasattr(reply, "reply_to_msg_id"):
        data[label] = reply.reply_to_msg_id
    if hasattr(reply, "reply_to_peer_id") and (peer := reply.reply_to_peer_id):
        match peer:
            case PeerChannel():
                peer = f"channel{peer.channel_id}"
            case PeerChat():
                peer = f"chat{peer.chat_id}"
            case PeerUser():
                peer = f"user{peer.user_id}"
        data["reply_to_peer_id"] = peer
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
        content = await dl_client.download_media(
            message,
            file=bytes,
            thumb=thumb,
            progress_callback=lambda current, total: log.info(
                "Downloading %s: %s/%s",
                file.name,
                current,
                total,
            ),
        )
        # Telethon allows to download media directly to a file, but that way
        # the file would be created even before the media is fully downloaded,
        # so the download won't be resumed after an interruption.
        file.parent.mkdir(exist_ok=True, parents=True)
        file.write_bytes(content)

    relative_path = Path(file.parent.name) / file.name

    return relative_path.as_posix()
